import unittest
from unittest.mock import MagicMock
from projekt import Program


class TestTimer(unittest.TestCase):
    def test_time_decreases(self):
        program = Program(run=False, load_images=False)
        program.player1.time = 5
        program.on_move = program.player1
        program.do_tick = True
        program.paint_time = MagicMock()
        program.canvas = MagicMock()
        program.canvas.after = MagicMock()

        program.timer()
        self.assertEqual(program.player1.time, 4)

    def test_timeout_triggers_end(self):
        program = Program(run=False, load_images=False)
        program.player1.time = 0
        program.on_move = program.player1
        program.do_tick = True
        program.paint_time = MagicMock()
        program.canvas = MagicMock()
        program.canvas.after = MagicMock()
        Program.set_game_result = MagicMock()

        program.timer()
        Program.set_game_result.assert_called_with(program, -1)
