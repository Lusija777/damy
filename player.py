class Player:
    def __init__(self, i, players_file_lines, player1_name):
        self.SQUARE_SIZE = 72
        self.SPACER = 10
        self.RATING_MULTIPLIER = 32
        self.pieces = []
        self.offering_draw = False
        self.time = 6000

        self.name = self.get_player_name(i, player1_name)
        self.set_pieces(i)
        self.set_buttons_and_timer(i)
        self.set_directions(i)

        result = self.check_if_old_player(players_file_lines)

        if result is not None:
            identifier, rating = result
            self.rating = [int(rating), None]
            self.identifier = identifier
        else:
            self.rating = [1500, None]
            self.identifier = None

    def get_player_name(self, player_index, player1_name):
        suffix = "st" if player_index == 1 else "nd"
        prompt = f"Enter the name of the {player_index}{suffix} player:"
        name = input(prompt)

        while not self.is_valid_name(name, player_index, player1_name):
            print("The name cannot be empty, contain spaces, exceed 20 characters, or duplicate of other player name.")
            name = input(prompt)

        return name

    def is_valid_name(self, name, player_index, player1_name):
        if not name or " " in name or len(name) > 20:
            return False
        if player_index == 2 and name.lower() == player1_name.lower():
            return False
        return True

    def check_if_old_player(self, players_file_lines):
        for identifier, line in enumerate(players_file_lines):
            if " " not in line:
                continue
            name, rating = line.strip().split(" ")
            if self.name.lower() == name.lower():
                return identifier, rating
        return None

    def set_pieces(self, player_index):
        rows = range(6, 8) if player_index == 1 else range(2)
        for x in range(8):
            for y in rows:
                if (x + y) % 2 == 1:
                    self.pieces.append({"type": "p", "x": x, "y": y})

    def set_buttons_and_timer(self, player_index):
        if player_index == 1:
            y_offset = self.SQUARE_SIZE * 8 + 3 * self.SPACER
        else:
            y_offset = self.SPACER - self.SQUARE_SIZE / 2

        self.buttons = {
            "draw": [[5.5 * self.SQUARE_SIZE - self.SPACER, y_offset + self.SQUARE_SIZE / 2],
                     [6 * self.SQUARE_SIZE - self.SPACER, y_offset + self.SQUARE_SIZE], "grey", .8],
            "resign": [[6 * self.SQUARE_SIZE, y_offset + self.SQUARE_SIZE / 2],
                       [6.5 * self.SQUARE_SIZE, y_offset + self.SQUARE_SIZE], "grey", .8],
        }

        self.timer = [6.5 * self.SQUARE_SIZE + self.SPACER, y_offset + self.SQUARE_SIZE / 2]

    def set_directions(self, player_index):
        self.directions = [[-1, -1], [1, -1]] if player_index == 1 else [[-1, 1], [1, 1]]

    def find_moves(self, opponent_pieces):
        """Find all valid moves for each of this player's pieces."""
        for piece in self.pieces:
            piece["moves"] = []

            if piece["type"] == "q":
                for dx, dy in [[-1, 1], [1, 1], [-1, -1], [1, -1]]:
                    moves = self.queen_move(piece["x"], piece["y"], dx, dy, opponent_pieces)
                    piece["moves"].extend(moves)
            else:
                for dx, dy in self.directions:
                    move = self.pawn_move(piece["x"], piece["y"], dx, dy, opponent_pieces)
                    if move:
                        piece["moves"].append(move)

    def pawn_move(self, x, y, dx, dy, opponent_pieces, first_call=True):
        """Check single-step or capture move for a pawn."""
        target_x, target_y = x + dx, y + dy
        if not self.is_on_board(target_x, target_y):
            return []

        if self.has_piece_at(target_x, target_y, self.pieces):
            return []

        if self.has_piece_at(target_x, target_y, opponent_pieces):
            if first_call:
                # Try jumping over opponent piece
                return self.pawn_move(target_x, target_y, dx, dy, opponent_pieces, False)
            else:
                return []
        else:
            landing = [target_x, target_y]
            source = [None, None] if first_call else [x, y]
            return [landing, source]

    def queen_move(self, x, y, dx, dy, opponent_pieces):
        """Get all valid diagonal moves for a queen."""
        moves = []
        jumped = False
        captured = None

        for i in range(1, 8):
            tx, ty = x + dx * i, y + dy * i
            if not self.is_on_board(tx, ty):
                break

            if self.has_piece_at(tx, ty, self.pieces):
                break

            if self.has_piece_at(tx, ty, opponent_pieces):
                if not jumped:
                    jumped = True
                    captured = [tx, ty]
                    continue
                else:
                    break  # Cannot jump over two pieces

            moves.append([[tx, ty], captured])

        return moves

    def is_on_board(self, x, y):
        """Return True if the coordinates are within the board."""
        return 0 <= x <= 7 and 0 <= y <= 7

    def has_piece_at(self, x, y, piece_list):
        """Return True if any piece in the list occupies (x, y)."""
        return any(piece["x"] == x and piece["y"] == y for piece in piece_list)

    def update_rating(self, gameResult, other_player_rating):
        # elo - rating calculation
        expected_result_player = 1 / (1 + 10 ** ((other_player_rating - self.rating[0]) / 400))

        if gameResult == 1:
            self.rating[1] = round(self.rating[0] + self.RATING_MULTIPLIER * (1 - expected_result_player))
        elif gameResult == 0:
            self.rating[1] = round(self.rating[0] + self.RATING_MULTIPLIER * ((1 / 2) - expected_result_player))
        else:
            self.rating[1] = round(self.rating[0] + self.RATING_MULTIPLIER * (0 - expected_result_player))
