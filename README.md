# Find Sam — Round 3: Treasure Hunt

> **Project Rewind: Monaco GP Memory Collapse**

A real-time multiplayer mystery game built with **FastAPI**, **WebSockets**, and vanilla HTML/CSS/JS. Teams navigate a graph-based street circuit, solving riddles to find "Sam" before the memory timeline collapses.

---

## 🎮 Gameplay Overview

- A **Game Master (GM)** configures the game: sets the graph/map, places Sam, and defines puzzles at each node.
- **Teams** join via a lobby and are placed at starting positions on the circuit.
- Sam moves along a pre-defined or random path at a configurable interval.
- Teams navigate node-by-node, solve puzzles at each location to unlock movement, and try to reach Sam's node.
- First 3 teams to find Sam win!

---

## 🗂 Project Structure

```
find_sam_game/
├── main.py              # FastAPI app — routes, WebSocket handlers, startup logic
├── game.py              # Core game engine — graph, Sam movement, puzzle logic
├── custom_map.json      # Custom node layout mapping and configuration
├── game_state.json      # (auto-generated at runtime, not committed)
├── requirements.txt     # Python dependencies
├── graphify-out/        # Graphify knowledge graph outputs
├── templates/           # Jinja2 HTML templates
│   ├── index.html       # Team lobby / join page
│   ├── team.html        # Team game view
│   └── gm.html          # Game Master control panel
├── static/
│   ├── css/main.css     # Global styles
│   ├── js/              # Frontend JavaScript
│   └── assets/          # Images and other assets
└── tests/               # Unit tests
```

---

## 🚀 Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/sahana-des41/phase2-round3.git
cd phase2-round3
```

### 2. Create a virtual environment & install dependencies

```bash
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open in browser

| Role | URL |
|------|-----|
| Team Lobby | http://localhost:8000/ |
| Game Master | http://localhost:8000/gm |
| Team View | http://localhost:8000/team/{team_name} |

---

## 🌐 Live Deployment

The game is currently deployed and playable at:
**[https://phase2-round3.onrender.com/](https://phase2-round3.onrender.com/)**

### Deploying to Render
1. Create a new **Web Service** on Render and connect your GitHub repository.
2. Set the Environment to **Python**.
3. Use the following build and start commands:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. *(Optional but recommended)* Attach a **Persistent Disk** to your Render deployment and set the mount path (e.g., `/var/data`). If you do this, you'll need to modify the `db_file` path in `main.py` to point to the persistent disk so the game state survives server restarts.

---

## 🧪 Running Tests

```bash
pytest tests/
```

---

## 🛡️ Security & Anti-Cheat

To ensure fair play and prevent automated solvers (AI bots), the following security measures are implemented:
- **Rate Limiting:** API endpoints are protected by per-IP rate limiting (120 requests/minute).
- **Anti-AI Puzzle Timing:** Solves completed in under 5 seconds are flagged as suspicious and reported to the Game Master dashboard.
- **Input Sanitization:** Team names and user inputs are strictly validated and escaped (`escapeHTML`) to prevent XSS.
- **Obfuscated State:** Puzzle answers are never sent to player clients. Adjacent nodes are hidden for eliminated or winning teams.
- **Strict Progression:** Puzzles must be solved to advance; bypassing is not permitted.
- **CSP Headers:** Security headers (Content-Security-Policy, X-Frame-Options, etc.) are active.

---

## 🛠 Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11+, FastAPI |
| Real-time | WebSockets |
| Templating | Jinja2 |
| Frontend | Vanilla HTML, CSS, JavaScript |
| State | In-memory + JSON file persistence |
