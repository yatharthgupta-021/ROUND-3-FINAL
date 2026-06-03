import collections

# Define 80 nodes
nodes = {}
# Winding Monaco Track nodes (0 to 59)
# y=0: 0..11
# y=1: 12..23
# y=2: 24..35
# y=3: 36..47
# y=4: 48..59
# Wait, let's lay them out in a snake or Monaco GP track pattern.
# Let's map each index to a coordinate and a name.
# Let's just define the nodes list directly with coordinates.

track_nodes_def = [
    # Row 0: y=0 (12 nodes)
    (0, "Grid Start Line", 0, 0),
    (1, "F1 Pit Lane Exit", 1, 0),
    (2, "Speed Trap Straight", 2, 0),
    (3, "Leclerc Fan Zone", 3, 0),
    (4, "Monaco GP Main Grandstand", 4, 0),
    (5, "Sponsor Gantry", 5, 0),
    (6, "Telemetry Broadcast Tower", 6, 0),
    (7, "Red Bull Energy Station", 7, 0),
    (8, "Marshal Post 1", 8, 0),
    (9, "Sainte Devote Turn 1", 9, 0),
    (10, "Sainte Devote Apex", 10, 0),
    (11, "Beau Rivage Ascent", 11, 0),
    
    # Row 1: y=1 (12 nodes)
    (12, "Beau Rivage S-Bends", 11, 1),
    (13, "Massenet Left Entry", 10, 1),
    (14, "Massenet Apex", 9, 1),
    (15, "Casino Square Gardens", 8, 1),
    (16, "Casino Square Corner", 7, 1),
    (17, "Casino Square Straight", 6, 1),
    (18, "Mirabeau Haute Entry", 5, 1),
    (19, "Mirabeau Haute Apex", 4, 1),
    (20, "Grand Hotel Hairpin", 3, 1),
    (21, "Mirabeau Bas Corner", 2, 1),
    (22, "Portier Corner Entry", 1, 1),
    (23, "Portier Seaside Apex", 0, 1),
    
    # Row 2: y=2 (12 nodes)
    (24, "Portier Seafront", 0, 2),
    (25, "Tunnel Entrance", 1, 2),
    (26, "Tunnel Midpoint", 2, 2),
    (27, "Tunnel Exit", 3, 2),
    (28, "Nouvelle Chicane Braking", 4, 2),
    (29, "Nouvelle Chicane Apex", 5, 2),
    (30, "Chicane Exit Acceleration", 6, 2),
    (31, "Tabac Harbor Corner", 7, 2),
    (32, "Louis Chiron Chicane Entry", 8, 2),
    (33, "Piscine Swimming Pool Entry", 9, 2),
    (34, "Swimming Pool Apex", 10, 2),
    (35, "Piscine Chicane Exit", 11, 2),
    
    # Row 3: y=3 (12 nodes)
    (36, "Rascasse Entry Straight", 11, 3),
    (37, "Rascasse Outer Wall", 10, 3),
    (38, "Rascasse Apex (Hard Left)", 9, 3),
    (39, "Anthony Noghes Turn", 8, 3),
    (40, "Pit Lane Entry Road", 7, 3),
    (41, "Grid Straight Entry", 6, 3),
    (42, "Podium Ceremonial Stage", 5, 3),
    (43, "F1 Team Garages", 4, 3),
    (44, "Paddock Hospitality", 3, 3),
    (45, "Monaco Yacht Club Dock", 2, 3),
    (46, "Harborside Boardwalk", 1, 3),
    (47, "Ste Devote Run-off Zone", 0, 3),
    
    # Row 4: y=4 (12 nodes)
    (48, "Sainte Devote Sandbox", 0, 4),
    (49, "Beau Rivage Corridor", 1, 4),
    (50, "Massenet Classroom", 2, 4),
    (51, "Casino Square Library", 3, 4),
    (52, "Mirabeau Haute Playground", 4, 4),
    (53, "Grand Hotel Hairpin Science Lab", 5, 4),
    (54, "Portier Math Room", 6, 4),
    (55, "Tunnel Cafeteria", 7, 4),
    (56, "Piscine Recess Yard", 8, 4),
    (57, "Rascasse Chemistry Lab", 9, 4),
    (58, "Anthony Noghes Computer Room", 10, 4),
    (59, "Kindergarten Playroom", 11, 4),
    
    # Row 5: y=5 (12 nodes)
    (60, "School Assembly Hall", 11, 5),
    (61, "Music Practice Room", 10, 5),
    (62, "Art Studio", 9, 5),
    (63, "Drama Theater", 8, 5),
    (64, "History Corridor", 7, 5),
    (65, "Geography Lab", 6, 5),
    (66, "Language Center", 5, 5),
    (67, "English Lit Corner", 4, 5),
    (68, "Principal's Office Entry", 3, 5),
    (69, "Staff Common Room", 2, 5),
    (70, "Counselor's Office", 1, 5),
    (71, "School Clinic Spur", 0, 5),
    
    # Row 6: y=6 (8 nodes for spurs)
    (72, "Detention Room", 0, 6),
    (73, "Locker Room Corridor", 1, 6),
    (74, "Sports Equipment Room", 2, 6),
    (75, "Biology Greenhouse", 3, 6),
    (76, "Physics Lab Corridor", 4, 6),
    (77, "Gymnasium Court", 5, 6),
    (78, "Running Track Spur", 6, 6),
    (79, "School Gate Exit", 7, 6)
]

# Let's write a connections generator.
# We want the track to be a loop of nodes:
# 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 ->
# 12 -> 13 -> 14 -> 15 -> 16 -> 17 -> 18 -> 19 -> 20 -> 21 -> 22 -> 23 ->
# 24 -> 25 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32 -> 33 -> 34 -> 35 ->
# 36 -> 37 -> 38 -> 39 -> 40 -> 41 -> 42 -> 43 -> 44 -> 45 -> 46 -> 47 ->
# 47 connects to 0? Yes, that forms a loop of 48 track nodes.
# Let's verify track loop: 0 to 47.
# Then we have spurs and memory locations.
# Nodes 48 to 79 are spurs and classroom memories branching off.
# Let's connect them to track nodes:
# e.g., 48 (Sainte Devote Sandbox) connects to 9 (Sainte Devote Turn 1)
# 49 connects to 48 and 50 (forming a branch line: 9 -> 48 -> 49 -> 50)
# Let's write connections explicitly.
connections = []
# Track loop: 0 -> 1 -> ... -> 47 -> 0
for i in range(48):
    connections.append((i, (i + 1) % 48))

# Let's connect the memory locations (48 to 79):
# Memory corridor 1: 9 -> 48 -> 49 -> 50 -> 51 -> 52
connections.append((9, 48))
connections.append((48, 49))
connections.append((49, 50))
connections.append((50, 51))
connections.append((51, 52))

# Memory corridor 2: 20 -> 53 -> 54 -> 55 -> 56 -> 57 -> 58
connections.append((20, 53))
connections.append((53, 54))
connections.append((54, 55))
connections.append((55, 56))
connections.append((56, 57))
connections.append((57, 58))

# Memory corridor 3: 35 -> 59 -> 60 -> 61 -> 62 -> 63
connections.append((35, 59))
connections.append((59, 60))
connections.append((60, 61))
connections.append((61, 62))
connections.append((62, 63))

# Memory corridor 4: 43 -> 64 -> 65 -> 66 -> 67 -> 68 -> 69
connections.append((43, 64))
connections.append((64, 65))
connections.append((65, 66))
connections.append((66, 67))
connections.append((67, 68))
connections.append((68, 69))

# School spurs:
connections.append((69, 70))
connections.append((70, 71))
connections.append((71, 72))
connections.append((72, 73))
connections.append((73, 74))
connections.append((74, 75))
connections.append((75, 76))
connections.append((76, 77))
connections.append((77, 78))
connections.append((78, 79))

# Build adjacency list
adj = collections.defaultdict(list)
for u, v in connections:
    adj[u].append(v)
    adj[v].append(u)

# Let's test distances to Sam (let's assume Sam is at Node 53: Grand Hotel Hairpin Science Lab)
# Let's compute shortest path from all nodes to Sam
def get_distances(sam_node):
    dist = {sam_node: 0}
    q = collections.deque([sam_node])
    while q:
        curr = q.popleft()
        for neighbor in adj[curr]:
            if neighbor not in dist:
                dist[neighbor] = dist[curr] + 1
                q.append(neighbor)
    return dist

sam_start = 53
dists = get_distances(sam_start)
starts_ge_25 = [node for node, d in dists.items() if d >= 25]
print(f"Nodes with distance >= 25 from Sam ({sam_start}): {starts_ge_25}")
print(f"Total nodes: {len(track_nodes_def)}")
print(f"Count of nodes >= 25: {len(starts_ge_25)}")
