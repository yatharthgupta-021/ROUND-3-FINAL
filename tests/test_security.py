"""Security-focused unit tests for Find Sam game."""
import unittest
import time
from game import GameManager


def _add_test_puzzles(game):
    """Add test puzzles to the game since custom_map.json may have none."""
    # Use node IDs that exist in the custom map (0-79)
    test_puzzles = {
        5: {"question": "What is 2+2?", "answer": "4", "intel": ""},
        10: {"question": "Capital of France?", "answer": "paris", "intel": ""},
        15: {"question": "Color of the sky?", "answer": "blue", "intel": ""},
    }
    for nid, puzzle in test_puzzles.items():
        if nid in game.nodes:
            game.puzzles[nid] = puzzle


class TestInputValidation(unittest.TestCase):
    def setUp(self):
        self.game = GameManager()
        _add_test_puzzles(self.game)
        self.game.add_team("Alpha")
        self.game.start_game()
        self.game.start_team("Alpha")

    def test_move_invalid_node_type_string(self):
        """target_node must be an integer, not a string."""
        result = self.game.move_team("Alpha", "not_a_number")
        self.assertFalse(result["success"])
        self.assertIn("Invalid", result["message"])

    def test_move_negative_node_id(self):
        """Negative node IDs don't exist in the graph."""
        result = self.game.move_team("Alpha", -1)
        self.assertFalse(result["success"])
        self.assertIn("Invalid", result["message"])

    def test_move_out_of_range_node_id(self):
        """Node IDs beyond the graph should be rejected."""
        result = self.game.move_team("Alpha", 99999)
        self.assertFalse(result["success"])
        self.assertIn("Invalid", result["message"])

    def test_solve_oversized_answer(self):
        """Answers longer than 200 chars should be rejected."""
        puzzle_node = list(self.game.puzzles.keys())[0]
        self.game.teams["Alpha"]["current_node"] = puzzle_node
        self.game.teams["Alpha"]["active_puzzle_node"] = puzzle_node
        self.game.teams["Alpha"]["puzzle_presented_at"] = time.time()

        result = self.game.solve_puzzle("Alpha", "A" * 201)
        self.assertFalse(result["success"])
        self.assertIn("Invalid answer format", result["message"])

    def test_solve_non_string_answer(self):
        """Answer must be a string."""
        puzzle_node = list(self.game.puzzles.keys())[0]
        self.game.teams["Alpha"]["current_node"] = puzzle_node
        self.game.teams["Alpha"]["active_puzzle_node"] = puzzle_node

        result = self.game.solve_puzzle("Alpha", 12345)
        self.assertFalse(result["success"])
        self.assertIn("Invalid answer format", result["message"])


class TestBypassDisabled(unittest.TestCase):
    def setUp(self):
        self.game = GameManager()

    def test_bypass_returns_failure(self):
        """bypass_puzzle should always return failure."""
        result = self.game.bypass_puzzle("AnyTeam")
        self.assertFalse(result["success"])
        self.assertIn("disabled", result["message"].lower())


class TestAntiAIPuzzleTiming(unittest.TestCase):
    def setUp(self):
        self.game = GameManager()
        _add_test_puzzles(self.game)
        self.game.add_team("Alpha")
        self.game.start_game()
        self.game.start_team("Alpha")

    def test_fast_solve_flagged(self):
        """Solving a puzzle in under 5 seconds should create a suspicious flag."""
        # Find a puzzle node and force the team there
        puzzle_nodes = list(self.game.puzzles.keys())
        self.assertTrue(len(puzzle_nodes) > 0, "No puzzles in game")

        puzzle_node = puzzle_nodes[0]
        answer = self.game.puzzles[puzzle_node]["answer"]

        # Force team adjacent to puzzle node
        adj = self.game.adj_list.get(puzzle_node, [])
        if adj:
            self.game.teams["Alpha"]["current_node"] = adj[0]
        else:
            self.game.teams["Alpha"]["current_node"] = puzzle_node

        # Move to the puzzle node (or force it)
        self.game.teams["Alpha"]["current_node"] = puzzle_node
        self.game.teams["Alpha"]["active_puzzle_node"] = puzzle_node
        self.game.teams["Alpha"]["puzzle_presented_at"] = time.time()  # presented NOW

        # Solve immediately (under 5 seconds)
        result = self.game.solve_puzzle("Alpha", answer)
        self.assertTrue(result["success"])

        # Should have a suspicious flag for fast solve
        flags = self.game.teams["Alpha"]["suspicious_flags"]
        self.assertTrue(len(flags) > 0, "Expected suspicious flag for fast solve")
        self.assertEqual(flags[0]["type"], "fast_solve")

    def test_normal_solve_not_flagged(self):
        """Solving a puzzle after 10+ seconds should NOT be flagged."""
        puzzle_nodes = list(self.game.puzzles.keys())
        puzzle_node = puzzle_nodes[0]
        answer = self.game.puzzles[puzzle_node]["answer"]

        self.game.teams["Alpha"]["current_node"] = puzzle_node
        self.game.teams["Alpha"]["active_puzzle_node"] = puzzle_node
        # Simulate puzzle was presented 10 seconds ago
        self.game.teams["Alpha"]["puzzle_presented_at"] = time.time() - 10.0

        result = self.game.solve_puzzle("Alpha", answer)
        self.assertTrue(result["success"])

        flags = self.game.teams["Alpha"]["suspicious_flags"]
        self.assertEqual(len(flags), 0, "Should not flag normal solve time")


class TestAdjacentNodeHiding(unittest.TestCase):
    def setUp(self):
        self.game = GameManager()
        _add_test_puzzles(self.game)
        self.game.add_team("Alpha")
        self.game.start_game()
        self.game.start_team("Alpha")

    def test_eliminated_team_gets_no_adjacent(self):
        """Eliminated teams should not see adjacent nodes."""
        self.game.teams["Alpha"]["is_eliminated"] = True
        view_data = self.game.get_team_view_data("Alpha")
        self.assertEqual(view_data["adjacent_nodes"], [])

    def test_winner_team_gets_no_adjacent(self):
        """Teams that found Sam should not see adjacent nodes."""
        self.game.teams["Alpha"]["found_sam"] = True
        view_data = self.game.get_team_view_data("Alpha")
        self.assertEqual(view_data["adjacent_nodes"], [])

    def test_active_team_gets_adjacent(self):
        """Active teams should see adjacent nodes."""
        view_data = self.game.get_team_view_data("Alpha")
        self.assertTrue(len(view_data["adjacent_nodes"]) > 0)


class TestSuspiciousFlagsInGMView(unittest.TestCase):
    def setUp(self):
        self.game = GameManager()
        _add_test_puzzles(self.game)
        self.game.add_team("Alpha")
        self.game.start_game()
        self.game.start_team("Alpha")

    def test_gm_view_includes_suspicious_flags(self):
        """GM view should include suspicious_flags for each team."""
        # Add a flag manually
        self.game.teams["Alpha"]["suspicious_flags"].append({
            "type": "fast_solve",
            "node": 5,
            "duration": 1.2,
            "timestamp": time.time()
        })

        gm_data = self.game.get_gm_view_data()
        team_data = gm_data["teams"]["Alpha"]
        self.assertIn("suspicious_flags", team_data)
        self.assertEqual(len(team_data["suspicious_flags"]), 1)

    def test_gm_view_includes_solve_times(self):
        """GM view should include solve_times for each team."""
        self.game.teams["Alpha"]["solve_times"].append({
            "node": 5,
            "duration_seconds": 45.2,
            "timestamp": time.time()
        })

        gm_data = self.game.get_gm_view_data()
        team_data = gm_data["teams"]["Alpha"]
        self.assertIn("solve_times", team_data)
        self.assertEqual(len(team_data["solve_times"]), 1)


if __name__ == "__main__":
    unittest.main()
