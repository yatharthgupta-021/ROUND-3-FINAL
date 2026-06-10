# Graph Report - .  (2026-06-11)

## Corpus Check
- 20 files · ~174,044 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 186 nodes · 263 edges · 12 communities (11 shown, 1 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_GM Interface (JS)|GM Interface (JS)]]
- [[_COMMUNITY_Team Interface (JS)|Team Interface (JS)]]
- [[_COMMUNITY_Game Logic Engine|Game Logic Engine]]
- [[_COMMUNITY_FastAPI Main App|FastAPI Main App]]
- [[_COMMUNITY_Websocket Manager|Websocket Manager]]
- [[_COMMUNITY_Game Unit Tests|Game Unit Tests]]
- [[_COMMUNITY_Team State Methods|Team State Methods]]
- [[_COMMUNITY_Custom Map Data|Custom Map Data]]
- [[_COMMUNITY_Static Map Data|Static Map Data]]

## God Nodes (most connected - your core abstractions)
1. `GameManager` - 40 edges
2. `update_all_clients()` - 16 edges
3. `ConnectionManager` - 10 edges
4. `TestFindSamGame` - 10 edges
5. `handleStateUpdate()` - 7 edges
6. `Any` - 6 edges
7. `WebSocket` - 6 edges
8. `websocket_gm()` - 5 edges
9. `websocket_team()` - 5 edges
10. `handleStateUpdate()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `BypassModel` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `ConfigureModel` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `ConnectionManager` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `MapUpdateModel` --uses--> `GameManager`  [INFERRED]
  main.py → game.py
- `MoveModel` --uses--> `GameManager`  [INFERRED]
  main.py → game.py

## Import Cycles
- None detected.

## Communities (12 total, 1 thin omitted)

### Community 0 - "GM Interface (JS)"
Cohesion: 0.06
Nodes (34): btnForceSamMove, btnResetGame, btnSaveMap, chkMapEditor, currentConnections, currentNodes, customNodesCoords, diagonalChk (+26 more)

### Community 1 - "Team Interface (JS)"
Cohesion: 0.05
Nodes (33): btnBypassPuzzle, btnCircuitMap, btnCloseIntel, btnCloseMapPopup, btnCloseRules, btnCloseWin, btnRules, btnStartMission (+25 more)

### Community 2 - "Game Logic Engine"
Cohesion: 0.10
Nodes (6): GameManager, Any, Deprecated: map is now loaded from custom_map.json via load_custom_map()., Load nodes and connections from custom_map.json., Populate self.puzzles from the raw puzzle list loaded by load_custom_map., Update map structure in memory and save to custom_map.json.

### Community 3 - "FastAPI Main App"
Cohesion: 0.13
Nodes (23): BaseModel, bypass_puzzle(), BypassModel, configure_game(), ConfigureModel, get_gm(), get_index(), get_team() (+15 more)

### Community 4 - "Websocket Manager"
Cohesion: 0.26
Nodes (5): ConnectionManager, Any, websocket_gm(), websocket_team(), WebSocket

### Community 6 - "Team State Methods"
Cohesion: 0.33
Nodes (6): fetchState(), getNodeCoords(), handleStateUpdate(), renderMap(), showWinnerOverlay(), updateTimerDisplay()

### Community 7 - "Custom Map Data"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

### Community 8 - "Static Map Data"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

## Knowledge Gaps
- **63 isolated node(s):** `nodes`, `connections`, `puzzles`, `sam_start_node`, `nodes` (+58 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameManager` connect `Game Logic Engine` to `FastAPI Main App`, `Websocket Manager`, `Game Unit Tests`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Why does `TestFindSamGame` connect `Game Unit Tests` to `Game Logic Engine`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `ConnectionManager` connect `Websocket Manager` to `Game Logic Engine`, `FastAPI Main App`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GameManager` (e.g. with `BypassModel` and `ConfigureModel`) actually correct?**
  _`GameManager` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nodes`, `connections`, `puzzles` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `GM Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.059233449477351915 - nodes in this community are weakly interconnected._
- **Should `Team Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.04878048780487805 - nodes in this community are weakly interconnected._