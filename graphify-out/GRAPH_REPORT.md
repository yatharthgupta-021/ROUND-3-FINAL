# Graph Report - phase2-round3  (2026-06-09)

## Corpus Check
- 11 files · ~25,402 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 175 nodes · 244 edges · 12 communities (10 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `30b81c52`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 10|Community 10]]

## God Nodes (most connected - your core abstractions)
1. `GameManager` - 35 edges
2. `update_all_clients()` - 15 edges
3. `ConnectionManager` - 10 edges
4. `TestFindSamGame` - 10 edges
5. `handleStateUpdate()` - 7 edges
6. `Find Sam — Round 3: Treasure Hunt` - 7 edges
7. `WebSocket` - 6 edges
8. `Any` - 5 edges
9. `websocket_gm()` - 5 edges
10. `websocket_team()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `BypassModel` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `ConfigureModel` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `ConnectionManager` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `MoveModel` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `Any` --uses--> `GameManager`  [INFERRED]
  main.py → game.py

## Import Cycles
- None detected.

## Communities (12 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (31): btnBypassPuzzle, btnCircuitMap, btnCloseIntel, btnCloseMapPopup, btnCloseRules, btnRules, btnStartMission, cluesList (+23 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (29): btnForceSamMove, btnResetGame, diagonalChk, enableConfigControls(), fetchState(), formatDuration(), getAdjacentNodes(), getNodeCoords() (+21 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (3): GameManager, Any, TestFindSamGame

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (21): BaseModel, bypass_puzzle(), BypassModel, configure_game(), ConfigureModel, get_gm(), get_index(), get_team() (+13 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (14): 1. Clone the repo, 2. Create a virtual environment & install dependencies, 3. Start the server, 4. Open in browser, Alternative: [Fly.io](https://fly.io), Alternative: [Railway](https://railway.app), Find Sam — Round 3: Treasure Hunt, ☁️ Free Deployment Options (+6 more)

### Community 5 - "Community 5"
Cohesion: 0.26
Nodes (5): ConnectionManager, Any, websocket_gm(), websocket_team(), WebSocket

### Community 6 - "Community 6"
Cohesion: 0.33
Nodes (6): fetchState(), getNodeCoords(), handleStateUpdate(), renderMap(), showWinnerOverlay(), updateTimerDisplay()

## Knowledge Gaps
- **61 isolated node(s):** `pathRecording`, `statusBadge`, `samCoordsBox`, `diagonalChk`, `samStaticChk` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameManager` connect `Community 2` to `Community 3`, `Community 5`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `ConnectionManager` connect `Community 5` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `GameManager` (e.g. with `BypassModel` and `ConfigureModel`) actually correct?**
  _`GameManager` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pathRecording`, `statusBadge`, `samCoordsBox` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05128205128205128 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07394957983193277 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._