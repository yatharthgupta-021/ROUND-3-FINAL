import os
import re
import time
import asyncio
import logging
from collections import defaultdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict, List, Set, Any
import secrets
from game import GameManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Find Sam - Multiplayer Mystery")

# ── Security: Per-IP rate limiting ─────────────────────────────────────────────
_ip_request_log: Dict[str, list] = defaultdict(list)
RATE_LIMIT_WINDOW = 60   # seconds
RATE_LIMIT_MAX = 120     # max requests per IP per window

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    # Prune old entries
    _ip_request_log[client_ip] = [
        t for t in _ip_request_log[client_ip] if now - t < RATE_LIMIT_WINDOW
    ]
    if len(_ip_request_log[client_ip]) >= RATE_LIMIT_MAX:
        return JSONResponse(
            {"detail": "Rate limit exceeded. Please slow down."},
            status_code=429
        )
    _ip_request_log[client_ip].append(now)
    response = await call_next(request)
    return response

# ── Security: CSP and hardening headers ────────────────────────────────────────
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' ws: wss:"
    )
    return response

# Ensure static and templates dirs exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize GameManager
db_file = "game_state.json"
game_manager = GameManager()
if os.path.exists(db_file):
    try:
        game_manager.load_state(db_file)
        logger.info("Loaded game state from file")
    except Exception as e:
        logger.error(f"Error loading state: {e}")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        # team_name -> WebSocket
        self.team_connections: Dict[str, WebSocket] = {}
        # List of GM WebSockets
        self.gm_connections: List[WebSocket] = []

    async def connect_team(self, team_name: str, websocket: WebSocket):
        await websocket.accept()
        self.team_connections[team_name] = websocket

    def disconnect_team(self, team_name: str):
        if team_name in self.team_connections:
            del self.team_connections[team_name]

    async def connect_gm(self, websocket: WebSocket):
        await websocket.accept()
        self.gm_connections.append(websocket)

    def disconnect_gm(self, websocket: WebSocket):
        if websocket in self.gm_connections:
            self.gm_connections.remove(websocket)

    async def broadcast_to_gm(self, data: Dict[str, Any]):
        for ws in self.gm_connections:
            try:
                await ws.send_json(data)
            except Exception:
                pass

    async def send_to_team(self, team_name: str, data: Dict[str, Any]):
        ws = self.team_connections.get(team_name)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                pass

    async def broadcast_to_all_teams(self, data: Dict[str, Any]):
        for ws in self.team_connections.values():
            try:
                await ws.send_json(data)
            except Exception:
                pass

manager = ConnectionManager()

# Background task for ticking Sam's movement
async def sam_tick_loop():
    while True:
        try:
            await asyncio.sleep(1)
            if game_manager.game_status == "active":
                moved = game_manager.tick_sam_movement()
                if moved:
                    game_manager.save_state(db_file)
                    # Broadcast updates
                    await update_all_clients()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in Sam tick loop: {e}")

@app.on_event("startup")
async def startup_event():
    # Start Sam's tick task
    app.state.sam_task = asyncio.create_task(sam_tick_loop())

@app.on_event("shutdown")
async def shutdown_event():
    app.state.sam_task.cancel()

async def update_all_clients():
    # Update GM
    gm_data = game_manager.get_gm_view_data(connected_teams=list(manager.team_connections.keys()))
    await manager.broadcast_to_gm({
        "type": "state_update",
        "data": gm_data
    })
    
    # Update Teams
    for team_name in list(game_manager.teams.keys()):
        team_data = game_manager.get_team_view_data(team_name)
        await manager.send_to_team(team_name, {
            "type": "state_update",
            "data": team_data
        })
        
    # Check global announcement condition
    # Winner announced if:
    # 1. At least 3 teams have found Sam
    # OR 2. There are registered teams, and all registered teams have finished/eliminated, and at least one team found Sam
    winners = game_manager.winners
    total_teams = len(game_manager.teams)
    finished_or_eliminated = sum(1 for t in game_manager.teams.values() if t["found_sam"] or t["is_eliminated"])
    
    if len(winners) >= 3 or (total_teams > 0 and finished_or_eliminated == total_teams and len(winners) > 0):
        # Broadcast winners announcement to everyone
        announcement = {
            "type": "winner_announcement",
            "winners": winners
        }
        await manager.broadcast_to_gm(announcement)
        await manager.broadcast_to_all_teams(announcement)

# Pydantic models for API
class ConfigureModel(BaseModel):
    diagonal_allowed: bool
    sam_static: bool
    sam_start_node: int
    sam_movement_interval: int
    sam_path: List[int]
    puzzles: List[Dict[str, Any]]
    node_names: Dict[str, str]

class MoveModel(BaseModel):
    team_name: str
    target_node: int

class SolveModel(BaseModel):
    team_name: str
    answer: str

class BypassModel(BaseModel):
    team_name: str

class StartTeamModel(BaseModel):
    team_name: str

class MapUpdateModel(BaseModel):
    nodes: List[Dict[str, Any]]
    connections: List[List[int]]

# HTML Routes
@app.get("/robots.txt", response_class=PlainTextResponse)
async def get_robots_txt():
    return PlainTextResponse("User-agent: *\nDisallow: /")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

security = HTTPBasic()
def verify_gm(credentials: HTTPBasicCredentials = Depends(security)):
    if not secrets.compare_digest(credentials.password, "ratikagr"):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/gm", response_class=HTMLResponse)
async def get_gm(request: Request, username: str = Depends(verify_gm)):
    return templates.TemplateResponse(request=request, name="gm.html")

@app.get("/team/{team_name}", response_class=HTMLResponse)
async def get_team(request: Request, team_name: str):
    if team_name not in game_manager.teams:
        return RedirectResponse(url="/?error=team_not_found")
    return templates.TemplateResponse(request=request, name="team.html", context={"team_name": team_name})

# HTTP API Endpoints
@app.get("/api/gm/state")
async def get_gm_state():
    return game_manager.get_gm_view_data(connected_teams=list(manager.team_connections.keys()))

@app.get("/api/team/state/{team_name}")
async def get_team_state(team_name: str):
    if team_name not in game_manager.teams:
        raise HTTPException(status_code=404, detail="Team not found")
    return game_manager.get_team_view_data(team_name)

@app.post("/api/join")
async def join_team(team_name: str = Form(...), start_node: int = Form(-1)):
    team_name = team_name.strip()
    if not team_name:
        return JSONResponse({"success": False, "message": "Invalid team name"}, status_code=400)

    # Input validation: restrict team name to safe characters, max 30 chars
    if len(team_name) > 30:
        return JSONResponse({"success": False, "message": "Team name too long (max 30 characters)"}, status_code=400)
    if not re.match(r'^[a-zA-Z0-9 _\-]+$', team_name):
        return JSONResponse({"success": False, "message": "Team name can only contain letters, numbers, spaces, hyphens, and underscores"}, status_code=400)

    allowed_teams = {
        "GoodSport", "Frustrated freshers", "Shabang", "Team VVinners", "Scythe", 
        "The Pro-Crastinators", "Gain eager", "Mohit K N", "PaneerTikka", "Momo", 
        "The classics", "Samarth", "Double trouble", "Triple trouble", "Wunderfools", 
        "Men of the match", "RadSinisterXypth", "We Love Pravalika", "The Clueless", 
        "NDND", "Sharath Raghavendra", "baksnan", "Kitty", "IMPOSTERS", "Team kanyarasi", 
        "Crazzzee", "Delulu", "404", "Namune"
    }
    allowed_teams_lower = {t.lower().strip() for t in allowed_teams}

    if team_name.lower().strip() not in allowed_teams_lower:
        return JSONResponse({"success": False, "message": "Unauthorized team name. Please use your registered team name."}, status_code=403)
    
    if game_manager.game_status == "ended":
        return JSONResponse({"success": False, "message": "Game has already ended"}, status_code=400)
        
    success = game_manager.add_team(team_name, start_node)
    if success:
        game_manager.save_state(db_file)
        await update_all_clients()
        return {"success": True, "team_name": team_name}
    else:
        return JSONResponse({"success": False, "message": "Team name already taken"}, status_code=400)

@app.post("/api/gm/configure")
async def configure_game(config: ConfigureModel):
    success = game_manager.configure_game(config.dict())
    if success:
        game_manager.save_state(db_file)
        await update_all_clients()
        return {"success": True}
    else:
        return JSONResponse({"success": False, "message": "Cannot configure game after setup"}, status_code=400)

@app.post("/api/gm/map/save")
async def save_map(map_data: MapUpdateModel):
    game_manager.update_map(map_data.nodes, map_data.connections)
    game_manager.save_state(db_file)
    await update_all_clients()
    return {"success": True}

@app.post("/api/gm/start")
async def start_game():
    if len(game_manager.teams) == 0:
        return JSONResponse({"success": False, "message": "At least one team must join first!"}, status_code=400)
    game_manager.start_game()
    game_manager.save_state(db_file)
    await update_all_clients()
    return {"success": True}

@app.post("/api/gm/pause")
async def pause_game():
    if game_manager.pause_game():
        game_manager.save_state(db_file)
        await update_all_clients()
        return {"success": True}
    return JSONResponse({"success": False, "message": "Game must be active to pause"}, status_code=400)

@app.post("/api/gm/resume")
async def resume_game():
    if game_manager.resume_game():
        game_manager.save_state(db_file)
        await update_all_clients()
        return {"success": True}
    return JSONResponse({"success": False, "message": "Game must be paused to resume"}, status_code=400)

@app.post("/api/team/move")
async def move_team(move: MoveModel):
    result = game_manager.move_team(move.team_name, move.target_node)
    if result["success"]:
        game_manager.save_state(db_file)
        await update_all_clients()
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.post("/api/team/solve")
async def solve_puzzle(solve: SolveModel):
    result = game_manager.solve_puzzle(solve.team_name, solve.answer)
    if result["success"]:
        game_manager.save_state(db_file)
        await update_all_clients()
        return result
    else:
        return JSONResponse(result, status_code=400)

@app.post("/api/team/bypass")
async def bypass_puzzle(bypass: BypassModel):
    result = game_manager.bypass_puzzle(bypass.team_name)
    return JSONResponse(result, status_code=403)

@app.post("/api/team/start")
async def start_team_mission(payload: StartTeamModel):
    success = game_manager.start_team(payload.team_name)
    if success:
        game_manager.save_state(db_file)
        await update_all_clients()
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Unable to start mission or team not found")

# WebSockets
@app.websocket("/ws/gm")
async def websocket_gm(websocket: WebSocket):
    await manager.connect_gm(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "state_update",
            "data": game_manager.get_gm_view_data(connected_teams=list(manager.team_connections.keys()))
        })
        while True:
            # GM websocket just holds connection, or handles manual Sam movement requests
            data = await websocket.receive_json()
            if data.get("action") == "move_sam_now" and game_manager.game_status == "active":
                # Manual trigger of Sam's next step
                game_manager.sam_path_index = (game_manager.sam_path_index + 1) % len(game_manager.sam_path)
                game_manager.sam_current_node = game_manager.sam_path[game_manager.sam_path_index]
                game_manager.last_sam_move_time = time.time()
                game_manager.update_puzzle_intel()
                
                # Check for collisions with Sam's new node
                for name, team in game_manager.teams.items():
                    if not team["is_eliminated"] and not team["found_sam"] and team["current_node"] == game_manager.sam_current_node:
                        game_manager.handle_team_win(name)
                
                game_manager.save_state(db_file)
                await update_all_clients()
    except WebSocketDisconnect:
        manager.disconnect_gm(websocket)
    except Exception as e:
        logger.error(f"WebSocket GM error: {e}")
        manager.disconnect_gm(websocket)

@app.websocket("/ws/team/{team_name}")
async def websocket_team(websocket: WebSocket, team_name: str):
    if team_name not in game_manager.teams:
        await websocket.close(code=4001)
        return
        
    await manager.connect_team(team_name, websocket)
    await update_all_clients()
    try:
        # Send initial state
        await websocket.send_json({
            "type": "state_update",
            "data": game_manager.get_team_view_data(team_name)
        })
        while True:
            # We don't expect messages from team client since we use HTTP POST for actions
            # to make integration straightforward and handle errors gracefully
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_team(team_name)
        await update_all_clients()
    except Exception as e:
        logger.error(f"WebSocket Team error: {e}")
        manager.disconnect_team(team_name)
        await update_all_clients()
