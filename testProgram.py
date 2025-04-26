import unittest
from unittest.mock import patch, mock_open, MagicMock
from projekt import Program

class TestProgram(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="Player1 1255\nPlayer2 1548\n")
    @patch("tkinter.Tk")  # Mock tkinter so GUI neotvorí pri inicializácii
    @patch("projekt.Player")
    def test_initialization(mock_player, mock_file, mock_tk, mock_loop):
        mock_player.return_value = MagicMock()

        with patch.object(Program, "create_win_animation"):  # vynecháme aj animácie
            p = Program(run=False, load_images=False)
            assert isinstance(p.players_file_lines, list)
            assert len(p.players_file_lines) == 2

    def test_highlight_move_coordinates(self):
        # Vytvor dummy objekt bez tkinter
        program = Program.__new__(Program)
        program.SQUARE_SIZE = 72
        program.SPACER = 10
        program.canvas = MagicMock()

        # Zavolaj highlight_move a skontroluj, či create_oval bol zavolaný
        program._highlight_move(2, 3)
        program.canvas.create_oval.assert_called_once()

    def test_paint_last_move_no_moves(self):
        program = Program.__new__(Program)
        program.moves = []
        program._highlight_square = MagicMock()
        program.canvas = MagicMock()

        # Nemalo by sa nič vykresliť
        program.paint_last_move()
        program._highlight_square.assert_not_called()

    def test_paint_last_move_with_move(self):
        program = Program.__new__(Program)
        program.moves = [["p", (1, 2), (3, 4)]]
        program._highlight_square = MagicMock()
        program.canvas = MagicMock()

        program.paint_last_move()
        program._highlight_square.assert_any_call((1, 2), fill="#8a714b")
        program._highlight_square.assert_any_call((3, 4), fill="#8a714b")
        self.assertEqual(program._highlight_square.call_count, 2)

    @patch("projekt.tkinter.Tk")
    def test_compute_notation_returns_correct_format(self, mock_tk):
        program = Program(run=False, load_images=False)
        program.moves = []


        program.add_to_notation_history("de3")
        program.moves.append(["p", [3, 6], [4, 5], False, False, "de3"])
        program.add_to_notation_history("ed6")
        program.moves.append(['p', [4, 1], [3, 2], False, False, "ed6"])

        program.game_result = 1
        program.add_to_notation_history("d4")
        program.moves.append(['p', [4, 5], [3, 4], False, False, "d4"])

        notation = program.notation

        assert "1. de3 ed6" in notation
        assert "2. d4" in notation
        assert "1 - 0" in notation

    def test_format_time_returns_correct_values(self):
        program = Program(run=False, load_images=False)
        assert program._format_time(125) == ("00", "12")  # 12.5 sekundy
        assert program._format_time(600) == ("01", "00")  # 60.0 sekundy
        assert program._format_time(0) == ("00", "00")

    @patch("projekt.tkinter.Tk")
    def test_reupdate_rating_string_after_end_game(self, mock_tk):
        program = Program(run=False)
        program.game_result = -1
        program.player1.rating = [1500, 1470]
        program.player2.rating = [1500, 1530]
        r1, r2 = program.reupdate_rating_string_after_end_game("1500", "1500")
        assert r1 == "1500 -30"
        assert r2 == "1500 +30"

    @patch("projekt.tkinter.Tk")
    def test_format_rating_change_positive_and_negative(self, mock_tk):
        program = Program(run=False, load_images=False)

        player1 = MagicMock()
        player1.rating = [1200, 1234]
        assert program._format_rating_change(player1) == "+34"

        player2 = MagicMock()
        player2.rating = [1200, 1188]
        assert program._format_rating_change(player2) == "-12"

    @patch("projekt.tkinter.Tk")
    def test_highlight_square_draws_rectangle(self, mock_tk):
        mock_canvas = MagicMock()
        program = Program(run=False)
        program.canvas = mock_canvas

        program._highlight_square((2, 3), fill="red")
        mock_canvas.create_rectangle.assert_called()

    def test_find_square_inside_bounds(self):
        program = Program(run=False, load_images=False)
        program.SQUARE_SIZE = 60
        program.SPACER = 10
        result = program.find_square(100, 200)
        self.assertIsInstance(result, list)

    def test_find_square_outside_bounds(self):
        program = Program(run=False, load_images=False)
        program.SQUARE_SIZE = 60
        program.SPACER = 10
        result = program.find_square(-20, 800)
        self.assertIsNone(result)

    def test_handle_button_click_draw(self):
        program = Program(run=False, load_images=False)
        program.player1 = MagicMock()
        program.player2 = MagicMock()
        program.player1.buttons = {"draw": [[0, 0], [50, 50], "grey"]}
        program.player2.buttons = {"draw": [[0, 0], [50, 50], "grey"]}
        program.is_within_bounds = MagicMock(return_value=True)
        program.handle_draw_offer = MagicMock()
        program.reset_current_move = MagicMock()

        event = MagicMock()
        result = program.handle_button_click(event)

        self.assertTrue(result)
        program.handle_draw_offer.assert_called()

    def test_select_piece(self):
        program = Program(run=False, load_images=False)
        program.player1 = MagicMock()
        program.player1.pieces = [{"x": 1, "y": 2, "type": "p", "moves": []}]
        program.on_move = program.player1
        program.current_move = {"piece": None, "to": None}
        Program.board = MagicMock()

        program.select_piece([1, 2])
        self.assertEqual(program.current_move["piece"]["x"], 1)

    def test_game_end_no_pieces(self):
        program = Program(run=False, load_images=False)
        program.on_move = program.player1
        program.player2.pieces = []
        Program.set_game_result = MagicMock()
        Program.board = MagicMock()

        program.check_game_end()
        Program.set_game_result.assert_called_with(program, 1)

    def test_game_end_no_moves(self):
        program = Program(run=False, load_images=False)
        program.on_move = program.player1
        program.player2.pieces = [{"x": 1, "y": 2, "moves": []}]
        Program.set_game_result = MagicMock()
        Program.board = MagicMock()

        program.check_game_end()
        Program.set_game_result.assert_called_with(program, 1)

    def test_stalemate_80_moves(self):
        program = Program(run=False, load_images=False)
        program.current_move = {'piece': {'moves': [[[4, 5], [None, None]], [[6, 5], [None, None]]], 'type': 'p', 'x': 5, 'y': 6}, 'to': [[4, 5], [None, None]]}
        for i in range(80):
            program.make_move(['p', [4, 5], [3, 4], False, False])
        Program.set_game_result = MagicMock()
        program.board = MagicMock()

        program.check_80_insignificant_moves()
        Program.set_game_result.assert_called_with(program, 0)

    def test_make_move_adds_to_move_list(self):
        program = Program(run=False, load_images=False)
        program.current_move = {
            "piece": {"x": 0, "y": 1, "type": "p", "moves": [[[0, 2], [None, None]]]},
            "to": [[0, 2], [None, None]]
        }
        program.on_move = program.player1
        program.moves = []
        move = ["p", [0, 1], [0, 2], False, False]

        program._generate_notation = MagicMock(return_value="e4")
        program._capture_piece_if_needed = MagicMock()
        program._update_piece_position = MagicMock()
        program._handle_promotion = MagicMock()
        program._refresh_available_moves = MagicMock()
        program.board = MagicMock()

        program.make_move(move)
        self.assertEqual(len(program.moves), 1)
        self.assertEqual(program.moves[0][5], "e4")


    def test_find_best_players_limit_to_30(self):
        program = Program(run=False, load_images=False)
        program.players_file_lines = [f"Player{i} {1500 + i}" for i in range(50)]
        program.find_best_players()

        self.assertTrue(program.best_players.startswith("1. Player49"))
        self.assertIn("30. Player20", program.best_players)
        self.assertNotIn("Player19", program.best_players)

    def test_1set_game_result_logic(self):
        program = Program(run=False, load_images=False)
        program.canvas = MagicMock()
        program.player1 = MagicMock()
        program.player2 = MagicMock()
        program.player1.buttons = {"draw": [[0, 0], [50, 50], "grey"]}
        program.player2.buttons = {"draw": [[0, 0], [50, 50], "grey"]}
        program.current_move = {"piece": None, "to": None}
        program.write_game_to_file = MagicMock()
        program.write_ratings_to_file = MagicMock()
        Program.board = MagicMock()

        program.set_game_result(1)

        self.assertEqual(program.game_result, 1)
        self.assertFalse(program.do_tick)
        program.write_game_to_file.assert_called()
        program.write_ratings_to_file.assert_called()
        Program.board.assert_called()

if __name__ == "__main__":
    unittest.main()
