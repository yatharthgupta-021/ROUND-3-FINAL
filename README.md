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
├── game_state.json      # (auto-generated at runtime, not committed)
├── requirements.txt     # Python dependencies
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

## ☁️ Free Deployment Options

This app uses **FastAPI + WebSockets** and requires a live Python server — it **cannot** be hosted on GitHub Pages (static only). Here are the best free options:

### ✅ Recommended: [Render](https://render.com)

1. Create a free account at [render.com](https://render.com)
2. Click **New → Web Service** → connect your GitHub repo
3. Set:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy — Render gives you a free `*.onrender.com` URL

> ⚠️ Free Render instances spin down after 15 min of inactivity. For a live game event, upgrade to the $7/mo paid tier or keep the instance warm.

### Alternative: [Railway](https://railway.app)

1. Sign up at [railway.app](https://railway.app)
2. Click **New Project → Deploy from GitHub Repo**
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Railway gives $5 free credit/month (enough for ~500 hours)

### Alternative: [Fly.io](https://fly.io)

For more control, deploy with Docker:
```bash
# Install flyctl, then:
fly launch
fly deploy
```
Fly.io offers 3 free VMs with 256MB RAM.

---

## 🧪 Running Tests

```bash
pytest tests/
```

---

## 🛠 Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11+, FastAPI |
| Real-time | WebSockets |
| Templating | Jinja2 |
| Frontend | Vanilla HTML, CSS, JavaScript |
| State | In-memory + JSON file persistence |
