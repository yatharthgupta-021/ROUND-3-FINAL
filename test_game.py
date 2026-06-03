import unittest
import time
from game import GameManager

class TestFindSamGame(unittest.TestCase):
    def setUp(self):
        self.game = GameManager()

    def test_default_map_setup(self):
        self.assertEqual(len(self.game.nodes), 80)
        self.assertEqual(self.game.nodes[0]["x"], 0)
        self.assertEqual(self.game.nodes[0]["y"], 0)
        self.assertEqual(self.game.nodes[45]["name"], "Backstage")

    def test_adjacent_nodes(self):
        # Node 15 is Piscine Swimming Pool Entry at x=8, y=1.
        # Its cardinally adjacent nodes in the main loop are 14 and 16.
        adj = self.game.get_adjacent_nodes(15)
        self.assertIn(14, adj)
        self.assertIn(16, adj)
        self.assertEqual(len(adj), 2)

    def test_add_team(self):
        # Sam is at default 53
        self.assertTrue(self.game.add_team("Alpha"))
        start_node = self.game.teams["Alpha"]["current_node"]
        
        # Verify start node is within grid range
        self.assertTrue(0 <= start_node < 80)
        
        # Verify shortest path from Sam (start_node 53) is at least 25
        dist = self.game.get_shortest_path_distance(start_node, 53)
        self.assertTrue(dist >= 25)
        self.assertEqual(self.game.teams["Alpha"]["tickets"], 50)
        
        # Duplicate name
        self.assertFalse(self.game.add_team("Alpha"))

    def test_game_states_and_movement(self):
        self.game.add_team("Alpha")
        start_node = self.game.teams["Alpha"]["current_node"]
        adj = self.game.get_adjacent_nodes(start_node)
        target = adj[0]
        
        # Move before start (should fail since status is setup)
        res = self.game.move_team("Alpha", target)
        self.assertFalse(res["success"])
        
        # Start game
        self.game.start_game()
        self.assertEqual(self.game.game_status, "active")

        # Find a non-adjacent node
        non_adjacent = [i for i in range(80) if i not in adj and i != start_node][0]
        res = self.game.move_team("Alpha", non_adjacent)
        self.assertFalse(res["success"])

        # Move to adjacent (should succeed)
        res = self.game.move_team("Alpha", target)
        self.assertTrue(res["success"])
        self.assertEqual(self.game.teams["Alpha"]["current_node"], target)
        self.assertEqual(self.game.teams["Alpha"]["tickets"], 49)

    def test_win_condition(self):
        # Sam is static at node 53
        self.game.sam_start_node = 53
        self.game.sam_current_node = 53
        self.game.sam_static = True
        self.game.add_team("Alpha")
        
        # Force team position adjacent to Sam (node 52 connects to 53)
        self.game.teams["Alpha"]["current_node"] = 52
        self.game.start_game()

        # Alpha moves from 52 to 53 - should fail due to clearance
        res = self.game.move_team("Alpha", 53)
        self.assertFalse(res["success"])
        self.assertIn("TIMELINE GLITCH", res["message"])
        
        # Mock solving 3 puzzles to gain clearance level 3
        self.game.teams["Alpha"]["puzzles_solved"] = [5, 10, 15]
        
        # Try again - should succeed
        res = self.game.move_team("Alpha", 53)
        self.assertTrue(res["success"])
        self.assertTrue(res.get("found_sam", False))
        self.assertTrue(self.game.teams["Alpha"]["found_sam"])
        self.assertEqual(len(self.game.winners), 1)
        self.assertEqual(self.game.winners[0]["team_name"], "Alpha")

    def test_clue_trigger_and_puzzle_decryption(self):
        self.game.add_team("Alpha")
        # Force position near a puzzle (Node 5 is Casino Square Library)
        self.game.teams["Alpha"]["current_node"] = 4
        
        # Load puzzle on node 5 (already loaded by setup_story_puzzles)
        self.game.start_game()

        # Move to node 5
        res = self.game.move_team("Alpha", 5)
        self.assertTrue(res["success"])
        self.assertTrue(res.get("riddle_triggered", False))
        self.assertEqual(self.game.teams["Alpha"]["active_puzzle_node"], 5)

        # Solve with wrong answer
        solve_res = self.game.solve_puzzle("Alpha", "wrong")
        self.assertFalse(solve_res["success"])
        self.assertEqual(self.game.teams["Alpha"]["active_puzzle_node"], 5)

        # Solve with correct answer
        solve_res = self.game.solve_puzzle("Alpha", "potter")
        self.assertTrue(solve_res["success"])
        self.assertIn(5, self.game.teams["Alpha"]["puzzles_solved"])
        self.assertIsNone(self.game.teams["Alpha"]["active_puzzle_node"])
        # Clues should be added
        intel_clues = [c for c in self.game.teams["Alpha"]["clues_received"] if c["type"] == "intel"]
        self.assertEqual(len(intel_clues), 3)
        for clue in intel_clues:
            self.assertIn("Decrypted Intel", clue["text"])

if __name__ == "__main__":
    unittest.main()
