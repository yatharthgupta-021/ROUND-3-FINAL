import sys
sys.path.append('/Users/sahana/.gemini/antigravity/scratch/find_sam_game')
from game import GameManager

gm = GameManager()
import json
print(json.dumps(gm.get_gm_view_data()["map_nodes"]))
