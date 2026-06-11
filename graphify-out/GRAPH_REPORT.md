# Graph Report - phase2-round3  (2026-06-11)

## Corpus Check
- 14 files · ~173,601 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 251 nodes · 342 edges · 20 communities (17 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f4e8615`
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
- [[_COMMUNITY_Layout Tests|Layout Tests]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]

## God Nodes (most connected - your core abstractions)
1. `GameManager` - 50 edges
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

## Communities (20 total, 3 thin omitted)

### Community 0 - "GM Interface (JS)"
Cohesion: 0.06
Nodes (34): btnForceSamMove, btnResetGame, btnSaveMap, chkMapEditor, currentConnections, currentNodes, customNodesCoords, diagonalChk (+26 more)

### Community 1 - "Team Interface (JS)"
Cohesion: 0.05
Nodes (39): btnBypassPuzzle, btnCircuitMap, btnCloseIntel, btnCloseMapPopup, btnCloseRules, btnCloseWin, btnRules, btnStartMission (+31 more)

### Community 2 - "Game Logic Engine"
Cohesion: 0.13
Nodes (4): GameManager, Any, Deprecated: map is now loaded from custom_map.json via load_custom_map()., Bypass is explicitly disabled — teams must solve puzzles.

### Community 3 - "FastAPI Main App"
Cohesion: 0.13
Nodes (25): BaseModel, bypass_puzzle(), BypassModel, configure_game(), ConfigureModel, get_gm(), get_index(), get_team() (+17 more)

### Community 4 - "Websocket Manager"
Cohesion: 0.26
Nodes (5): ConnectionManager, Any, websocket_gm(), websocket_team(), WebSocket

### Community 6 - "Team State Methods"
Cohesion: 0.12
Nodes (15): 1. Clone the repo, 2. Create a virtual environment & install dependencies, 3. Start the server, 4. Open in browser, Alternative: [Fly.io](https://fly.io), Alternative: [Railway](https://railway.app), Find Sam — Round 3: Treasure Hunt, ☁️ Free Deployment Options (+7 more)

### Community 7 - "Custom Map Data"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

### Community 8 - "Static Map Data"
Cohesion: 0.40
Nodes (4): connections, nodes, puzzles, sam_start_node

### Community 11 - "Layout Tests"
Cohesion: 0.18
Nodes (6): target_node must be an integer, not a string., Negative node IDs don't exist in the graph., Node IDs beyond the graph should be rejected., Answers longer than 200 chars should be rejected., Answer must be a string., TestInputValidation

### Community 12 - "Community 12"
Cohesion: 0.22
Nodes (5): _add_test_puzzles(), Solving a puzzle after 10+ seconds should NOT be flagged., Add test puzzles to the game since custom_map.json may have none., Solving a puzzle in under 5 seconds should create a suspicious flag., TestAntiAIPuzzleTiming

### Community 13 - "Community 13"
Cohesion: 0.25
Nodes (4): Eliminated teams should not see adjacent nodes., Teams that found Sam should not see adjacent nodes., Active teams should see adjacent nodes., TestAdjacentNodeHiding

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (3): Security-focused unit tests for Find Sam game., bypass_puzzle should always return failure., TestBypassDisabled

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (3): Load nodes and connections from custom_map.json., Populate self.puzzles from the raw puzzle list loaded by load_custom_map., Update map structure in memory and save to custom_map.json.

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (3): GM view should include suspicious_flags for each team., GM view should include solve_times for each team., TestSuspiciousFlagsInGMView

## Knowledge Gaps
- **77 isolated node(s):** `nodes`, `connections`, `puzzles`, `sam_start_node`, `nodes` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameManager` connect `Game Logic Engine` to `FastAPI Main App`, `Websocket Manager`, `Game Unit Tests`, `Layout Tests`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`?**
  _High betweenness centrality (0.197) - this node is a cross-community bridge._
- **Why does `TestInputValidation` connect `Layout Tests` to `Game Logic Engine`, `Community 12`, `Community 14`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `TestFindSamGame` connect `Game Unit Tests` to `Game Logic Engine`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `GameManager` (e.g. with `BypassModel` and `ConfigureModel`) actually correct?**
  _`GameManager` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nodes`, `connections`, `puzzles` to the rest of the system?**
  _97 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `GM Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.05758582502768549 - nodes in this community are weakly interconnected._
- **Should `Team Interface (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.04609929078014184 - nodes in this community are weakly interconnected._