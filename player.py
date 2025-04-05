class Player:
    def __init__(self, i, players_file_lines, player1_name):
        self.square_size = 72
        self.spacer = 10
        self.pieces = []

        # sending player_name_1 to make sure not duplicate names playing together
        self.initialize_player(i, player1_name)

        identifier, is_new_player = self.check_if_old_player(players_file_lines)
        if is_new_player:
            self.rating = [1500, None]
            self.identifier = identifier + 1

        self.offering_draw = False
        self.time = 6000

    def check_if_old_player(self, players_file_lines):
        is_new_player = True
        identifier = 0
        for identifier, line in enumerate(players_file_lines):
            if " " not in line:
                continue
            name_in_line, rating_in_line = line.strip().split(" ")
            rating_in_line = int(rating_in_line)
            if self.name.lower() == name_in_line.lower():
                self.rating = [rating_in_line, None]
                self.identifier = identifier
                is_new_player = False
                break
        return identifier, is_new_player

    def initialize_player(self, i, player1_name):
        if i == 1:
            for k in range(8):
                for j in range(6, 8):
                    if (k % 2) == 1 and (j % 2) == 0:
                        self.pieces.append({"type": "p", "x": k, "y": j})
                    elif (k % 2) == 0 and (j % 2) == 1:
                        self.pieces.append({"type": "p", "x": k, "y": j})

            self.name = input(f"Enter the name of the {i}st player:")
            while self.name == "" or " " in self.name or len(self.name) > 20:
                print("The name cannot be empty, cannot contain a space and cannot contain more than 20 characters.")
                self.name = input(f"Enter the name of the {i}st player:")
            self.buttons = {
                "draw": [[5.5 * self.square_size - self.spacer,
                          self.square_size * 8 + 3 * self.spacer + self.square_size / 2],
                         [6 * self.square_size - self.spacer, self.square_size * 9 + 3 * self.spacer], "grey", .8],
                "resign": [[6 * self.square_size, self.square_size * 8 + 3 * self.spacer + self.square_size / 2],
                           [6.5 * self.square_size, self.square_size * 9 + 3 * self.spacer], "grey", .8],
            }
            self.timer = [6.5 * self.square_size + self.spacer,
                          self.square_size * 8 + 3 * self.spacer + self.square_size / 2]
            self.directions = [[-1, -1], [1, -1]]
        else:
            for k in range(8):
                for j in range(2):
                    if (k % 2) == 1 and (j % 2) == 0:
                        self.pieces.append({"type": "p", "x": k, "y": j})
                    elif (k % 2) == 0 and (j % 2) == 1:
                        self.pieces.append({"type": "p", "x": k, "y": j})

            self.name = input(f"Enter the name of the {i}nd player:")
            while self.name == "" or " " in self.name or self.name == player1_name or len(self.name) > 20:
                print(
                    "The name cannot be empty, cannot contain a space, cannot play with yourself, and cannot contain more than 20 characters.")
                self.name = input(f"Enter the name of the {i}nd player:")
            self.buttons = {
                "draw": [[5.5 * self.square_size - self.spacer, self.spacer],
                         [6 * self.square_size - self.spacer, self.spacer + self.square_size / 2], "grey", .8],
                "resign": [[6 * self.square_size, self.spacer],
                           [6.5 * self.square_size, self.spacer + self.square_size / 2], "grey", .8],
            }
            self.timer = [6.5 * self.square_size + self.spacer, self.spacer]
            self.directions = [[-1, 1], [1, 1]]

    def find_moves(self, other_player_pieces):
        for piece in self.pieces:
            pole = []
            if piece["type"] == "q":
                directions = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
                for direction in directions:
                    moves = Player.queen_move(self, self.pieces, other_player_pieces, [piece["x"], piece["y"]],
                                              direction[0], direction[1])
                    for move in moves:
                        pole.append(move)
            else:
                for direction in self.directions:
                    move = Player.pawn_move(self, self.pieces, other_player_pieces, [piece["x"], piece["y"]],
                                            direction[0], direction[1])
                    if [] != move:
                        pole.append(move)
            piece["moves"] = pole

    def pawn_move(self, my_pieces, opponent_pieces, square, x, y, first_call=True):
        if (square[0] + x) < 0 or (square[0] + x) > 7 or (square[1] + y) < 0 or (square[1] + y) > 7:
            return []

        is_my_pawn = False
        is_opponent_pawn = False
        for piece in my_pieces:
            if piece["x"] == (square[0] + x) and piece["y"] == (square[1] + y):
                is_my_pawn = True
                break
        for piece in opponent_pieces:
            if piece["x"] == (square[0] + x) and piece["y"] == (square[1] + y):
                is_opponent_pawn = True
                break
        if not is_my_pawn and not is_opponent_pawn:
            if first_call:
                return [[square[0] + x, square[1] + y], [None, None]]
            else:
                return [[square[0] + x, square[1] + y], square]
        elif is_opponent_pawn and first_call:
            return Player.pawn_move(self, my_pieces, opponent_pieces, [square[0] + x, square[1] + y], x, y, False)

        return []

    def queen_move(self, my_pieces, opponent_pieces, square, x, y):
        moves = []
        is_my_pawn = False
        is_opponent_pawn = False
        first_opponent_pawn = False
        vynechaj = False
        first_opponent_pawn_place = [None, None]
        for i in range(1, 8):
            if (square[0] + x * i) < 0 or (square[0] + x * i) > 7 or (square[1] + y * i) < 0 or (square[1] + y * i) > 7:
                break
            for piece in my_pieces:
                if piece["x"] == (square[0] + x * i) and piece["y"] == (square[1] + y * i):
                    is_my_pawn = True
                    break
            if is_my_pawn:
                break
            for piece in opponent_pieces:
                if piece["x"] == (square[0] + x * i) and piece["y"] == (square[1] + y * i):
                    if first_opponent_pawn == False:
                        first_opponent_pawn = True
                        first_opponent_pawn_place = [square[0] + x * i, square[1] + y * i]
                        vynechaj = True
                        break
                    else:
                        is_opponent_pawn = True
            if vynechaj:
                vynechaj = False
                continue
            if first_opponent_pawn and is_opponent_pawn:
                break

            moves.append([[square[0] + x * i, square[1] + y * i], first_opponent_pawn_place])

        return moves

    def update_rating(self, gameResult, other_player_rating):
        # elo - rating calculation
        expected_result_player = 1 / (1 + 10 ** ((other_player_rating - self.rating[0]) / 400))

        if gameResult == 1:
            self.rating[1] = round(self.rating[0] + 32 * (1 - expected_result_player))
        elif gameResult == 0:
            self.rating[1] = round(self.rating[0] + 32 * ((1 / 2) - expected_result_player))
        else:
            self.rating[1] = round(self.rating[0] + 32 * (0 - expected_result_player))
