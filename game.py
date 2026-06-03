import time
import random
import json
from typing import Dict, List, Set, Any, Optional

class GameManager:
    def __init__(self):
        self.game_status = "setup"  # "setup", "active", "ended"
        self.diagonal_allowed = False
        self.sam_static = True
        self.sam_movement_interval = 90
        self.last_sam_move_time = 0.0
        self.start_time = 0.0  # Game start timestamp
        
        # 80 Nodes: Monaco Street Circuit + School Corridor Spurs (10x12 Grid)
        self.nodes: Dict[int, Dict[str, Any]] = {}
        self.adj_list: Dict[int, List[int]] = {}
        self.setup_monaco_map()
        
        # Sam Hiding Node (Default: Node 53 - School Clinic Bed)
        self.sam_start_node = 53
        self.sam_path: List[int] = [53]
        self.sam_path_index = 0
        self.sam_current_node = 53
        
        # Teams State
        self.teams: Dict[str, Dict[str, Any]] = {}
        
        # Puzzles and Intel Clues (Storyline Puzzles)
        self.puzzles: Dict[int, Dict[str, str]] = {}
        self.setup_story_puzzles()
        
        # Winners tracking
        self.winners: List[Dict[str, Any]] = []

    def setup_monaco_map(self):
        # 80 Nodes layout definition on a 10x12 grid (x: 0..9, y: 0..11)
        node_defs = [
            # Row 0: y=0 (x: 0..7)
            (0, "Start", 0, 0),
            (1, "Pit Exit", 1, 0),
            (2, "Hill Class", 2, 0),
            (3, "Blackboard", 3, 0),
            (4, "Casino", 4, 0),
            (5, "Library", 5, 0),
            (6, "Playground", 6, 0),
            (7, "Lab", 7, 0),
            
            # Row 1: y=1 (x: 7..1, reversed)
            (8, "Math", 7, 1),
            (9, "Cafeteria", 6, 1),
            (10, "Tunnel In", 5, 1),
            (11, "Tunnel Mid", 4, 1),
            (12, "Tunnel Out", 3, 1),
            (13, "Yard", 2, 1),
            (14, "Harbor", 1, 1),
            
            # Row 2: y=2 (x: 1..7)
            (15, "Pool Entry", 1, 2),
            (16, "Pool Apex", 2, 2),
            (17, "Pool Exit", 3, 2),
            (18, "Rascasse In", 4, 2),
            (19, "Wall", 5, 2),
            (20, "Rascasse", 6, 2),
            (21, "Noghes", 7, 2),
            
            # Row 3: y=3 (x: 7..1, reversed)
            (22, "Pit Entry", 7, 3),
            (23, "Straight", 6, 3),
            (24, "Podium", 5, 3),
            (25, "Garages", 4, 3),
            (26, "Paddock", 3, 3),
            (27, "Yacht Club", 2, 3),
            (28, "Boardwalk", 1, 3),
            
            # Row 4: y=4 (x: 1..7)
            (29, "Run-off", 1, 4),
            (30, "Sandbox", 2, 4),
            (31, "Corridor", 3, 4),
            (32, "Class", 4, 4),
            (33, "Library Rm", 5, 4),
            (34, "Playground Rm", 6, 4),
            (35, "Lab Spur", 7, 4),
            
            # Row 5: y=5 (x: 7..1, reversed)
            (36, "Math Sec", 7, 5),
            (37, "Cafe Table", 6, 5),
            (38, "Swing", 5, 5),
            (39, "Chem Bench", 4, 5),
            (40, "Computer", 3, 5),
            (41, "Playroom", 2, 5),
            (42, "Podium", 1, 5),
            
            # Row 6: y=6 (x: 1..9)
            (43, "Piano", 1, 6),
            (44, "Art", 2, 6),
            (45, "Backstage", 3, 6),
            (46, "Lockers", 4, 6),
            (47, "Globe", 5, 6),
            (48, "Headset", 6, 6),
            (49, "Bookshelf", 7, 6),
            (50, "Principal", 8, 6),
            (51, "Couch", 9, 6),
            
            # Row 7: y=7 (x: 9..1, reversed)
            (52, "Armchair", 9, 7),
            (53, "Clinic", 8, 7),
            (54, "Detention", 7, 7),
            (55, "Locker Spur", 6, 7),
            (56, "Equipment", 5, 7),
            (57, "Greenhouse", 4, 7),
            (58, "Physics", 3, 7),
            (59, "Gym", 2, 7),
            (60, "Track", 1, 7),
            
            # Column 0: x=0, y=7..1 (going up)
            (61, "Gate", 0, 7),
            (62, "Swings", 0, 6),
            (63, "Slides", 0, 5),
            (64, "Grandstand", 0, 4),
            (65, "Marshal 2", 0, 3),
            (66, "Marshal 3", 0, 2),
            (67, "Marshal 4", 0, 1),
            
            # Spur: Columns 8 and 9, Rows 0 to 5
            (68, "Chapel", 8, 3),
            (69, "Monument", 8, 4),
            (70, "Cafe", 8, 5),
            (71, "Restaurant", 9, 5),
            (72, "Fountain", 9, 4),
            (73, "Hotel", 9, 3),
            (74, "Garden", 9, 2),
            (75, "Breeze Walk", 8, 2),
            (76, "Ventilation", 8, 1),
            (77, "Chicane", 9, 1),
            (78, "Yacht", 9, 0),
            (79, "Cafe Bar", 8, 0)
        ]
        
        for nid, name, x, y in node_defs:
            self.nodes[nid] = {
                "id": nid,
                "name": name,
                "x": x,
                "y": y
            }
            
        # Define graph connections (loops + spurs)
        connections = []
        # Main track serpentine loop (0 to 67)
        for i in range(67):
            connections.append((i, i + 1))
        connections.append((67, 0))  # Vertically closes loop along x=0
        
        # Spur nodes (68 to 79)
        connections.append((22, 68))  # Branch off main track at loop node 22 (7,3)
        for i in range(68, 79):
            connections.append((i, i + 1))
            
        # Custom user requested connections
        connections.append((79, 8))
        connections.append((70, 35))
            
        # Adjacency list
        self.adj_list = {i: [] for i in range(80)}
        for u, v in connections:
            self.adj_list[u].append(v)
            self.adj_list[v].append(u)

    def get_adjacent_nodes(self, node_id: int) -> List[int]:
        if node_id not in self.nodes:
            return []
            
        adjacent = list(self.adj_list.get(node_id, []))
        
        # Diagonal shortcut logic if allowed by GM
        if self.diagonal_allowed:
            curr = self.nodes[node_id]
            diagonals = []
            for nid, node in self.nodes.items():
                if abs(node["x"] - curr["x"]) == 1 and abs(node["y"] - curr["y"]) == 1:
                    diagonals.append(nid)
            adjacent.extend(diagonals)
            
        return sorted(list(set(adjacent)))

    def get_shortest_path_distance(self, start_node: int, target_node: int) -> int:
        if start_node == target_node:
            return 0
            
        visited = {start_node}
        queue = [(start_node, 0)]
        
        while queue:
            curr, dist = queue.pop(0)
            if curr == target_node:
                return dist
                
            for neighbor in self.get_adjacent_nodes(curr):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
                    
        return 999  # Unreachable

    def setup_story_puzzles(self):
        # 20 storyline-specific puzzles: focused on school days, childhood memories, cartoons, and memory restoration
        story_riddles = [
            {
                "node": 5,
                "q": "Casino Square Library: In school, you read a classic book about a boy wizard who attends Hogwarts. What is his last name?",
                "a": "potter"
            },
            {
                "node": 10,
                "q": "Sainte Devote Sandbox: During recess, children build sandcastles. What is the standard geometric shape of a sandbox with four equal sides and 90-degree angles?",
                "a": "square"
            },
            {
                "node": 15,
                "q": "Beau Rivage S-Bends: A memory fragment shows children playing hopscotch. If you jump on 3 squares, then 2, then 4, how many total squares did you land on?",
                "a": "9"
            },
            {
                "node": 20,
                "q": "Science Lab: Water has 2 hydrogen atoms and 1 oxygen atom. Write its chemical formula.",
                "a": "h2o"
            },
            {
                "node": 25,
                "q": "Tunnel Entry: A voice echoes: 'I tawt I taw a puddy tat!' What yellow cartoon canary says this?",
                "a": "tweety"
            },
            {
                "node": 30,
                "q": "Math Classroom: Solve: 15 multiplied by 4, plus 20.",
                "a": "80"
            },
            {
                "node": 35,
                "q": "Principal's Office: A rule is written: 'No running in the corridors.' What is the opposite of 'running'?",
                "a": "walking"
            },
            {
                "node": 40,
                "q": "Computer Room: What 3-letter abbreviation stands for the central processing unit of a computer?",
                "a": "cpu"
            },
            {
                "node": 45,
                "q": "Music Room: What musical instrument has 88 keys and black and white notes?",
                "a": "piano"
            },
            {
                "node": 50,
                "q": "Art Studio: Mixing the primary colors Blue and Yellow produces what color?",
                "a": "green"
            },
            {
                "node": 53,
                "q": "School Clinic: The clinic clock is ticking. What 5-letter word describes the mental ability to store and recall information?",
                "a": "memory"
            },
            {
                "node": 55,
                "q": "Locker Corridor: Each locker has a number. If your locker number is the sum of 45 and 55, what is it?",
                "a": "100"
            },
            {
                "node": 57,
                "q": "Biology Greenhouse: What green pigment in leaves allows plants to absorb light for photosynthesis?",
                "a": "chlorophyll"
            },
            {
                "node": 60,
                "q": "Gymnasium: What sport involves shooting a ball through a high hoop with a net?",
                "a": "basketball"
            },
            {
                "node": 62,
                "q": "Detention Room: The teacher writes a word scrambler: 'Y S T R O I H'. Unscramble this school subject.",
                "a": "history"
            },
            {
                "node": 65,
                "q": "Geography Lab: A large globe spins in the corner. What is the name of the largest ocean on Earth?",
                "a": "pacific"
            },
            {
                "node": 70,
                "q": "Recess Playgrounds: A cartoon mouse named Jerry is always escaping from a cat named...?",
                "a": "tom"
            },
            {
                "node": 72,
                "q": "English Lit Corner: A quote from a play: 'To be, or not to be.' What famous English playwright wrote this?",
                "a": "shakespeare"
            },
            {
                "node": 75,
                "q": "Detention blackboard: Write the name of Sam's memory stabilization machine. (Two words)",
                "a": "project rewind"
            },
            {
                "node": 78,
                "q": "Recess Swings: Children play a game with white and black pieces where the goal is to trap the opponent's king. What is the game?",
                "a": "chess"
            }
        ]
        
        for riddle in story_riddles:
            node_id = riddle["node"]
            self.puzzles[node_id] = {
                "question": riddle["q"],
                "answer": riddle["a"],
                "intel": ""
            }

    def add_team(self, team_name: str, start_node: int = -1) -> bool:
        if self.game_status != "setup":
            return False
        if team_name in self.teams:
            return False
            
        # Determine starting node such that the shortest path distance to Sam (default 53) is AT LEAST 25 steps
        sam_node = self.sam_current_node
        possible_starts = []
        for nid in range(80):
            dist = self.get_shortest_path_distance(nid, sam_node)
            is_occupied = any(t["current_node"] == nid for t in self.teams.values())
            # Enforce distance >= 25 and avoid start overlap if possible
            if dist >= 25 and not is_occupied:
                possible_starts.append(nid)
                
        if not possible_starts:
            # Fallback: choose any node with maximum distance >= 20
            possible_starts = [nid for nid in range(80) if self.get_shortest_path_distance(nid, sam_node) >= 20]
            
        if not possible_starts:
            possible_starts = [0]
            
        assigned_node = random.choice(possible_starts)
        
        self.teams[team_name] = {
            "tickets": 50,
            "current_node": assigned_node,
            "history": [assigned_node],
            "clues_received": [],
            "puzzles_solved": [],
            "join_time": time.time(),
            "finish_time": 0.0,
            "is_eliminated": False,
            "found_sam": False,
            "moves_since_last_intel": 0,
            "active_puzzle_node": None
        }
        
        # Provide starting location info
        self.teams[team_name]["clues_received"].append({
            "type": "system",
            "text": f"📍 Project Rewind Deployed: Landed at '{self.nodes[assigned_node]['name']}' (Node {assigned_node}). Security Clearance Level 0/3.",
            "timestamp": time.time()
        })
        return True

    def remove_team(self, team_name: str):
        if team_name in self.teams:
            del self.teams[team_name]

    def start_game(self):
        if self.game_status == "setup":
            self.game_status = "active"
            self.start_time = time.time()
            self.last_sam_move_time = time.time()
            
            # Reset teams join/start timers
            start_time = time.time()
            for team in self.teams.values():
                team["join_time"] = start_time
                team["tickets"] = 50
                team["is_eliminated"] = False
                team["found_sam"] = False
                team["moves_since_last_intel"] = 0
            
            self.sam_current_node = self.sam_start_node

    def handle_team_win(self, team_name: str):
        team = self.teams.get(team_name)
        if team and not team["found_sam"] and not team["is_eliminated"]:
            team["found_sam"] = True
            team["finish_time"] = time.time()
            duration = team["finish_time"] - self.start_time
            
            if not any(w["team_name"] == team_name for w in self.winners):
                self.winners.append({
                    "team_name": team_name,
                    "duration_seconds": round(duration, 2),
                    "tickets_left": team["tickets"]
                })
                self.winners.sort(key=lambda x: x["duration_seconds"])
                
            team["clues_received"].append({
                "type": "system",
                "text": "🎉 Timeline Stabilized! You successfully rescued Sam and restored the Memory Core!",
                "timestamp": time.time()
            })

    def move_team(self, team_name: str, target_node: int) -> Dict[str, Any]:
        if self.game_status != "active":
            return {"success": False, "message": "Game is not active"}
            
        team = self.teams.get(team_name)
        if not team:
            return {"success": False, "message": "Team not found"}
            
        if team["is_eliminated"] or team["found_sam"]:
            return {"success": False, "message": "Team is inactive or has already finished"}
            
        # Check if the team is locked by an unsolved puzzle
        if team.get("active_puzzle_node") is not None:
            return {"success": False, "message": "❌ SECURITY LOCK: You must decrypt the communication key at this landmark before moving ahead."}
            
        if target_node not in self.get_adjacent_nodes(team["current_node"]):
            return {"success": False, "message": "Target location is not adjacent"}
            
        if team["tickets"] <= 0:
            team["is_eliminated"] = True
            team["finish_time"] = time.time()
            return {"success": False, "message": "No tickets left"}
            
        # Enforce security clearance to enter Sam's node
        required_clearance = 3
        if target_node == self.sam_current_node:
            solved_count = len(team["puzzles_solved"])
            if solved_count < required_clearance:
                return {"success": False, "message": f"❌ TIMELINE GLITCH: Security Clearance Level {required_clearance} required to stabilize the Memory Core. Decrypt more memories (Solved: {solved_count}/{required_clearance})."}
            
        # Execute Move
        team["tickets"] -= 1
        team["current_node"] = target_node
        team["history"].append(target_node)
        team["moves_since_last_intel"] += 1
        
        result = {
            "success": True,
            "tickets": team["tickets"],
            "current_node": target_node,
            "riddle_triggered": False
        }
        
        # Check Win Condition
        if target_node == self.sam_current_node:
            self.handle_team_win(team_name)
            result["found_sam"] = True
            return result
            
        # Check Elimination
        if team["tickets"] <= 0:
            team["is_eliminated"] = True
            team["finish_time"] = time.time()
            team["clues_received"].append({
                "type": "system",
                "text": "❌ Chrono-Friction: Out of tickets. Team lost in the collapsing memory timeline.",
                "timestamp": time.time()
            })
            return result

        # Check for Charles Leclerc cameo at Node 7 (Grand Hotel Hairpin Science Lab)
        if target_node == 7:
            team["clues_received"].append({
                "type": "system",
                "text": "🏎️ Charles Leclerc Monaco GP Crossover: You hear a screeching sound. Charles Leclerc zooms past in his red Ferrari SF-24, looks at you, and yells: 'No, no! I am trying to win the Monaco Grand Prix on May 26th, 2024, but there is a giant school desk and a memory core glitching in the middle of the track at the Grand Hotel Hairpin! My race engineer is just saying: We are checking! Help me stabilize the memory timeline so I can take the chequered flag!'",
                "timestamp": time.time()
            })
            result["cameo_trigger"] = "charles_leclerc"

        if target_node in self.puzzles and target_node not in team["puzzles_solved"]:
            team["active_puzzle_node"] = target_node
            result["riddle_triggered"] = True
            result["riddle_question"] = self.puzzles[target_node]["question"]
            
        # Process moves-based automatic clues (Every 3 moves)
        if team["moves_since_last_intel"] >= 3:
            team["moves_since_last_intel"] = 0
            unsolved_nodes = [nid for nid in self.puzzles.keys() if nid not in team["puzzles_solved"]]
            if unsolved_nodes:
                hint_node_id = random.choice(unsolved_nodes)
                hint_name = self.nodes[hint_node_id]["name"]
                hint_msg = f"🔍 Signal Tracer: Go to '{hint_name}' (Node {hint_node_id}) to decrypt a school memory fragment."
            else:
                hint_msg = "🔍 Signal Tracer: Memory decryption complete. Go find Sam in the campus grid!"
                
            team["clues_received"].append({
                "type": "intel_hint",
                "text": hint_msg,
                "timestamp": time.time()
            })
            result["new_clue"] = hint_msg

        return result

    def solve_puzzle(self, team_name: str, answer: str) -> Dict[str, Any]:
        team = self.teams.get(team_name)
        if not team:
            return {"success": False, "message": "Team not found"}
            
        puzzle_node = team["active_puzzle_node"]
        if puzzle_node is None:
            return {"success": False, "message": "No active puzzle for team"}
            
        puzzle = self.puzzles.get(puzzle_node)
        if not puzzle:
            team["active_puzzle_node"] = None
            return {"success": False, "message": "Puzzle data not found"}
            
        user_ans = answer.strip().lower()
        correct_ans = puzzle["answer"].strip().lower()
        
        if user_ans == correct_ans:
            team["puzzles_solved"].append(puzzle_node)
            team["active_puzzle_node"] = None
            
            solved_count = len(team["puzzles_solved"])
            sam_loc = self.nodes[self.sam_current_node]
            sam_x = sam_loc["x"]
            sam_y = sam_loc["y"]
            
            # Generate pool of valid clues
            clue_pool = []
            
            # 1. North/South half
            clue_pool.append("The target is in the Northern region (Rows 0-3)." if sam_y < 4 else "The target is in the Southern region (Rows 4-7).")
            # 2. East/West half
            clue_pool.append("The target is in the Western region (Cols 0-4)." if sam_x < 5 else "The target is in the Eastern region (Cols 5-9).")
            # 3. Row parity
            clue_pool.append("The target's grid row index is even." if sam_y % 2 == 0 else "The target's grid row index is odd.")
            # 4. Col parity
            clue_pool.append("The target's grid column index is even." if sam_x % 2 == 0 else "The target's grid column index is odd.")
            # 5. Coordinate sum parity
            clue_pool.append("The sum of the target's grid coordinates (X + Y) is even." if (sam_x + sam_y) % 2 == 0 else "The sum of the target's grid coordinates (X + Y) is odd.")
            # 6. Outer boundary check
            clue_pool.append("The target is on the outer border of the campus grid." if (sam_x == 0 or sam_x == 9 or sam_y == 0 or sam_y == 7) else "The target is in the inner section of the campus grid (not on outer edges).")
            # 7. Row range check
            clue_pool.append("The target is located in the lower rows (Row 3 to 7)." if sam_y >= 3 else "The target is located in the upper rows (Row 0 to 4).")
            # 8. Column range check
            clue_pool.append("The target is located in the right-hand columns (Col 4 to 9)." if sam_x >= 4 else "The target is located in the left-hand columns (Col 0 to 5).")
            # 9. Far-left check
            clue_pool.append("The target is in the leftmost columns (Cols 0-2)." if sam_x <= 2 else "The target is not in the leftmost columns (Cols 0-2).")
            # 10. Far-right check
            clue_pool.append("The target is in the rightmost columns (Cols 7-9)." if sam_x >= 7 else "The target is not in the rightmost columns (Cols 7-9).")
            # 11. Top rows check
            clue_pool.append("The target is in the top rows (Rows 0-2)." if sam_y <= 2 else "The target is not in the top rows (Rows 0-2).")
            # 12. Bottom rows check
            clue_pool.append("The target is in the bottom rows (Rows 6-7)." if sam_y >= 6 else "The target is not in the bottom rows (Rows 6-7).")
            
            # Pick 3 random clues
            random.seed(time.time() + solved_count)
            selected = random.sample(clue_pool, min(3, len(clue_pool)))
            
            # Combined text for alert popup modal
            clue_text = f"🔒 Decrypted Intel (Clearance Level: {solved_count}/3):\n" + "\n".join(f"- {c}" for c in selected)

            # Append each clue as an individual entry to yield multiple separate items in team dossier
            for idx, c in enumerate(selected):
                team["clues_received"].append({
                    "type": "intel",
                    "text": f"🔒 Decrypted Intel {solved_count}.{idx + 1}/3: {c}",
                    "timestamp": time.time()
                })
            
            return {
                "success": True,
                "message": "Correct! Intel unlocked.",
                "intel": clue_text
            }
        else:
            return {
                "success": False,
                "message": "Incorrect answer. Try again!"
            }

    def bypass_puzzle(self, team_name: str):
        # Do not allow bypassing the puzzle! They must solve it.
        pass

    def get_team_view_data(self, team_name: str) -> Dict[str, Any]:
        team = self.teams.get(team_name)
        if not team:
            return {}
            
        map_data = []
        for i in range(80):
            node = self.nodes[i]
            map_data.append({
                "id": node["id"],
                "name": node["name"],
                "x": node["x"],
                "y": node["y"]
            })
            
        adjacent = self.get_adjacent_nodes(team["current_node"])
        
        active_puzzle = None
        if team["active_puzzle_node"] is not None:
            p_node = team["active_puzzle_node"]
            active_puzzle = {
                "node_id": p_node,
                "question": self.puzzles[p_node]["question"]
            }
            
        total_teams = len(self.teams)
        finished_or_eliminated = sum(1 for t in self.teams.values() if t["found_sam"] or t["is_eliminated"])
        winner_announced = len(self.winners) >= 3 or (total_teams > 0 and finished_or_eliminated == total_teams and len(self.winners) > 0)
        
        if team["found_sam"] or team["is_eliminated"]:
            elapsed_seconds = int(team["finish_time"] - self.start_time)
        else:
            elapsed_seconds = int(time.time() - self.start_time) if self.game_status == "active" else 0
            
        links = []
        for u in self.adj_list:
            for v in self.adj_list[u]:
                if u < v:
                    links.append({"source": u, "target": v, "is_diagonal": False})
        if self.diagonal_allowed:
            for i in range(80):
                curr = self.nodes[i]
                for j in range(i + 1, 80):
                    node = self.nodes[j]
                    if abs(node["x"] - curr["x"]) == 1 and abs(node["y"] - curr["y"]) == 1:
                        links.append({"source": i, "target": j, "is_diagonal": True})
        
        return {
            "team_name": team_name,
            "tickets": team["tickets"],
            "current_node": team["current_node"],
            "adjacent_nodes": adjacent,
            "history": [self.nodes[nid]["name"] for nid in team["history"]],
            "clues": team["clues_received"],
            "active_puzzle": active_puzzle,
            "is_eliminated": team["is_eliminated"],
            "found_sam": team["found_sam"],
            "game_status": self.game_status,
            "winners": self.winners if winner_announced else [],
            "winners_count": len(self.winners),
            "clearance_level": len(team["puzzles_solved"]),
            "required_clearance": 3,
            "elapsed_seconds": elapsed_seconds,
            "map_nodes": map_data,
            "links": links,
            "diagonal_nodes_allowed": self.diagonal_allowed
        }
 
    def get_gm_view_data(self, connected_teams: List[str] = None) -> Dict[str, Any]:
        teams_data = {}
        for name, data in self.teams.items():
            teams_data[name] = {
                "current_node": data["current_node"],
                "history": data["history"],
                "tickets": data["tickets"],
                "is_eliminated": data["is_eliminated"],
                "found_sam": data["found_sam"],
                "puzzles_solved_count": len(data["puzzles_solved"]),
                "last_active": data.get("finish_time", 0.0) or data.get("join_time", 0.0),
                "elapsed_seconds": int((data.get("finish_time", 0.0) or time.time()) - self.start_time) if self.game_status == "active" else 0,
                "is_online": (connected_teams is not None and name in connected_teams)
            }
            
        map_data = []
        for i in range(80):
            node = self.nodes[i]
            has_puzzle = i in self.puzzles
            map_data.append({
                "id": node["id"],
                "name": node["name"],
                "x": node["x"],
                "y": node["y"],
                "has_puzzle": has_puzzle
            })
            
        elapsed_seconds = int(time.time() - self.start_time) if self.game_status == "active" else 0
        
        links = []
        for u in self.adj_list:
            for v in self.adj_list[u]:
                if u < v:
                    links.append({"source": u, "target": v, "is_diagonal": False})
        if self.diagonal_allowed:
            for i in range(80):
                curr = self.nodes[i]
                for j in range(i + 1, 80):
                    node = self.nodes[j]
                    if abs(node["x"] - curr["x"]) == 1 and abs(node["y"] - curr["y"]) == 1:
                        links.append({"source": i, "target": j, "is_diagonal": True})
            
        return {
            "game_status": self.game_status,
            "diagonal_allowed": self.diagonal_allowed,
            "sam_static": self.sam_static,
            "sam_current_node": self.sam_current_node,
            "sam_coords": {
                "name": self.nodes[self.sam_current_node]["name"],
                "x": self.nodes[self.sam_current_node]["x"],
                "y": self.nodes[self.sam_current_node]["y"]
            },
            "sam_path": self.sam_path,
            "sam_movement_interval": self.sam_movement_interval,
            "elapsed_seconds": elapsed_seconds,
            "teams": teams_data,
            "map_nodes": map_data,
            "links": links,
            "winners": self.winners,
            "puzzles": [{"node_id": k, "question": v["question"], "answer": v["answer"]} for k, v in self.puzzles.items()]
        }
 
    def configure_game(self, config: Dict[str, Any]):
        # Allow configuring diagonal moves, static Sam, and move timer during active game
        if "diagonal_allowed" in config:
            self.diagonal_allowed = bool(config["diagonal_allowed"])
            
        if "sam_static" in config:
            self.sam_static = bool(config["sam_static"])
            if not self.sam_static and self.last_sam_move_time == 0.0:
                self.last_sam_move_time = time.time()
                
        if "sam_movement_interval" in config:
            self.sam_movement_interval = int(config["sam_movement_interval"])
            
        # Rest of configuration structural settings only during setup
        if self.game_status == "setup":
            if "sam_start_node" in config:
                start_node = int(config["sam_start_node"])
                if 0 <= start_node < 80:
                    self.sam_start_node = start_node
                    self.sam_current_node = start_node
                    
            if "sam_path" in config:
                path = config["sam_path"]
                if isinstance(path, list) and all(isinstance(x, int) and 0 <= x < 80 for x in path):
                    self.sam_path = path
                    
            if "puzzles" in config:
                p_list = config["puzzles"]
                self.puzzles.clear()
                for p in p_list:
                    node_id = int(p["node_id"])
                    if 0 <= node_id < 80:
                        self.puzzles[node_id] = {
                            "question": str(p["question"]),
                            "answer": str(p["answer"]),
                            "intel": ""
                        }
                        
        return True

    def save_state(self, filepath: str):
        state = {
            "game_status": self.game_status,
            "sam_static": self.sam_static,
            "sam_start_node": self.sam_start_node,
            "sam_path": self.sam_path,
            "sam_path_index": self.sam_path_index,
            "sam_current_node": self.sam_current_node,
            "start_time": self.start_time,
            "teams": self.teams,
            "puzzles": self.puzzles,
            "winners": self.winners
        }
        with open(filepath, 'w') as f:
            json.dump(state, f)

    def load_state(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
                
            self.game_status = state["game_status"]
            self.sam_static = state["sam_static"]
            self.sam_start_node = state["sam_start_node"]
            self.sam_path = state["sam_path"]
            self.sam_path_index = state["sam_path_index"]
            self.sam_current_node = state["sam_current_node"]
            self.start_time = state.get("start_time", 0.0)
            self.teams = state["teams"]
            self.puzzles = {int(k): v for k, v in state["puzzles"].items()}
            self.winners = state["winners"]
        except FileNotFoundError:
            pass

    def tick_sam_movement(self) -> bool:
        if self.sam_static or self.game_status != "active":
            return False
            
        now = time.time()
        if now - self.last_sam_move_time >= self.sam_movement_interval:
            if len(self.sam_path) > 1:
                self.sam_path_index = (self.sam_path_index + 1) % len(self.sam_path)
                self.sam_current_node = self.sam_path[self.sam_path_index]
                self.last_sam_move_time = now
                self.update_puzzle_intel()
                
                # Check for collision with teams
                for name, team in self.teams.items():
                    if not team["is_eliminated"] and not team["found_sam"] and team["current_node"] == self.sam_current_node:
                        self.handle_team_win(name)
                return True
        return False

    def update_puzzle_intel(self):
        pass
