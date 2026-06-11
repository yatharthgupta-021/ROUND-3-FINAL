# Graph Report - phase2-round3  (2026-06-12)

## Corpus Check
- 14 files · ~405,825 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 249 nodes · 339 edges · 19 communities (15 shown, 4 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eb231092`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

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
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]

## God Nodes (most connected - your core abstractions)
1. `GameManager` - 51 edges
2. `update_all_clients()` - 16 edges
3. `ConnectionManager` - 10 edges
4. `TestFindSamGame` - 10 edges
5. `TestInputValidation` - 8 edges
6. `Find Sam — Round 3: Treasure Hunt` - 8 edges
7. `Any` - 7 edges
8. `handleStateUpdate()` - 7 edges
9. `Request` - 6 edges
10. `WebSocket` - 6 edges

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

## Communities (19 total, 4 thin omitted)

### Community 0 - "GM Interface (JS)"
Cohesion: 0.05
Nodes (36): btnBypassPuzzle, btnCloseIntel, btnCloseRules, btnCloseWin, btnRules, btnStartMission, cluesList, fetchState() (+28 more)

### Community 1 - "Team Interface (JS)"
Cohesion: 0.06
Nodes (35): btnForceSamMove, btnPauseGame, btnResumeGame, btnSaveMap, chkMapEditor, currentConnections, currentNodes, customNodesCoords (+27 more)

### Community 2 - "Game Logic Engine"
Cohesion: 0.11
Nodes (4): GameManager, Any, Deprecated: map is now loaded from custom_map.json via load_custom_map()., Bypass is explicitly disabled — teams must solve puzzles.

### Community 3 - "FastAPI Main App"
Cohesion: 0.18
Nodes (6): target_node must be an integer, not a string., Negative node IDs don't exist in the graph., Node IDs beyond the graph should be rejected., Answers longer than 200 chars should be rejected., Answer must be a string., TestInputValidation

### Community 4 - "Websocket Manager"
Cohesion: 0.09
Nodes (31): BaseModel, bypass_puzzle(), BypassModel, configure_game(), ConfigureModel, ConnectionManager, get_gm(), get_index() (+23 more)

### Community 5 - "Game Unit Tests"
Cohesion: 0.18
Nodes (6): _add_test_puzzles(), Security-focused unit tests for Find Sam game., GM view should include suspicious_flags for each team., GM view should include solve_times for each team., Add test puzzles to the game since custom_map.json may have none., TestSuspiciousFlagsInGMView

### Community 6 - "Team State Methods"
Cohesion: 0.15
Nodes (12): 1. Clone the repo, 2. Create a virtual environment & install dependencies, 3. Start the server, 4. Open in browser, Find Sam — Round 3: Treasure Hunt, 🎮 Gameplay Overview, 🌐 Live Deployment, 🗂 Project Structure (+4 more)

### Community 8 - "Static Map Data"
Cohesion: 0.25
Nodes (4): Eliminated teams should not see adjacent nodes., Teams that found Sam should not see adjacent nodes., Active teams should see adjacent nodes., TestAdjacentNodeHiding

### Community 9 - "Graph Tests"
Cohesion: 0.33
Nodes (3): Load nodes and connections from custom_map.json., Populate self.puzzles from the raw puzzle list loaded by load_custom_map., Update map structure in memory and save to custom_map.json.

### Community 10 - "Serpentine Tests"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (3): Solving a puzzle after 10+ seconds should NOT be flagged., Solving a puzzle in under 5 seconds should create a suspicious flag., TestAntiAIPuzzleTiming

### Community 17 - "Community 17"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

## Knowledge Gaps
- **73 isolated node(s):** `nodes`, `connections`, `puzzles`, `sam_start_node`, `nodes` (+68 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameManager` connect `Game Logic Engine` to `FastAPI Main App`, `Websocket Manager`, `Game Unit Tests`, `Custom Map Data`, `Static Map Data`, `Graph Tests`, `Community 16`, `Community 18`?**
  _High betweenness centrality (0.211) - this node is a cross-community bridge._
- **Why does `TestInputValidation` connect `FastAPI Main App` to `Game Logic Engine`, `Game Unit Tests`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `TestFindSamGame` connect `Custom Map Data` to `Game Logic Engine`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `GameManager` (e.g. with `BypassModel` and `ConfigureModel`) actually correct?**
  _`GameManager` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nodes`, `connections`, `puzzles` to the rest of the system?**
  _93 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `GM Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.049494949494949494 - nodes in this community are weakly interconnected._
- **Should `Team Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.056025369978858354 - nodes in this community are weakly interconnected._