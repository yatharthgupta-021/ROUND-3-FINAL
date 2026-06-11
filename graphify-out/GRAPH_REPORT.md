# Graph Report - .  (2026-06-11)

## Corpus Check
- 19 files · ~404,818 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 245 nodes · 314 edges · 16 communities (13 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
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
- [[_COMMUNITY_Graph Tests|Graph Tests]]
- [[_COMMUNITY_Serpentine Tests|Serpentine Tests]]
- [[_COMMUNITY_Layout Tests|Layout Tests]]
- [[_COMMUNITY_Community 12|Community 12]]

## God Nodes (most connected - your core abstractions)
1. `GameManager` - 32 edges
2. `update_all_clients()` - 15 edges
3. `ConnectionManager` - 9 edges
4. `TestFindSamGame` - 9 edges
5. `Find Sam — Round 3: Treasure Hunt` - 8 edges
6. `Any` - 7 edges
7. `handleStateUpdate()` - 7 edges
8. `TestInputValidation` - 7 edges
9. `_add_test_puzzles()` - 6 edges
10. `Request` - 5 edges

## Surprising Connections (you probably didn't know these)
- `reset_game()` --calls--> `GameManager`  [EXTRACTED]
  main.py → game.py

## Import Cycles
- None detected.

## Communities (16 total, 3 thin omitted)

### Community 0 - "GM Interface (JS)"
Cohesion: 0.05
Nodes (36): btnBypassPuzzle, btnCloseIntel, btnCloseRules, btnCloseWin, btnRules, btnStartMission, cluesList, fetchState() (+28 more)

### Community 1 - "Team Interface (JS)"
Cohesion: 0.06
Nodes (34): btnForceSamMove, btnResetGame, btnSaveMap, chkMapEditor, currentConnections, currentNodes, customNodesCoords, diagonalChk (+26 more)

### Community 2 - "Game Logic Engine"
Cohesion: 0.10
Nodes (7): Any, GameManager, Deprecated: map is now loaded from custom_map.json via load_custom_map()., Load nodes and connections from custom_map.json., Populate self.puzzles from the raw puzzle list loaded by load_custom_map., Bypass is explicitly disabled — teams must solve puzzles., Update map structure in memory and save to custom_map.json.

### Community 3 - "FastAPI Main App"
Cohesion: 0.07
Nodes (17): _add_test_puzzles(), Security-focused unit tests for Find Sam game., Solving a puzzle after 10+ seconds should NOT be flagged., GM view should include suspicious_flags for each team., GM view should include solve_times for each team., target_node must be an integer, not a string., Negative node IDs don't exist in the graph., Node IDs beyond the graph should be rejected. (+9 more)

### Community 4 - "Websocket Manager"
Cohesion: 0.12
Nodes (25): BaseModel, bypass_puzzle(), BypassModel, configure_game(), ConfigureModel, get_gm(), get_index(), get_team() (+17 more)

### Community 5 - "Game Unit Tests"
Cohesion: 0.26
Nodes (5): Any, ConnectionManager, websocket_gm(), websocket_team(), WebSocket

### Community 6 - "Team State Methods"
Cohesion: 0.15
Nodes (12): 1. Clone the repo, 2. Create a virtual environment & install dependencies, 3. Start the server, 4. Open in browser, Find Sam — Round 3: Treasure Hunt, 🎮 Gameplay Overview, 🌐 Live Deployment, 🗂 Project Structure (+4 more)

### Community 8 - "Static Map Data"
Cohesion: 0.25
Nodes (4): Eliminated teams should not see adjacent nodes., Teams that found Sam should not see adjacent nodes., Active teams should see adjacent nodes., TestAdjacentNodeHiding

### Community 9 - "Graph Tests"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

### Community 10 - "Serpentine Tests"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

## Knowledge Gaps
- **72 isolated node(s):** `graphify`, `Workflow: graphify`, `nodes`, `connections`, `puzzles` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameManager` connect `Game Logic Engine` to `Static Map Data`, `FastAPI Main App`, `Websocket Manager`, `Custom Map Data`?**
  _High betweenness centrality (0.198) - this node is a cross-community bridge._
- **Why does `reset_game()` connect `Websocket Manager` to `Game Logic Engine`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **What connects `graphify`, `Workflow: graphify`, `nodes` to the rest of the system?**
  _92 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `GM Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.049494949494949494 - nodes in this community are weakly interconnected._
- **Should `Team Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.05758582502768549 - nodes in this community are weakly interconnected._
- **Should `Game Logic Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.0967741935483871 - nodes in this community are weakly interconnected._
- **Should `FastAPI Main App` be split into smaller, more focused modules?**
  _Cohesion score 0.06854838709677419 - nodes in this community are weakly interconnected._