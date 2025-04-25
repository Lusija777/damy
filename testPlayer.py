import unittest
from unittest.mock import patch
from player import Player  # alebo zmeň podľa cesty

class TestPlayer(unittest.TestCase):

    @patch("builtins.input", return_value="Alice")
    def test_get_player_name_valid(self, mocked_input):
        player = Player(1, [], "")
        self.assertEqual(player.name, "Alice")

    @patch("builtins.input", side_effect=["", "   ", "Alice"])
    def test_get_player_name_reprompt_on_invalid(self, mocked_input):
        player = Player(1, [], "")
        self.assertEqual(player.name, "Alice")

    def test_is_valid_name(self):
        player = Player.__new__(Player)  # bypass __init__
        self.assertTrue(player.is_valid_name("Bob", 1, "Alice"))
        self.assertFalse(player.is_valid_name("", 1, "Alice"))
        self.assertFalse(player.is_valid_name("A B", 1, "Alice"))
        self.assertFalse(player.is_valid_name("a"*21, 1, "Alice"))
        self.assertFalse(player.is_valid_name("Alice", 2, "Alice"))  # duplicate

    def test_check_if_old_player_found(self):
        lines = ["Alice 1600\n", "Bob 1500\n"]
        player = Player.__new__(Player)
        player.name = "alice"
        result = player.check_if_old_player(lines)
        self.assertEqual(result, (0, "1600"))

    def test_check_if_old_player_not_found(self):
        lines = ["Bob 1500\n"]
        player = Player.__new__(Player)
        player.name = "Charlie"
        self.assertIsNone(player.check_if_old_player(lines))

    def test_set_pieces_player1(self):
        player = Player.__new__(Player)
        player.pieces = []
        player.set_pieces(1)
        self.assertTrue(all(6 <= p["y"] <= 7 for p in player.pieces))

    def test_set_pieces_player2(self):
        player = Player.__new__(Player)
        player.pieces = []
        player.set_pieces(2)
        self.assertTrue(all(0 <= p["y"] <= 1 for p in player.pieces))

    def test_queen_move_single_capture(self):
        player = Player.__new__(Player)
        player.pieces = [{"type": "q", "x": 2, "y": 2}]
        opponent = [{"x": 3, "y": 3}]
        moves = player.queen_move(2, 2, 1, 1, opponent)
        self.assertIn([[4, 4], [3, 3]], moves)
        self.assertIn([[5, 5], [3, 3]], moves)


    def test_pawn_move_simple_forward(self):
        player = Player.__new__(Player)
        player.pieces = [{"x": 4, "y": 4}]
        move = player.pawn_move(4, 4, 1, -1, [])
        self.assertEqual(move[0], [5, 3])

    def test_pawn_move_capture(self):
        player = Player.__new__(Player)
        player.pieces = [{"x": 2, "y": 2}]
        opponent = [{"x": 3, "y": 3}]
        move = player.pawn_move(2, 2, 1, 1, opponent)
        self.assertEqual(move[0], [4, 4])  # jump over opponent

    def test_update_rating_win(self):
        player = Player.__new__(Player)
        player.rating = [1500, None]
        player.update_rating(1, 1500)
        self.assertGreater(player.rating[1], 1500)

    def test_update_rating_loss(self):
        player = Player.__new__(Player)
        player.rating = [1500, None]
        player.update_rating(-1, 1500)
        self.assertLess(player.rating[1], 1500)

    def test_update_rating_draw(self):
        player = Player.__new__(Player)
        player.rating = [1500, None]
        player.update_rating(0, 1500)
        self.assertEqual(player.rating[1], 1500)

