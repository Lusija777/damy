import tkinter
from PIL import Image, ImageTk
import itertools
from player import Player

class Program:
    BOUND_OF_GAME_REPORT = 8

    def __init__(self, run=True, load_images = True):
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
        self.notation = ""
        self.number_of_insignificant_moves = 0

        root = tkinter.Tk()
        root.title('Checkers')

        self.canvas = tkinter.Canvas(root, height = self.square_size*8 + 2*self.spacer, width = self.square_size*8 + 3*self.spacer+ game_size, bg = "black")

        self.canvas.bind('<ButtonPress-1>', self.click)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.pack(fill = tkinter.BOTH, expand = True)
        
        if load_images:
            b_queen, w_queen = self.load_images()
            self.create_win_animation(b_queen, w_queen)

        if run:
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

        self.canvas.delete("all")
        self.paint_squares()

        self.paint_last_move()

        self.paint_next_move()

        self.generate_pieces_on_canvas()

        self.paint_marking_on_chess_board()

        self.generate_game_report_space(game_size)

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
        def animate_queens(pieces, images, tag_prefix):
            for image in images:
                for piece in pieces:
                    if piece["type"] == "q":
                        tag = f"{tag_prefix}_queen{piece['x']}{piece['y']}"
                        x = self.spacer + self.square_size * piece["x"] + self.square_size / 2
                        y = 2 * self.spacer + self.square_size * piece["y"] + self.square_size

                        self.canvas.delete(tag)
                        self.canvas.create_image(x, y, image=image, tag=tag)
                        self.canvas.update()
                self.canvas.after(300)

        if self.game_result == 1:
            animate_queens(self.player1.pieces, self.w_queen_anim, "w")
        elif self.game_result == -1:
            animate_queens(self.player2.pieces, self.b_queen_anim, "b")

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
                                        fill="ForestGreen", outline="", tags="on_move")
            elif self.on_move == self.player1:
                self.canvas.create_oval(2 * self.spacer, self.square_size * 8 + 4 * self.spacer + self.square_size / 2,
                                        self.square_size / 2, self.square_size * 9 + 2 * self.spacer,
                                        fill="ForestGreen", outline="", tags="on_move")

    def generate_best_players_space(self, game_size):
        self.generate_side_panel("BEST PLAYERS", self.best_players, 3 * self.spacer + game_size, game_size)

    def generate_game_report_space(self, game_size):
        self.generate_side_panel("GAME REPORT", self.notation, 2 * self.spacer, game_size)


    def generate_side_panel(self, title, content, x_offset, game_size):
        left = self.square_size * 8 + x_offset
        right = left + game_size

        self.canvas.create_rectangle(left, 2 * self.spacer + self.square_size / 2,
                                     right, 2 * self.spacer + self.square_size, fill="white")
        self.canvas.create_text(left + self.spacer,
                                3 * self.spacer + self.square_size / 2,
                                text=title, anchor="nw", font="arial 12")

        self.canvas.create_rectangle(left, 2 * self.spacer + self.square_size,
                                     right, 2 * self.spacer + 8.5 * self.square_size, fill="white")
        self.canvas.create_text(left + self.spacer,
                                3 * self.spacer + self.square_size,
                                anchor="nw", text=content, font="arial 10")

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
        col_letters = [chr(i) for i in range(ord("h"), ord("a") - 1, -1)]
        for i in range(8):
            self.canvas.create_text(
                self.spacer + self.square_size * (7 - i) + 5,
                2 * self.spacer + self.square_size / 2 + self.square_size * 8,
                text=col_letters[i],
                anchor="sw",
                fill=row_colors[(i+1) % 2]
            )

    def generate_pieces_on_canvas(self):
        piece_parameters = [(self.player1, self.w_pawn, self.w_queen, "w"), (self.player2, self.b_pawn, self.b_queen, "b")]

        for player, pawn_img, queen_img, queen_tag_prefix in piece_parameters:
            for piece in player.pieces:
                if piece["type"] == "q":
                    tag = f"{queen_tag_prefix}_queen{piece['x']}{piece['y']}"
                    image = queen_img

                else:
                    tag = ""
                    image = pawn_img

                x_pos = self.spacer + self.square_size * piece["x"] + self.square_size / 2
                y_pos = 2 * self.spacer + self.square_size * piece["y"] + self.square_size
                self.canvas.create_image(x_pos, y_pos, image=image, tag=tag)


    def add_to_notation_history(self, new_move_notation):
        lenght_moves = len(self.moves)

        if lenght_moves % self.BOUND_OF_GAME_REPORT == 0 and lenght_moves != 0:
            self.notation += "\n"

        if lenght_moves % 2 == 0:
            self.notation += f"{lenght_moves // 2 + 1}. "

        self.notation += new_move_notation + " "

        if self.game_result is not None:
            self.update_notation_based_on_game_result()

    def update_notation_based_on_game_result(self):
        match self.game_result:
            case 1:
                self.notation += "1 - 0"
            case 0:
                self.notation += "1/2 - 1/2"
            case -1:
                self.notation += "0 - 1"

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
        if 0 <= x <= 7 and 0 <= y <= 7:
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

        if self.handle_button_click(event):
            return None

        square = Program.find_square(self, event.x, event.y)
        if square is None:
            self.reset_current_move()
            return None

        if self.current_move["piece"] is None:
            self.select_piece(square)
            return None

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
        return (event.x >= coordinates[0][0] and event.y >= coordinates[0][1] and
                event.x <= coordinates[1][0] and event.y <= coordinates[1][1])

    def handle_draw_offer(self, player):
        if player.offering_draw:
            player.offering_draw = False
            self.reset_draw_buttons()
            Program.board(self)
        else:
            self.offer_or_accept_draw(player)


    def offer_or_accept_draw(self, player):
        if ((player == self.player1 and self.player2.offering_draw) or
                (player == self.player2 and self.player1.offering_draw)):
            Program.set_game_result(self, 0)  # Draw accepted
        else:
            player.offering_draw = True
            self.update_draw_buttons(player)
            Program.board(self)


    def reset_draw_buttons(self):
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
        result = -1 if player == self.player1 else 1
        Program.set_game_result(self, result)


    def reset_current_move(self):
        self.current_move = {"piece": None, "to": None}
        Program.board(self)


    def select_piece(self, square):
        for piece in self.on_move.pieces:
            if [piece["x"], piece["y"]] == square:
                self.current_move["piece"] = piece
                Program.board(self)


    def move_piece(self, square):
        for moves in self.current_move["piece"]["moves"]:
            if square == moves[0]:
                self.current_move["to"] = moves
                break

        if self.current_move["to"] is None:
            self.reset_current_move()
            return None

        self.ready_to_move()


    def ready_to_move(self):
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
        self.on_move = self.get_opponent_player()
        self.reset_current_move()

    def get_opponent_player(self):
        return self.player2 if self.on_move == self.player1 else self.player1

    def check_game_end(self):
        opponent = self.get_opponent_player()

        if len(opponent.pieces) == 0:
            result = -1 if opponent == self.player1 else 1
            Program.set_game_result(self, result)
            return

        has_available_move = any(len(piece["moves"]) > 0 for piece in opponent.pieces)
        if not has_available_move:
            result = -1 if opponent == self.player1 else 1
            Program.set_game_result(self, result)
            return

        self.check_80_insignificant_moves()

    def check_80_insignificant_moves(self):
        if self.number_of_insignificant_moves >= 80:
            Program.set_game_result(self, 0)


    def make_move(self, move):
        """Executes a move, updates game state, and appends notation."""
        notation = self._generate_notation(move)
        move.append(notation)
        self.add_to_notation_history(notation)

        self.moves.append(move)
        if not move[3] and not move[4]:
            self.number_of_insignificant_moves += 1

        self._capture_piece_if_needed()
        self._update_piece_position()
        self._handle_promotion()
        self._refresh_available_moves()


    def _generate_notation(self, move):
        length = len(self.moves)
        alphabet = {i: chr(97 + i) for i in range(8)}  # {0: 'a', ..., 7: 'h'}
        notation = "Q" if move[0] == "q" else ""

        pieces = self.player1.pieces if (length % 2) == 0 else self.player2.pieces
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
        for piece in pieces:
            if piece["type"] == move[0] and [piece["x"], piece["y"]] != move[1]:
                if any(move[2] == available_move[0] for available_move in piece["moves"]):
                    return True
        return False


    def _capture_piece_if_needed(self):
        """Removes the opponent's piece if it was captured."""
        opponent = self.get_opponent_player()
        captured_pos = self.current_move["to"][1]

        if captured_pos != [None, None]:
            opponent.pieces = [
                p for p in opponent.pieces if [p["x"], p["y"]] != captured_pos
            ]


    def _update_piece_position(self):
        to_square = self.current_move["to"][0]
        self.current_move["piece"]["x"] = to_square[0]
        self.current_move["piece"]["y"] = to_square[1]


    def _handle_promotion(self):
        y = self.current_move["to"][0][1]
        if y in (0, 7):
            self.current_move["piece"]["type"] = "q"


    def _refresh_available_moves(self):
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
        for i, (name, rating) in enumerate(all_players.items()):
            self.best_players += (f"{i + 1}. {name} {rating}\n")

    def set_game_result(self, result):
        self.game_result = result
        # reset default values on the board
        self.reset_current_move()
        self.reset_draw_buttons()

        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
        self.do_tick = False

        self.update_notation_based_on_game_result()

        Player.update_rating(self.player1, result, self.player2.rating[0])
        Player.update_rating(self.player2, result*(-1), self.player1.rating[0])

        Program.board(self)

        self.write_game_to_file()
        self.write_ratings_to_file()


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
        game_file.write(self.notation)
        game_file.close()


Program()
    


