import os
import time
import random
import json
import secrets
import hashlib
from typing import Dict, List, Set, Any, Optional

class GameManager:
    def __init__(self):
        self.game_status = "setup"  # "setup", "active", "ended"
        self.diagonal_allowed = False
        self.sam_static = True
        self.sam_movement_interval = 90
        self.last_sam_move_time = 0.0
        self.start_time = 0.0  # Game start timestamp
        self.pause_start_time = 0.0
        
        # Nodes and adjacency loaded from custom_map.json
        self.nodes: Dict[int, Dict[str, Any]] = {}
        self.adj_list: Dict[int, List[int]] = {}
        self._node_count = 0
        self.load_custom_map()
        
        # Sam Hiding Node (set by load_custom_map, default 0)
        self.sam_start_node = self._default_sam_node
        self.sam_path: List[int] = [self._default_sam_node]
        self.sam_path_index = 0
        self.sam_current_node = self._default_sam_node
        
        # Teams State
        self.teams: Dict[str, Dict[str, Any]] = {}
        
        # Puzzles and Intel Clues (loaded from custom_map.json)
        self.puzzles: Dict[int, Dict[str, str]] = {}
        self._load_puzzles_from_map()
        
        # Winners tracking
        self.winners: List[Dict[str, Any]] = []

    def load_custom_map(self):
        """Load nodes and connections from custom_map.json."""
        map_path = os.path.join(os.path.dirname(__file__), "custom_map.json")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.nodes = {}
        self.adj_list = {}

        for node in data["nodes"]:
            nid = int(node["id"])
            self.nodes[nid] = {
                "id": nid,
                "name": node["name"],
                "x": node["x"],
                "y": node["y"]
            }
            self.adj_list[nid] = []

        for u, v in data["connections"]:
            u, v = int(u), int(v)
            if v not in self.adj_list[u]:
                self.adj_list[u].append(v)
            if u not in self.adj_list[v]:
                self.adj_list[v].append(u)

        self._node_count = len(self.nodes)
        # Sam default node from JSON, fallback to first node id
        self._default_sam_node = int(data.get("sam_start_node", sorted(self.nodes.keys())[0]))
        # Store raw puzzle data for _load_puzzles_from_map
        self._raw_puzzles = data.get("puzzles", [])

    def _load_puzzles_from_map(self):
        """Populate self.puzzles from the raw puzzle list loaded by load_custom_map."""
        for p in self._raw_puzzles:
            node_id = int(p["node_id"])
            if node_id in self.nodes:
                self.puzzles[node_id] = {
                    "question": str(p["question"]),
                    "answer": str(p["answer"]),
                    "intel": ""
                }

    def update_map(self, new_nodes: List[Dict[str, Any]], new_connections: List[List[int]]):
        """Update map structure in memory and save to custom_map.json."""
        map_path = os.path.join(os.path.dirname(__file__), "custom_map.json")
        static_map_path = os.path.join(os.path.dirname(__file__), "static", "custom_map.json")
        
        # Keep old puzzles/sam_start_node
        with open(map_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            
        old_data["nodes"] = new_nodes
        old_data["connections"] = new_connections
        
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(old_data, f, indent=2)
            
        with open(static_map_path, "w", encoding="utf-8") as f:
            json.dump(old_data, f, indent=2)
            
        # Hot-reload in memory
        self.load_custom_map()
        self._load_puzzles_from_map()

    # ---- Kept for historical reference; no longer called ----
    def setup_monaco_map(self):
        """Deprecated: map is now loaded from custom_map.json via load_custom_map()."""
        pass

    def _noop_setup(self):
        # placeholder so old node_defs list below is never executed
        node_defs = [
            # Row 0: y=0 (x: 0..7)
            (0,  "Port Hercules N.",    0, 0),
            (1,  "La Condamine",        1, 0),
            (2,  "Rue Grimaldi",        2, 0),
            (3,  "Casino Square",       3, 0),
            (4,  "Café de Paris",       4, 0),
            (5,  "Monte-Carlo Hotel",   5, 0),
            (6,  "Portier",             6, 0),
            (7,  "Tunnel Entrance",     7, 0),

            # Row 1: y=1 (x: 7..1, reversed)
            (8,  "Nouveau Chicane",     7, 1),
            (9,  "Louis II Stadium",    6, 1),
            (10, "Fontvieille",         5, 1),
            (11, "Jardin Exotique",     4, 1),
            (12, "Princess Antoinette", 3, 1),
            (13, "Larvotto Beach",      2, 1),
            (14, "Blvd. Princesse Ch.", 1, 1),

            # Row 2: y=2 (x: 1..7)
            (15, "Blvd. des Moulins",  1, 2),
            (16, "Saint-Charles Ch.",  2, 2),
            (17, "Rotonde",            3, 2),
            (18, "Grimaldi Forum",     4, 2),
            (19, "Sporting MC",        5, 2),
            (20, "Pointe Paillon",     6, 2),
            (21, "Plage du Larvotto",  7, 2),

            # Row 3: y=3 (x: 7..1, reversed)
            (22, "Le Méridien Beach",  7, 3),
            (23, "Ave. Princesse Gr.", 6, 3),
            (24, "Japanese Garden",    5, 3),
            (25, "Blvd. du Larvotto", 4, 3),
            (26, "Fontvieille Spurs",  3, 3),
            (27, "Larvotto (East)",    2, 3),
            (28, "Chapteau Fontvieille", 1, 3),

            # Row 4: y=4 (x: 1..7)
            (29, "Yacht Club Monaco",  1, 4),
            (30, "Piscine Olympique",  2, 4),
            (31, "Quai Antoine 1er",   3, 4),
            (32, "Saint-Elvire",       4, 4),
            (33, "Tabac Corner",       5, 4),
            (34, "Fairmont Hairpin",   6, 4),
            (35, "Saint Martin Gdns.", 7, 4),

            # Row 5: y=5 (x: 7..1, reversed)
            (36, "Chemin des Révoires", 7, 5),
            (37, "Ave. Princesse Gr.",  6, 5),
            (38, "Exotic Garden",       5, 5),
            (39, "Fort Antoine Thtre.", 4, 5),
            (40, "Prince's Palace",     3, 5),
            (41, "Stade Louis II N.",   2, 5),
            (42, "Musée Océanographique", 1, 5),

            # Row 6: y=6 (x: 1..9)
            (43, "Terrasse Fontvieille", 1, 6),
            (44, "Stade Louis II",       2, 6),
            (45, "Côtes d'Azur W.",      3, 6),
            (46, "Ave. de la Quarant.",  4, 6),
            (47, "Jardin du Casino",     5, 6),
            (48, "Place d'Armes",        6, 6),
            (49, "Blvd. Princesse Ch.",  7, 6),
            (50, "Avenue Beaux-Arts",    8, 6),
            (51, "Rue de Millo",         9, 6),

            # Row 7: y=7 (x: 9..1, reversed)
            (52, "Saint Dévote Ch.",        9, 7),
            (53, "Gare de Monaco",          8, 7),
            (54, "Avenue du Portier",       7, 7),
            (55, "MC Bay Resort",           6, 7),
            (56, "Ave. Princesse Gr. W.",   5, 7),
            (57, "Terrasses Fontvieille",   4, 7),
            (58, "Marché Condamine",        3, 7),
            (59, "Rue Suffren Raymond",     2, 7),
            (60, "Place d'Armes S.",        1, 7),

            # Column 0: x=0, y=7..1 (going up)
            (61, "Rue du Portier",      0, 7),
            (62, "La Costa Props.",     0, 6),
            (63, "Villa Sassone",       0, 5),
            (64, "Blvd. de Belgique",   0, 4),
            (65, "Quai Albert 1er",     0, 3),
            (66, "Yacht Club (West)",   0, 2),
            (67, "Tête de Chien",       0, 1),

            # Spur: Columns 8 and 9, Rows 0 to 5
            (68, "Digue Rainier III",      8, 3),
            (69, "Port de Fontvieille",    8, 4),
            (70, "Marina Fontvieille",     8, 5),
            (71, "Rocher Princesse Gr.",   9, 5),
            (72, "Parc Princesse Ant.",    9, 4),
            (73, "Grimaldi Castle Hill",   9, 3),
            (74, "Chemin des Serres",      9, 2),
            (75, "Avenue Albert II",       8, 2),
            (76, "Blvd. Rainier III",      8, 1),
            (77, "Port Hercules W.",       9, 1),
            (78, "Place du Palais",        9, 0),
            (79, "Blvd. d'Italie",         8, 0)
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
        # Main track serpentine loop (0 to 67), EXCLUDING 7-8
        for i in range(67):
            if i == 7:  # Remove connection 7->8
                continue
            connections.append((i, i + 1))
        connections.append((67, 0))  # Vertically closes loop along x=0
        
        # Spur nodes (68 to 79)
        connections.append((22, 68))  # Branch off main track at loop node 22 (7,3)
        for i in range(68, 79):
            connections.append((i, i + 1))
            
        # Custom user requested connections
        connections.append((79, 8))
        connections.append((70, 35))
        
        # Additional shortcut connections
        connections.append((66, 28))  # Marshal 3 <-> Boardwalk shortcut
        connections.append((42, 44))  # Podium <-> Art shortcut
        connections.append((18, 24))  # Rascasse In <-> Podium shortcut
        connections.append((3, 11))   # Blackboard <-> Tunnel Mid shortcut
            
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
        # 25 HARDER puzzles: 3 Wordle grids, Atbash/Rail-fence ciphers, logic, hex, binary, coordinate rotation
        story_riddles = [
            {
                "node": 3,
                "q": "🎲 CASINO SQUARE — ROMAN NUMERAL ARITHMETIC: The famous Casino Square is at 55 metres elevation — the highest point of the circuit. Solve this encoded calculation:\nXIV² ÷ (VII × II) = ?\n(XIV=14, VII=7, II=2). Calculate and enter the number.",
                "a": "14"
            },
            {
                "node": 5,
                "q": "🏨 MONTE-CARLO HOTEL — WORDLE (5 letters):\n🟩=correct spot | 🟨=wrong spot | ⬛=not in word\n\nAttempt 1:  F⬛  L⬛  I⬛  R🟨  T⬛\nAttempt 2:  D🟨  R🟩  I⬛  N🟩  K⬛\nAttempt 3:  B⬛  R🟩  A🟩  N🟩  D🟩\nAttempt 4:  ?🟩  ?🟩  ?🟩  ?🟩  ?🟩  ← TYPE THE WORD!\n\n💡 Hint: It connects Monaco to the word Prix.",
                "a": "grand"
            },
            {
                "node": 10,
                "q": "🌿 FONTVIEILLE — ATBASH CIPHER: In Atbash, each letter maps to its mirror position in the alphabet (A↔Z, B↔Y, C↔X, D↔W, E↔V, F↔U, G↔T, H↔S, I↔R, J↔Q, K↔P, L↔O, M↔N).\n\nDecode:  N  Z  M  Z  X  L\n\nWhere are Sam's memories set?",
                "a": "monaco"
            },
            {
                "node": 11,
                "q": "🌺 JARDIN EXOTIQUE — THREE-PART RIDDLE:\n🕐 I have hands, but I cannot clap.\n👁️ I have a face, but no eyes.\n🏃 I run without legs and tick without moving.\n\nWhat am I? (one word)",
                "a": "clock"
            },
            {
                "node": 15,
                "q": "🛤️ BLVD. DES MOULINS — MISSING MIDDLE TERM: Find X in the sequence:\n3,  X,  48,  192,  768\nEach term is multiplied by the same constant.\nWhat is X?",
                "a": "12"
            },
            {
                "node": 18,
                "q": "🏛️ GRIMALDI FORUM — F1 LAP FRACTION: The Monaco Grand Prix runs for 78 laps total.\nSam's driver completes exactly HALF the race before a red flag stops it.\nAfter the restart, they complete exactly ONE THIRD of the total race distance.\nHow many laps in total have been completed?",
                "a": "65"
            },
            {
                "node": 20,
                "q": "🏖️ POINTE PAILLON — RAIL FENCE CIPHER (2 rails): A school subject was encrypted by splitting letters across 2 rails:\nRail 1 (positions 0,2,4,6,8):  C  E  I  T  Y\nRail 2 (positions 1,3,5,7):    H  M  S  R\n\nWeave them back together alternating Rail1, Rail2 to decode the 9-letter school subject.",
                "a": "chemistry"
            },
            {
                "node": 24,
                "q": "🌸 JAPANESE GARDEN — SKIP ALPHABET BACKWARDS: The sequence skips every other letter going backwards from Z:\nZ,  X,  V,  T,  R,  ___\nWhat is the next letter?",
                "a": "p"
            },
            {
                "node": 25,
                "q": "🌊 BLVD. DU LARVOTTO — SECTOR TIME MATHS: A driver's three sector times are 28.4s, 31.2s, and 19.4s.\nHis rival is exactly 0.3s FASTER in every single sector.\nWhat is the rival's TOTAL lap time? (answer as a decimal, e.g. 00.0)",
                "a": "78.1"
            },
            {
                "node": 30,
                "q": "🏊 PISCINE OLYMPIQUE — COORDINATE ROTATION: You stand at grid point (2, 3).\nRotate 90° CLOCKWISE about the origin using the formula:\n(x, y)  →  (y, −x)\nWhat is your new position? Answer as 'X,Y' (e.g. 3,-2).",
                "a": "3,-2"
            },
            {
                "node": 34,
                "q": "🏎️ FAIRMONT HAIRPIN — THE SLOWEST CORNER IN F1: The Fairmont Hairpin (formerly Loews Hairpin) is the tightest corner in all of Formula 1. Cars crawl through at barely 50 km/h.\n\nIn the 2024 Monaco GP, drivers completed 78 laps. If a driver spent exactly 4 seconds navigating the hairpin on each lap, how many TOTAL seconds did they spend inside the Fairmont Hairpin across the entire race?\n(78 × 4 = ?)",
                "a": "312"
            },
            {
                "node": 35,
                "q": "🌳 SAINT MARTIN GDNS. — HIDDEN WORD: A 7-letter school subject is hiding as consecutive letters inside a longer word.\nFind it inside:  B I O S C I E N C E\n(Hint: it begins at the 4th letter of the word above)",
                "a": "science"
            },
            {
                "node": 40,
                "q": "👑 PRINCE'S PALACE — HEXADECIMAL DECODE: Computers store values in hex. Convert to decimal:\n0x2F\n(Hint: 0x2F = 2 × 16 + 15 = ?)",
                "a": "47"
            },
            {
                "node": 42,
                "q": "🐠 MUSÉE OCÉANOGRAPHIQUE — NOTE-NUMBER CIPHER: Using the cipher A=1, B=2 ... Z=26, decode these 5 numbers to name a woodwind instrument:\n6  ·  12  ·  21  ·  20  ·  5\nWhat instrument is it?",
                "a": "flute"
            },
            {
                "node": 50,
                "q": "🎨 AVENUE BEAUX-ARTS — MORSE CODE: Decode this Morse transmission:\n-.-. .-.. --- ... .\n(C=-.-.  L=.-..  O=---  S=...  E=.)\nWhat 5-letter word did you decode? Sam is this many steps away.",
                "a": "close"
            },
            {
                "node": 52,
                "q": "⛪ SAINT DÉVOTE CHURCH — MORSE CODE: Saint Dévote is Corner 1 of the Monaco Grand Prix — the very first turn where legends are made. One driver won here a record 6 times and is forever known as the King of Monaco.\n\nHis name is encoded below. Decode it:\n.- -.-- .-. - --- -.  ...  . -. -. .-\nWho is he? (First name + Last name)",
                "a": "ayrton senna"
            },
            {
                "node": 53,
                "q": "🚉 GARE DE MONACO — WORDLE (5 letters):\n🟩=correct spot | 🟨=wrong spot | ⬛=not in word\n\nAttempt 1:  C⬛  R⬛  A⬛  N⬛  E⬛\nAttempt 2:  S🟨  H🟩  O🟩  U⬛  T🟩\nAttempt 3:  F⬛  R⬛  O🟩  S🟩  T🟩\nAttempt 4:  ?🟩  ?🟩  ?🟩  ?🟩  ?🟩  ← TYPE THE WORD!\n\n💡 Hint: Sam is fading like one. Something that haunts a memory.",
                "a": "ghost"
            },
            {
                "node": 55,
                "q": "🏖️ MC BAY RESORT — 3-DIGIT COMBINATION LOCK:\nClue 1: The three digits add up to 15.\nClue 2: The FIRST digit is the square root of 9.\nClue 3: The LAST digit equals the first digit plus 1.\nEnter the 3-digit code (no spaces, e.g. 123).",
                "a": "384"
            },
            {
                "node": 57,
                "q": "🌿 TERRASSES FONTVIEILLE — CHEMISTRY & COMMON NAME: Na is the symbol for Sodium. Cl is the symbol for Chlorine.\nWhen they combine they form the compound NaCl.\nWhat is the common everyday name for NaCl? (one word)",
                "a": "salt"
            },
            {
                "node": 60,
                "q": "🏁 PLACE D'ARMES S. — WORDLE (5 letters):\n🟩=correct spot | 🟨=wrong spot | ⬛=not in word\n\nAttempt 1:  T⬛  R🟩  A🟩  C⬛  K🟨\nAttempt 2:  G⬛  R🟩  A🟩  Z⬛  E🟩\nAttempt 3:  D⬛  R🟩  A🟩  K🟩  E🟩\nAttempt 4:  ?🟩  ?🟩  ?🟩  ?🟩  ?🟩  ← TYPE THE WORD!\n\n💡 Hint: What every F1 driver hits hard at the end of a straight.",
                "a": "brake"
            },
            {
                "node": 62,
                "q": "🏠 LA COSTA PROPS. — NUMBER-LETTER CIPHER (A=1 ... Z=26): Decode this number sequence:\n8  ·  9  ·  19  ·  20  ·  15  ·  18  ·  25\nWhat 7-letter school subject does it spell?",
                "a": "history"
            },
            {
                "node": 65,
                "q": "⚓ QUAI ALBERT 1ER — NATO PHONETIC ALPHABET: Take only the FIRST letter of each NATO code word below:\nPAPA — ALFA — CHARLIE — INDIA — FOXTROT — INDIA — CHARLIE\nWhat 7-letter word (the world's largest ocean) do the first letters spell?",
                "a": "pacific"
            },
            {
                "node": 66,
                "q": "⛵ YACHT CLUB (WEST) — BINARY → LETTER CIPHER: Convert each 5-bit binary number to decimal, then use A=1...Z=26 to find each letter:\n10011  →  ?  →  ?\n00001  →  ?  →  ?\n01101  →  ?  →  ?\nThe 3 letters spell the name of the person you are here to find!",
                "a": "sam"
            },
            {
                "node": 70,
                "q": "⚓ MARINA FONTVIEILLE — LOGIC SEATING PUZZLE: Five people sit in a row.\nClue 1: Amy sits 1st, Dan sits 5th (last).\nClue 2: Ben sits 2nd.\nClue 3: Eva sits directly between Ben and Cal.\nWho sits in the MIDDLE (3rd seat)? (one name)",
                "a": "eva"
            },
            {
                "node": 72,
                "q": "🌿 PARC PRINCESSE ANT. — INTERLEAVED SEQUENCES: Two sequences are woven together alternately:\nSquares:  1,  4,  9,  16,  25 ...\nEvens:    2,  4,  6,   8,  10 ...\nMerged sequence: 1, 2, 4, 4, 9, 6, 16, 8, ___\nWhat is the next number?",
                "a": "25"
            },
            {
                "node": 75,
                "q": "🛣️ AVENUE ALBERT II — WORD CHAIN: Change exactly ONE letter at each step to make a new valid word:\nCARE  →  CORE  →  GORE  →  ?ONE\nThe final word means 'departed' or 'no longer here'.\nWhat is it?",
                "a": "gone"
            },
            {
                "node": 78,
                "q": "🏰 PLACE DU PALAIS — KNIGHT'S TOUR: A chess knight starts at square A1.\nMove 1: 2 RIGHT + 1 UP  →  C2\nMove 2: 1 RIGHT + 2 UP  →  D4\nMove 3: 1 LEFT  + 2 UP  →  ???\nWhat square does the knight land on? (answer in chess notation, e.g. c6)",
                "a": "c6"
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
        if self.game_status == "ended":
            return False
        if team_name in self.teams:
            return False
            
        # Determine starting node with at least some distance from Sam
        sam_node = self.sam_current_node
        possible_starts = []
        for nid in self.nodes:
            dist = self.get_shortest_path_distance(nid, sam_node)
            is_occupied = any(t["current_node"] == nid for t in self.teams.values())
            # Enforce distance >= 25 and avoid start overlap if possible
            if dist >= 25 and not is_occupied:
                possible_starts.append(nid)
                
        if not possible_starts:
            # Fallback: choose any node with maximum distance >= 20
            possible_starts = [nid for nid in self.nodes if self.get_shortest_path_distance(nid, sam_node) >= 20]
            
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
            "active_puzzle_node": None,
            "started": False,
            "start_time": 0.0,
            "puzzle_presented_at": 0.0,
            "last_solve_attempt": 0.0,
            "solve_times": [],
            "suspicious_flags": []
        }
        
        # Provide starting location info
        self.teams[team_name]["clues_received"].append({
            "type": "system",
            "text": f"📍 Project Rewind Deployed: Landed at '{self.nodes[assigned_node]['name']}' (Node {assigned_node}). Security Clearance Level 0.",
            "timestamp": time.time()
        })
        return True

    def remove_team(self, team_name: str):
        if team_name in self.teams:
            del self.teams[team_name]

    def start_team(self, team_name: str) -> bool:
        team = self.teams.get(team_name)
        if not team:
            return False
        
        # If the global game is in setup, transition it to active
        if self.game_status == "setup":
            self.game_status = "active"
            self.start_time = time.time()
            self.last_sam_move_time = time.time()
            self.sam_current_node = self.sam_start_node
            
        if not team.get("started", False):
            team["started"] = True
            team["start_time"] = time.time()
            team["join_time"] = team["start_time"]
            team["tickets"] = 50
            team["is_eliminated"] = False
            team["found_sam"] = False
            team["moves_since_last_intel"] = 0
            return True
        return False

    def start_game(self):
        if self.game_status == "setup":
            self.game_status = "active"
            self.start_time = time.time()
            self.last_sam_move_time = time.time()
            self.sam_current_node = self.sam_start_node

    def pause_game(self) -> bool:
        if self.game_status == "active":
            self.game_status = "paused"
            self.pause_start_time = time.time()
            return True
        return False

    def resume_game(self) -> bool:
        if self.game_status == "paused":
            pause_duration = time.time() - self.pause_start_time
            self.start_time += pause_duration
            self.last_sam_move_time += pause_duration
            
            for team in self.teams.values():
                if team.get("start_time", 0.0) > 0.0:
                    team["start_time"] += pause_duration
                if team.get("join_time", 0.0) > 0.0:
                    team["join_time"] += pause_duration
                if team.get("puzzle_presented_at", 0.0) > 0.0:
                    team["puzzle_presented_at"] += pause_duration
                if team.get("last_solve_attempt", 0.0) > 0.0:
                    team["last_solve_attempt"] += pause_duration
                
            self.game_status = "active"
            self.pause_start_time = 0.0
            return True
        return False

    def handle_team_win(self, team_name: str):
        team = self.teams.get(team_name)
        if team and not team["found_sam"] and not team["is_eliminated"]:
            team["found_sam"] = True
            team["finish_time"] = time.time()
            team_start = team.get("start_time", 0.0) or self.start_time
            duration = team["finish_time"] - team_start
            
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
        # Input validation: ensure target_node is a valid integer within graph
        if not isinstance(target_node, int) or target_node not in self.nodes:
            return {"success": False, "message": "Invalid target node"}

        if self.game_status != "active":
            return {"success": False, "message": "Game is not active"}
            
        team = self.teams.get(team_name)
        if not team:
            return {"success": False, "message": "Team not found"}
            
        if not team.get("started", False):
            return {"success": False, "message": "❌ SECURITY LOCK: You must click 'Start Mission' to begin."}
            
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
            team["puzzle_presented_at"] = time.time()
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

        # Input validation: sanitize answer length
        if not isinstance(answer, str) or len(answer) > 200:
            return {"success": False, "message": "Invalid answer format"}

        puzzle_node = team["active_puzzle_node"]
        if puzzle_node is None:
            return {"success": False, "message": "No active puzzle for team"}
            
        puzzle = self.puzzles.get(puzzle_node)
        if not puzzle:
            team["active_puzzle_node"] = None
            return {"success": False, "message": "Puzzle data not found"}

        # Track solve attempt timing
        now = time.time()
        team["last_solve_attempt"] = now

        user_ans = answer.strip().lower()
        correct_ans = puzzle["answer"].strip().lower()
        
        if user_ans == correct_ans:
            # Anti-AI: track how fast they solved it
            presented_at = team.get("puzzle_presented_at", 0.0)
            solve_duration = now - presented_at if presented_at > 0 else 999
            team["solve_times"].append({
                "node": puzzle_node,
                "duration_seconds": round(solve_duration, 2),
                "timestamp": now
            })
            # Flag suspiciously fast solves (under 5 seconds)
            if solve_duration < 5.0:
                team["suspicious_flags"].append({
                    "type": "fast_solve",
                    "node": puzzle_node,
                    "duration": round(solve_duration, 2),
                    "timestamp": now
                })
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
            clue_text = f"🔒 Decrypted Intel (Clearance Level: {solved_count}):\n" + "\n".join(f"- {c}" for c in selected)

            # Append each clue as an individual entry to yield multiple separate items in team dossier
            for idx, c in enumerate(selected):
                team["clues_received"].append({
                    "type": "intel",
                    "text": f"🔒 Decrypted Intel {solved_count}.{idx + 1}: {c}",
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

    def bypass_puzzle(self, team_name: str) -> Dict[str, Any]:
        """Bypass is explicitly disabled — teams must solve puzzles."""
        return {"success": False, "message": "Bypass is disabled. Solve the puzzle!"}

    def get_team_view_data(self, team_name: str) -> Dict[str, Any]:
        team = self.teams.get(team_name)
        if not team:
            return {}
            
        map_data = []
        for nid in sorted(self.nodes.keys()):
            node = self.nodes[nid]
            map_data.append({
                "id": node["id"],
                "name": node["name"],
                "x": node["x"],
                "y": node["y"]
            })
            
        # Don't expose adjacent nodes for inactive teams
        if team["is_eliminated"] or team["found_sam"]:
            adjacent = []
        else:
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
            team_start = team.get("start_time", 0.0) or self.start_time
            elapsed_seconds = int(team["finish_time"] - team_start)
        else:
            team_start = team.get("start_time", 0.0)
            now = self.pause_start_time if self.game_status == "paused" else time.time()
            elapsed_seconds = int(now - team_start) if team_start > 0.0 else 0
            
        links = []
        for u in self.adj_list:
            for v in self.adj_list[u]:
                if u < v:
                    links.append({"source": u, "target": v, "is_diagonal": False})
        if self.diagonal_allowed:
            nids = sorted(self.nodes.keys())
            for idx_a, i in enumerate(nids):
                curr = self.nodes[i]
                for j in nids[idx_a + 1:]:
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
            "diagonal_nodes_allowed": self.diagonal_allowed,
            "started": team.get("started", False)
        }
 
    def get_gm_view_data(self, connected_teams: List[str] = None) -> Dict[str, Any]:
        teams_data = {}
        for name, data in self.teams.items():
            team_start = data.get("start_time", 0.0) or self.start_time
            now = self.pause_start_time if self.game_status == "paused" else time.time()
            teams_data[name] = {
                "current_node": data["current_node"],
                "history": data["history"],
                "tickets": data["tickets"],
                "is_eliminated": data["is_eliminated"],
                "found_sam": data["found_sam"],
                "puzzles_solved_count": len(data["puzzles_solved"]),
                "last_active": data.get("finish_time", 0.0) or data.get("join_time", 0.0),
                "elapsed_seconds": int((data.get("finish_time", 0.0) or now) - team_start) if data.get("started", False) else 0,
                "is_online": (connected_teams is not None and name in connected_teams),
                "started": data.get("started", False),
                "solve_times": data.get("solve_times", []),
                "suspicious_flags": data.get("suspicious_flags", [])
            }
            
        map_data = []
        for nid in sorted(self.nodes.keys()):
            node = self.nodes[nid]
            has_puzzle = nid in self.puzzles
            map_data.append({
                "id": node["id"],
                "name": node["name"],
                "x": node["x"],
                "y": node["y"],
                "has_puzzle": has_puzzle
            })
            
        now = self.pause_start_time if self.game_status == "paused" else time.time()
        elapsed_seconds = int(now - self.start_time) if self.game_status in ("active", "paused") else 0
        
        links = []
        for u in self.adj_list:
            for v in self.adj_list[u]:
                if u < v:
                    links.append({"source": u, "target": v, "is_diagonal": False})
        if self.diagonal_allowed:
            nids = sorted(self.nodes.keys())
            for idx_a, i in enumerate(nids):
                curr = self.nodes[i]
                for j in nids[idx_a + 1:]:
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
            "seconds_since_sam_move": int((self.pause_start_time if self.game_status == "paused" else time.time()) - self.last_sam_move_time),
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
                if start_node in self.nodes:
                    self.sam_start_node = start_node
                    self.sam_current_node = start_node
                    
            if "sam_path" in config:
                path = config["sam_path"]
                if isinstance(path, list) and all(isinstance(x, int) and x in self.nodes for x in path):
                    self.sam_path = path
                    
            if "puzzles" in config:
                p_list = config["puzzles"]
                self.puzzles.clear()
                for p in p_list:
                    node_id = int(p["node_id"])
                    if node_id in self.nodes:
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
            "pause_start_time": self.pause_start_time,
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
            self.pause_start_time = state.get("pause_start_time", 0.0)
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
