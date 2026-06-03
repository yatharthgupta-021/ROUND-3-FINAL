import collections

# Loop coordinates (0 to 67)
path = []
# Row 0: (0,0) to (5,0) (6 nodes)
for x in range(6): path.append((x, 0))
# Row 1: (5,1) to (1,1) (5 nodes)
for x in range(5, 0, -1): path.append((x, 1))
# Row 2: (1,2) to (5,2) (5 nodes)
for x in range(1, 6): path.append((x, 2))
# Row 3: (5,3) to (1,3) (5 nodes)
for x in range(5, 0, -1): path.append((x, 3))
# Row 4: (1,4) to (5,4) (5 nodes)
for x in range(1, 6): path.append((x, 4))
# Row 5: (5,5) to (1,5) (5 nodes)
for x in range(5, 0, -1): path.append((x, 5)) # index 26 is (5,5)
# Row 6: (1,6) to (5,6) (5 nodes)
for x in range(1, 6): path.append((x, 6))
# Row 7: (5,7) to (1,7) (5 nodes)
for x in range(5, 0, -1): path.append((x, 7))
# Row 8: (1,8) to (4,8) (4 nodes)
for x in range(1, 5): path.append((x, 8))
# Row 9: (4,9) to (1,9) (4 nodes)
for x in range(4, 0, -1): path.append((x, 9))
# Row 10: (1,10) to (4,10) (4 nodes)
for x in range(1, 5): path.append((x, 10))
# Row 11: (4,11) to (0,11) (5 nodes)
for x in range(4, -1, -1): path.append((x, 11))
# Up column 0:
for y in range(10, 0, -1): path.append((0, y))

# Loop connections
connections = []
for i in range(67):
    connections.append((i, i + 1))
connections.append((67, 0))

# Spur coordinates (68 to 79)
nodes = list(path)

# Node 68: (6, 5) -> connects to Node 26 at (5, 5)
nodes.append((6, 5))
connections.append((26, 68))

# Node 69..79:
spur_coords = [
    (7, 5), (8, 5), (9, 5),  # 69, 70, 71
    (9, 4), (8, 4), (7, 4), (6, 4),  # 72, 73, 74, 75
    (6, 6), (7, 6), (8, 6), (9, 6)   # 76, 77, 78, 79
]
for coord in spur_coords:
    nodes.append(coord)

for i in range(68, 79):
    connections.append((i, i + 1))

# Check duplicate coordinates
assert len(set(nodes)) == 80, f"Duplicate coordinates! Unique: {len(set(nodes))}"

# Build adjacency
adj = collections.defaultdict(list)
for u, v in connections:
    adj[u].append(v)
    adj[v].append(u)

# Check distance from Sam (at node 53)
sam_node = 53
dist = {sam_node: 0}
q = collections.deque([sam_node])
while q:
    curr = q.popleft()
    for neighbor in adj[curr]:
        if neighbor not in dist:
            dist[neighbor] = dist[curr] + 1
            q.append(neighbor)

starts = [node for node, d in dist.items() if d >= 25]
print(f"Node 26 coordinate: {path[26]}")
print(f"Starts >= 25: {len(starts)}, List: {starts}")
