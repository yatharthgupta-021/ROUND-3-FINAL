import collections

# Define nodes list
nodes = []
connections = []

# Row 0: x from 0 to 11, y=0 (Nodes 0..11)
for x in range(12):
    nodes.append((len(nodes), f"Loc {len(nodes)}", x, 0))
# Row 1: x from 11 to 1, y=1 (Nodes 12..22)
for x in range(11, 0, -1):
    nodes.append((len(nodes), f"Loc {len(nodes)}", x, 1))
# Row 2: x from 1 to 11, y=2 (Nodes 23..33)
for x in range(1, 12):
    nodes.append((len(nodes), f"Loc {len(nodes)}", x, 2))
# Row 3: x from 11 to 1, y=3 (Nodes 34..44)
for x in range(11, 0, -1):
    nodes.append((len(nodes), f"Loc {len(nodes)}", x, 3))
# Row 4: x from 1 to 11, y=4 (Nodes 45..55)
for x in range(1, 12):
    nodes.append((len(nodes), f"Loc {len(nodes)}", x, 4))
# Row 5: x from 11 to 0, y=5 (Nodes 56..67)
for x in range(11, -1, -1):
    nodes.append((len(nodes), f"Loc {len(nodes)}", x, 5))

# Loop connections: 0->1->2...->67->0
for i in range(67):
    connections.append((i, i + 1))
connections.append((67, 0))

# Spurs: Row 6 (Nodes 68..79)
for x in range(12):
    nodes.append((len(nodes), f"Spur {len(nodes)}", x, 6))

connections.append((67, 68)) # Connect spur start to main loop
for i in range(68, 79):
    connections.append((i, i + 1))

# Build adjacency
adj = collections.defaultdict(list)
for u, v in connections:
    adj[u].append(v)
    adj[v].append(u)

# Shortest path from any Sam node (e.g. Node 35)
def test_dists(sam_node):
    dist = {sam_node: 0}
    q = collections.deque([sam_node])
    while q:
        curr = q.popleft()
        for n in adj[curr]:
            if n not in dist:
                dist[n] = dist[curr] + 1
                q.append(n)
    return dist

for sam_node in [30, 35, 40]:
    dists = test_dists(sam_node)
    starts = [n for n, d in dists.items() if d >= 25]
    print(f"Sam at {sam_node} - count of starting locations >= 25: {len(starts)}, starts: {starts}")
