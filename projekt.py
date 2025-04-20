import tkinter
from PIL import Image, ImageTk
import itertools
from player import Player

class Program:

    def __init__(self):
        players_file = open("players.txt", "a")
        players_file.close()
        players_file = open("players.txt", "r")
        self.players_file_lines = players_file.readlines()
        players_file.close()

        self.square_size = 72
        self.spacer = 10
        game_size = 400

        Program.find_best_players(self)
        self.player1 = Player(1, self.players_file_lines, None)
        self.player2 = Player(2, self.players_file_lines, self.player1.name)
        self.on_move = self.player1
        Player.find_moves(self.player2, self.player1.pieces)
        Player.find_moves(self.player1, self.player2.pieces)

        self.current_move = {"piece": None, "to": None}
        self.moves = []
        self.game_result = None
        self.moving = False
        self.do_tick = True

        root = tkinter.Tk()
        root.title('Checkers')

        self.canvas = tkinter.Canvas(root, height = self.square_size*8 + 2*self.spacer, width = self.square_size*8 + 3*self.spacer+ game_size, bg = "black")

        self.canvas.bind('<ButtonPress-1>', self.click)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.pack(fill = tkinter.BOTH, expand = True)
        

        b_queen, w_queen = self.load_images()
        self.create_win_animation(b_queen, w_queen)
        
        Program.timer(self)
        Program.board(self)
        tkinter.mainloop()


    def load_images(self):
        w_pawn = Image.open('white-pawn.png').resize((self.square_size, self.square_size))
        b_pawn = Image.open('black-pawn.png').resize((self.square_size, self.square_size))
        w_queen = Image.open('white-queen.png').resize((self.square_size, self.square_size))
        b_queen = Image.open('black-queen.png').resize((self.square_size, self.square_size))
        flag = Image.open('flag.png').resize((int(0.3 * self.square_size), int(0.3 * self.square_size)))
        half = Image.open('half.png').resize((int(0.3 * self.square_size), int(0.3 * self.square_size)))
        self.w_pawn = ImageTk.PhotoImage(w_pawn)
        self.b_pawn = ImageTk.PhotoImage(b_pawn)
        self.w_queen = ImageTk.PhotoImage(w_queen)
        self.b_queen = ImageTk.PhotoImage(b_queen)
        self.flag = ImageTk.PhotoImage(flag)
        self.half = ImageTk.PhotoImage(half)

        return b_queen, w_queen


    def create_win_animation(self, b_queen, w_queen):
        self.b_queen_anim = [ImageTk.PhotoImage(b_queen.rotate(15)), self.b_queen,
                             ImageTk.PhotoImage(b_queen.rotate(-15)), self.b_queen]
        self.w_queen_anim = [ImageTk.PhotoImage(w_queen.rotate(15)), self.w_queen,
                             ImageTk.PhotoImage(w_queen.rotate(-15)), self.w_queen]


    def board(self):
        game_size = 360

        notation = self.compute_notation()

        self.canvas.delete("all")
        self.paint_squares()

        self.paint_last_move()

        self.paint_next_move()

        self.generate_pieces_on_canvas()

        self.paint_marking_on_chess_board()

        self.generate_game_report_space(game_size, notation)

        self.generate_best_players_space(game_size)

        self.paint_info_for_on_move_player()

        self.paint_players_rating()

        for i, player in enumerate ([self.player1, self.player2]):
            self.paint_resign_and_flag_button(player)

            self.paint_time(i, player)

        self.end_queens_animation()


    def paint_players_rating(self):
        rating1 = str(self.player1.rating[0])
        rating2 = str(self.player2.rating[0])
        rating1, rating2 = self.reupdate_rating_string_after_end_game(rating1, rating2)
        self.canvas.create_text(self.square_size / 2 + 2 * self.spacer,
                                self.square_size * 8 + 3 * self.spacer + self.square_size / 2,
                                text=f"{self.player1.name} {rating1}", anchor="nw", font='arial 24', fill="white")
        self.canvas.create_text(self.square_size / 2 + 2 * self.spacer, self.spacer,
                                text=f"{self.player2.name} {rating2}", anchor="nw", font='arial 24', fill="white")


    def paint_last_move(self):
        """Highlights the last move made on the board."""
        if not self.moves:
            return

        from_square = self.moves[-1][1]
        to_square = self.moves[-1][2]

        self._highlight_square(from_square, fill="#8a714b")
        self._highlight_square(to_square, fill="#8a714b")


    def paint_next_move(self):
        """Highlights the piece and its possible next moves."""
        if self.current_move["piece"] is None:
            return

        # Paint the current piece
        piece = self.current_move["piece"]
        self._highlight_square((piece["x"], piece["y"]), fill="YellowGreen")

        # Paint available moves
        for move in piece["moves"]:
            self._highlight_move(move[0][0], move[0][1])


    def _highlight_move(self, x, y):
        """Highlights a potential move square with an oval shape."""
        x1 = self.spacer + self.square_size * x + 1 / 3 * self.square_size
        y1 = 2 * self.spacer + self.square_size / 2 + self.square_size * y + 1 / 3 * self.square_size
        x2 = x1 + self.square_size - 2 / 3 * self.square_size
        y2 = y1 + self.square_size - 2 / 3 * self.square_size
        self.canvas.create_oval(x1, y1, x2, y2, fill="YellowGreen", outline="YellowGreen")


    def _highlight_square(self, position, fill):
        """Highlights a board square at a given logical position (x, y)."""
        x, y = position
        x1 = self.spacer + self.square_size * x
        y1 = 2 * self.spacer + self.square_size / 2 + self.square_size * y
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")


    def paint_squares(self):
        farba1, farba2 = "khaki", "saddlebrown"
        for i in range(8):
            f1, f2 = farba1, farba2
            for j in range(8):
                self.canvas.create_rectangle(self.spacer + self.square_size * j,
                                             2 * self.spacer + self.square_size * i + self.square_size / 2,
                                             self.spacer + self.square_size * j + self.square_size,
                                             2 * self.spacer + self.square_size * i + self.square_size + self.square_size / 2,
                                             fill=f1, outline="")
                f1, f2 = f2, f1
            farba1, farba2 = farba2, farba1


    def end_queens_animation(self):
        if self.game_result == 1:
            for image in self.w_queen_anim:
                for piece in self.player1.pieces:
                    if piece["type"] == "q":
                        self.canvas.delete("w_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.create_image(self.spacer + self.square_size * piece["x"] + self.square_size / 2,
                                                 2 * self.spacer + self.square_size * piece["y"] + self.square_size,
                                                 image=image, tag="w_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.update()
                self.canvas.after(300)
        if self.game_result == -1:
            for image in self.b_queen_anim:
                for piece in self.player2.pieces:
                    if piece["type"] == "q":
                        self.canvas.delete("b_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.create_image(self.spacer + self.square_size * piece["x"] + self.square_size / 2,
                                                 2 * self.spacer + self.square_size * piece["y"] + self.square_size,
                                                 image=image, tag="b_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.update()
                self.canvas.after(300)

    def paint_time(self, i, player):
        """Draws the timer rectangle and formatted time text for the player."""
        minutes, seconds = self._format_time(player.time)

        self.canvas.create_rectangle(
            player.timer[0], player.timer[1],
            player.timer[0] + 1.5 * self.square_size,
            player.timer[1] + 0.5 * self.square_size,
            fill="#333333"
        )

        self.canvas.delete(f"timer{i}")
        self.canvas.create_text(
            player.timer[0] + 1.5 * self.spacer - 2, player.timer[1],
            text=f"{minutes}:{seconds}", fill="white", tags=f"timer{i}", anchor="nw", font='arial 24'
        )

    def _format_time(self, time_units):
        """Formats internal time (in tenths of a second) into (MM, SS) strings."""
        total_seconds = time_units // 10
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}", f"{seconds:02}"

    def paint_resign_and_flag_button(self, player):
        """Draws the resign and draw (flag/half-flag) buttons for the player."""
        for name, button in player.buttons.items():
            x1, y1 = button[0]
            x2, y2 = button[1]
            fill_color = button[2]
            image = self.flag if name == "resign" else self.half

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)
            self._draw_centered_image((x1, y1, x2, y2), image)

    def _draw_centered_image(self, rect, image):
        """Draws an image centered within the given rectangle."""
        x1, y1, x2, y2 = rect
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        self.canvas.create_image(center_x, center_y, image=image)


    def reupdate_rating_string_after_end_game(self, rating1_str, rating2_str):
        """Appends rating change (e.g., +30 or -15) to each player's rating string after game ends."""
        if self.game_result is None:
            return rating1_str, rating2_str

        rating1_change = self._format_rating_change(self.player1)
        rating2_change = self._format_rating_change(self.player2)

        return f"{rating1_str} {rating1_change}", f"{rating2_str} {rating2_change}"

    def _format_rating_change(self, player):
        """Returns a string representing the rating change, like '+25' or '-13'."""
        if player.rating[1] is None:
            return ""  # Fallback in case rating wasn't updated properly

        change = player.rating[1] - player.rating[0]
        sign = "+" if change >= 0 else ""
        return f"{sign}{change}"

    def paint_info_for_on_move_player(self):
        self.canvas.delete("on_move")
        if self.game_result is None:
            if self.on_move == self.player2:
                self.canvas.create_oval(2 * self.spacer, 2 * self.spacer, self.square_size / 2, self.square_size / 2,
                                        fill="ForestGreen", outline="", tag="on_move")
            elif self.on_move == self.player1:
                self.canvas.create_oval(2 * self.spacer, self.square_size * 8 + 4 * self.spacer + self.square_size / 2,
                                        self.square_size / 2, self.square_size * 9 + 2 * self.spacer,
                                        fill="ForestGreen", outline="", tag="on_move")

    def generate_best_players_space(self, game_size):
        self.canvas.create_rectangle(self.square_size * 8 + 3 * self.spacer + game_size,
                                     2 * self.spacer + self.square_size / 2,
                                     self.square_size * 8 + 3 * self.spacer + 2 * game_size,
                                     2 * self.spacer + self.square_size, fill="white")
        self.canvas.create_text(self.square_size * 8 + 4 * self.spacer + game_size,
                                3 * self.spacer + self.square_size / 2, text="BEST PLAYERS", anchor="nw",
                                font="arial 12")
        self.canvas.create_rectangle(self.square_size * 8 + 3 * self.spacer + game_size,
                                     2 * self.spacer + self.square_size,
                                     self.square_size * 8 + 3 * self.spacer + 2 * game_size,
                                     2 * self.spacer + 8.5 * self.square_size, fill="white")
        self.canvas.create_text(self.square_size * 8 + 4 * self.spacer + game_size, 3 * self.spacer + self.square_size,
                                anchor="nw", text=self.best_players, font="arial 10")

    def generate_game_report_space(self, game_size, notation):
        self.canvas.create_rectangle(self.square_size * 8 + 2 * self.spacer, 2 * self.spacer + self.square_size / 2,
                                     self.square_size * 8 + 2 * self.spacer + game_size,
                                     2 * self.spacer + self.square_size, fill="white")
        self.canvas.create_text(self.square_size * 8 + 3 * self.spacer, 3 * self.spacer + self.square_size / 2,
                                text="GAME REPORT", anchor="nw", font="arial 12")
        self.canvas.create_rectangle(self.square_size * 8 + 2 * self.spacer, 2 * self.spacer + self.square_size,
                                     self.square_size * 8 + 2 * self.spacer + game_size,
                                     2 * self.spacer + 8.5 * self.square_size, fill="white")
        self.canvas.create_text(self.square_size * 8 + 3 * self.spacer, 3 * self.spacer + self.square_size, anchor="nw",
                                text=notation, font="arial 10")

    def paint_marking_on_chess_board(self):
        """Draws row and column markings on the chessboard."""
        # Colors for alternating row markings
        row_colors = ["khaki", "saddlebrown"]

        # Draw row numbers (8 to 1)
        for i in range(8):
            row_number = 8 - i
            self.canvas.create_text(
                self.spacer + self.square_size * 8 - 5,
                2 * self.spacer + self.square_size / 2 + self.square_size * i,
                text=str(row_number),
                anchor="ne",
                fill=row_colors[i % 2]
            )

        # Draw column letters (a to h)
        col_letters = ["h", "g", "f", "e", "d", "c", "b", "a"]
        for i in range(8):
            self.canvas.create_text(
                self.spacer + self.square_size * (7 - i) + 5,
                2 * self.spacer + self.square_size / 2 + self.square_size * 8,
                text=col_letters[i],
                anchor="sw",
                fill=row_colors[i % 2]
            )

    def generate_pieces_on_canvas(self):
        for piece in self.player1.pieces:
            if piece["type"] == "q":
                self.canvas.create_image(self.spacer + self.square_size * piece["x"] + self.square_size / 2,
                                         2 * self.spacer + self.square_size * piece["y"] + self.square_size,
                                         image=self.w_queen, tag="w_queen" + str(piece["x"]) + str(piece["y"]))
            else:
                self.canvas.create_image(self.spacer + self.square_size * piece["x"] + self.square_size / 2,
                                         2 * self.spacer + self.square_size * piece["y"] + self.square_size,
                                         image=self.w_pawn)
        for piece in self.player2.pieces:
            if piece["type"] == "q":
                self.canvas.create_image(self.spacer + self.square_size * piece["x"] + self.square_size / 2,
                                         2 * self.spacer + self.square_size * piece["y"] + self.square_size,
                                         image=self.b_queen, tag="b_queen" + str(piece["x"]) + str(piece["y"]))
            else:
                self.canvas.create_image(self.spacer + self.square_size * piece["x"] + self.square_size / 2,
                                         2 * self.spacer + self.square_size * piece["y"] + self.square_size,
                                         image=self.b_pawn)

    def compute_notation(self):
        notation = ""
        for i, move in enumerate(self.moves):
            if i % 8 == 0 and i != 0:
                notation += "\n"
            if i % 2 == 0:
                notation += (f"{i // 2 + 1}. {move[5]} ")
            else:
                notation += (f"{move[5]} ")

        if self.game_result is not None:
            if len(notation) > 0:
                notation += "\n"
            notation = self.update_notation_based_on_game_result(notation)
        return notation

    def update_notation_based_on_game_result(self, notation):
        if self.game_result == 1:
            notation += "1 - 0"
        elif self.game_result == 0:
            notation += "1/2 - 1/2"
        elif self.game_result == -1:
            notation += "0 - 1"
        return notation

    def timer(self):
        """Updates the timer for the current player and checks for timeout."""
        if not self.do_tick:
            return

        current_player = self.on_move
        player_index = 0 if current_player == self.player1 else 1

        self.paint_time(player_index, current_player)

        if current_player.time == 0:
            self.handle_game_timeout(current_player)
        else:
            current_player.time -= 1
            self.canvas.after(100, self.timer)

    def handle_game_timeout(self, player):
        """Handles the timeout logic and sets the game result."""
        if player == self.player1:
            Program.set_game_result(self, -1)
        else:
            Program.set_game_result(self, 1)


    def find_square(self, x, y):
        x = (x - self.spacer) // self.square_size
        y = (y - 2*self.spacer - self.square_size/2 ) // self.square_size
        if x >= 0 and x <= 7 and y >= 0 and y <= 7:
            return [x, y]
        else:
            return None

    def motion(self, event):
        self.moving = True
        
    def release(self, event):
        if self.moving:
            self.moving = False
            self.click(event)


    def click(self, event):
        """Handles click events for offering/accepting draws and making moves."""
        # Check if a button was clicked (draw or resign)
        if self.handle_button_click(event):
            return None

        # Find the square clicked on the board
        square = Program.find_square(self, event.x, event.y)
        if square is None:
            self.reset_current_move()
            return None

        # Handle the piece selection or movement
        if self.current_move["piece"] is None:
            self.select_piece(square)
            return None

        # Handle the movement of the selected piece
        self.move_piece(square)


    def handle_button_click(self, event):
        """Handles clicking on any of the buttons (draw, resign, etc.)."""
        for player in [self.player1, self.player2]:
            for name, coordinates in player.buttons.items():
                if self.is_within_bounds(event, coordinates):
                    self.reset_current_move()
                    if name == "draw":
                        self.handle_draw_offer(player)
                    else:
                        self.handle_resignation(player)
                    return True
        return False


    def is_within_bounds(self, event, coordinates):
        """Checks if the click event is within the bounds of a button."""
        return (event.x >= coordinates[0][0] and event.y >= coordinates[0][1] and
                event.x <= coordinates[1][0] and event.y <= coordinates[1][1])

    def handle_draw_offer(self, player):
        """Handles the logic for offering or accepting a draw."""
        if player.offering_draw:
            player.offering_draw = False
            self.reset_draw_buttons()
            Program.board(self)
        else:
            self.offer_or_accept_draw(player)


    def offer_or_accept_draw(self, player):
        """Offers or accepts a draw based on the current game state."""
        if ((player == self.player1 and self.player2.offering_draw) or
                (player == self.player2 and self.player1.offering_draw)):
            Program.set_game_result(self, 0)  # Draw accepted
        else:
            player.offering_draw = True
            self.update_draw_buttons(player)
            Program.board(self)


    def reset_draw_buttons(self):
        """Resets the draw buttons to their default state."""
        self.player2.buttons["draw"][2] = "grey"
        self.player1.buttons["draw"][2] = "grey"

    def update_draw_buttons(self, player):
        """Updates the draw buttons when a player offers a draw."""
        coordinates = player.buttons["draw"]
        coordinates[2] = "maroon"
        if player == self.player1:
            self.player2.buttons["draw"][2] = "navy"
        else:
            self.player1.buttons["draw"][2] = "navy"


    def handle_resignation(self, player):
        """Handles the logic for a player resigning."""
        result = -1 if player == self.player1 else 1
        Program.set_game_result(self, result)


    def reset_current_move(self):
        """Resets the current move data."""
        self.current_move = {"piece": None, "to": None}
        Program.board(self)


    def select_piece(self, square):
        """Selects a piece for the current move."""
        for piece in self.on_move.pieces:
            if [piece["x"], piece["y"]] == square:
                self.current_move["piece"] = piece
                Program.board(self)


    def move_piece(self, square):
        """Handles the movement of a selected piece."""
        for moves in self.current_move["piece"]["moves"]:
            if square == moves[0]:
                self.current_move["to"] = moves
                break

        if self.current_move["to"] is None:
            self.reset_current_move()
            return None

        self.ready_to_move()


    def ready_to_move(self):
        """Makes the move and updates the game state."""
        Program.make_move(self, [
            self.current_move["piece"]["type"],
            [self.current_move["piece"]["x"], self.current_move["piece"]["y"]],
            [self.current_move["to"][0][0], self.current_move["to"][0][1]],
            self.current_move["to"][1] != [None, None],
            self.current_move["to"][0][1] == 7 or self.current_move["to"][0][1] == 0
        ])

        # Decline draw offer after a move
        self.player2.offering_draw = False
        self.player1.offering_draw = False
        self.reset_draw_buttons()

        # Check for game end conditions (no pieces or no available moves)
        self.check_game_end()

        # Switch to the other player's turn
        self.on_move = self.player2 if self.on_move == self.player1 else self.player1
        self.reset_current_move()
        Program.board(self)

    def check_game_end(self):
        """Checks if the game has ended due to no available moves or pieces."""
        opposite_player = self.player2 if self.on_move == self.player1 else self.player1

        if len(opposite_player.pieces) == 0:
            result = -1 if opposite_player == self.player1 else 1
            Program.set_game_result(self, result)
            return

        has_available_move = any(len(piece["moves"]) > 0 for piece in opposite_player.pieces)
        if not has_available_move:
            result = -1 if opposite_player == self.player1 else 1
            Program.set_game_result(self, result)
            return

        self.check_insignificant_moves()

    def check_insignificant_moves(self):
        """Checks for 80 moves with no captures or promotions (stalemate)."""
        number_of_insignificant_moves = 0
        for move in self.moves[::-1]:
            if not move[3] and not move[4]:
                number_of_insignificant_moves += 1
            else:
                break

        if number_of_insignificant_moves >= 80:
            Program.set_game_result(self, 0)


    def make_move(self, move):
        """Executes a move, updates game state, and appends notation."""
        notation = self._generate_notation(move)
        move.append(notation)
        self.moves.append(move)

        self._capture_piece_if_needed()
        self._update_piece_position()
        self._handle_promotion()
        self._refresh_available_moves()


    def _generate_notation(self, move):
        """Creates algebraic notation for a move."""
        i = len(self.moves)
        alphabet = {i: chr(97 + i) for i in range(8)}  # {0: 'a', ..., 7: 'h'}
        notation = "Q" if move[0] == "q" else ""

        pieces = self.player1.pieces if (i % 2) == 0 else self.player2.pieces
        move_possible_by_another = self._is_ambiguous_move(pieces, move)

        if move_possible_by_another or (move[3] and move[0] == "p"):
            notation += alphabet[move[1][0]]

        if move[3]:
            notation += "x"

        notation += alphabet[move[2][0]] + str(8 - move[2][1])

        if move[4]:
            notation += "=Q"

        return notation


    def _is_ambiguous_move(self, pieces, move):
        """Checks if another piece of the same type can also perform the move."""
        for piece in pieces:
            if piece["type"] == move[0] and [piece["x"], piece["y"]] != move[1]:
                if any(move[2] == available_move[0] for available_move in piece["moves"]):
                    return True
        return False


    def _capture_piece_if_needed(self):
        """Removes the opponent's piece if it was captured."""
        opponent = self.player2 if self.on_move == self.player1 else self.player1
        captured_pos = self.current_move["to"][1]

        if captured_pos != [None, None]:
            opponent.pieces = [
                p for p in opponent.pieces if [p["x"], p["y"]] != captured_pos
            ]


    def _update_piece_position(self):
        """Updates the position of the moving piece."""
        to_square = self.current_move["to"][0]
        self.current_move["piece"]["x"] = to_square[0]
        self.current_move["piece"]["y"] = to_square[1]


    def _handle_promotion(self):
        """Promotes a pawn to a queen if it reaches the back rank."""
        y = self.current_move["to"][0][1]
        if y in (0, 7):
            self.current_move["piece"]["type"] = "q"


    def _refresh_available_moves(self):
        """Recalculates legal moves for both players."""
        Player.find_moves(self.player1, self.player2.pieces)
        Player.find_moves(self.player2, self.player1.pieces)


    def find_best_players(self):
        all_players = {}
        for line in self.players_file_lines:
            name_in_line, rating_in_line = line.strip().split(" ")
            all_players[name_in_line] = rating_in_line

        all_players = dict(sorted(all_players.items(), key = lambda item: item[1], reverse = True))

        if len(all_players) > 30:
            all_players = dict(itertools.islice(all_players.items(),30))

        self.best_players = ""
        i = 1
        for name,rating in all_players.items():
            self.best_players += (f"{i}. {name} {rating}\n")
            i += 1


    def set_game_result(self, result):
        self.game_result = result
        # reset default values on the board
        self.current_move = {"piece": None, "to": None}
        self.player2.buttons["draw"][2] = "grey"
        self.player1.buttons["draw"][2] = "grey"

        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
        self.do_tick = False

        self.write_game_to_file()

        Player.update_rating(self.player1, result, self.player2.rating[0])
        Player.update_rating(self.player2, result*(-1), self.player1.rating[0])

        self.write_ratings_to_file()

        Program.board(self)

    def write_ratings_to_file(self):
        for player in [self.player1, self.player2]:
            if player.identifier is None:
                self.players_file_lines.append(f"{player.name} {player.rating[1]}\n")
            else:
                self.players_file_lines[player.identifier] = (f"{player.name} {player.rating[1]}\n")
        players_file = open("players.txt", "w")
        players_file.writelines(self.players_file_lines)
        players_file.close()

    def write_game_to_file(self):
        game_file = open("game.txt", "w")
        # two moves in one line (for each player)
        for i, move in enumerate(self.moves):
            if i % 2 == 0:
                game_file.write(f"{i // 2 + 1}. {move[5]}")
            else:
                game_file.write(f" {move[5]}\n")
        notation = ""
        if len(self.moves) > 0:
            notation += "\n"
        notation = self.update_notation_based_on_game_result(notation)
        game_file.write(notation)
        game_file.close()


Program()
    


