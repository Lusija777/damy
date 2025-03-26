import tkinter
from PIL import Image, ImageTk
import itertools

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
        

        w_pawn = Image.open('white-pawn.png').resize((self.square_size, self.square_size))
        b_pawn = Image.open('black-pawn.png').resize((self.square_size, self.square_size))
        w_queen = Image.open('white-queen.png').resize((self.square_size, self.square_size))
        b_queen = Image.open('black-queen.png').resize((self.square_size, self.square_size))
        flag = Image.open('flag.png').resize((int(0.3*self.square_size), int(0.3*self.square_size)))
        half = Image.open('half.png').resize((int(0.3*self.square_size), int(0.3*self.square_size)))
        self.w_pawn = ImageTk.PhotoImage(w_pawn)
        self.b_pawn = ImageTk.PhotoImage(b_pawn)
        self.w_queen = ImageTk.PhotoImage(w_queen)
        self.b_queen = ImageTk.PhotoImage(b_queen)
        self.flag = ImageTk.PhotoImage(flag)
        self.half = ImageTk.PhotoImage(half)

        self.b_queen_anim = [ImageTk.PhotoImage(b_queen.rotate(15)), self.b_queen, ImageTk.PhotoImage(b_queen.rotate(-15)), self.b_queen]
        self.w_queen_anim = [ImageTk.PhotoImage(w_queen.rotate(15)), self.w_queen, ImageTk.PhotoImage(w_queen.rotate(-15)), self.w_queen]
        
        Program.timer(self)
        Program.board(self)
        tkinter.mainloop() 
        
    def board(self):
        farba1, farba2 =  "khaki", "saddlebrown"
        game_size = 360

        notation = ""
        for i, move in enumerate (self.moves):
            if i%8 == 0 and i!=0:
                notation += "\n"
            if i%2 == 0:       
                notation += (f"{i//2 +1}. {move[5]} ")
            else:
                notation += (f"{move[5]} ")
                
        if self.game_result is not None:
            if len(notation) > 0:
                notation += "\n"
            if self.game_result == 1:
                notation += "1 - 0"
            elif self.game_result == 0:
                notation += "1/2 - 1/2"
            elif self.game_result == -1:
                notation += "0 - 1"
        
        self.canvas.delete("all")
        for i in range(8):
            f1, f2 = farba1, farba2
            for j in range(8):
                self.canvas.create_rectangle(self.spacer+self.square_size*j, 2*self.spacer+self.square_size*i+ self.square_size/2, self.spacer+self.square_size*j+self.square_size, 2*self.spacer+self.square_size*i+self.square_size+ self.square_size/2, fill=f1, outline = "")
                f1, f2 = f2, f1
            farba1, farba2 = farba2, farba1

        if len(self.moves) > 0:
            last_move = self.moves[-1]
            self.canvas.create_rectangle(self.spacer+self.square_size*last_move[1][0], 2*self.spacer +self.square_size/2+self.square_size*last_move[1][1], self.spacer+self.square_size*last_move[1][0]+self.square_size, 2*self.spacer +self.square_size/2+self.square_size*last_move[1][1]+self.square_size, fill="#8a714b", outline = "")
            self.canvas.create_rectangle(self.spacer+self.square_size*last_move[2][0], 2*self.spacer +self.square_size/2+self.square_size*last_move[2][1], self.spacer+self.square_size*last_move[2][0]+self.square_size, 2*self.spacer +self.square_size/2+self.square_size*last_move[2][1]+self.square_size, fill="#8a714b", outline = "")

        if self.current_move["piece"] is not None:
            self.canvas.create_rectangle(self.spacer+self.square_size*self.current_move["piece"]["x"], 2*self.spacer+self.square_size*self.current_move["piece"]["y"]+ self.square_size/2, self.spacer+self.square_size*self.current_move["piece"]["x"]+self.square_size, 2*self.spacer+self.square_size*self.current_move["piece"]["y"]+self.square_size+ self.square_size/2, fill="YellowGreen", outline = "")
            for available_move in self.current_move["piece"]["moves"]:
                self.canvas.create_oval(self.spacer+self.square_size*available_move[0][0] + 1/3*self.square_size, 2*self.spacer +self.square_size/2+self.square_size*available_move[0][1]+ 1/3*self.square_size, self.spacer+self.square_size*available_move[0][0]+self.square_size - 1/3*self.square_size, 2*self.spacer +self.square_size/2+self.square_size*available_move[0][1]+self.square_size - 1/3*self.square_size, fill="YellowGreen", outline = "YellowGreen")

        for piece in self.player1.pieces:
            if piece["type"] == "q":
                self.canvas.create_image(self.spacer+self.square_size*piece["x"]+self.square_size/2, 2*self.spacer+self.square_size*piece["y"]+self.square_size, image=self.w_queen, tag = "w_queen" + str(piece["x"]) + str(piece["y"]))
            else:
                self.canvas.create_image(self.spacer+self.square_size*piece["x"]+self.square_size/2, 2*self.spacer+self.square_size*piece["y"]+self.square_size, image=self.w_pawn)

        for piece in self.player2.pieces:
            if piece["type"] == "q":
                self.canvas.create_image(self.spacer+self.square_size*piece["x"]+self.square_size/2, 2*self.spacer+self.square_size*piece["y"]+self.square_size, image=self.b_queen, tag = "b_queen" + str(piece["x"]) + str(piece["y"]))
            else:
                self.canvas.create_image(self.spacer+self.square_size*piece["x"]+self.square_size/2, 2*self.spacer+self.square_size*piece["y"]+self.square_size, image=self.b_pawn)
        

        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*0, text = f"8", anchor="ne", fill = "khaki")
        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*1, text = f"7", anchor="ne", fill = "saddlebrown")
        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*2, text = f"6", anchor="ne", fill = "khaki")
        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*3, text = f"5", anchor="ne", fill = "saddlebrown")
        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*4, text = f"4", anchor="ne", fill = "khaki")
        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*5, text = f"3", anchor="ne", fill = "saddlebrown")
        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*6, text = f"2", anchor="ne", fill = "khaki")
        self.canvas.create_text(self.spacer+self.square_size*8 - 5, 2*self.spacer+self.square_size/2+self.square_size*7, text = f"1", anchor="ne", fill = "saddlebrown")
        
        self.canvas.create_text(self.spacer+self.square_size*7 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"h", anchor="sw", fill = "saddlebrown")
        self.canvas.create_text(self.spacer+self.square_size*6 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"g", anchor="sw", fill = "khaki")
        self.canvas.create_text(self.spacer+self.square_size*5 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"f", anchor="sw", fill = "saddlebrown")
        self.canvas.create_text(self.spacer+self.square_size*4 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"e", anchor="sw", fill = "khaki")
        self.canvas.create_text(self.spacer+self.square_size*3 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"d", anchor="sw", fill = "saddlebrown")
        self.canvas.create_text(self.spacer+self.square_size*2 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"c", anchor="sw", fill = "khaki")
        self.canvas.create_text(self.spacer+self.square_size*1 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"b", anchor="sw", fill = "saddlebrown")
        self.canvas.create_text(self.spacer+self.square_size*0 + 5, 2*self.spacer+self.square_size/2+self.square_size*8, text = f"a", anchor="sw", fill = "khaki")
        

        self.canvas.create_rectangle(self.square_size*8+2*self.spacer, 2*self.spacer + self.square_size/2, self.square_size*8+2*self.spacer + game_size, 2*self.spacer + self.square_size,fill="white")
        self.canvas.create_text(self.square_size*8+3*self.spacer, 3*self.spacer + self.square_size/2, text = "GAME REPORT", anchor = "nw", font = "arial 12")
        self.canvas.create_rectangle(self.square_size*8+2*self.spacer, 2*self.spacer + self.square_size, self.square_size*8+2*self.spacer + game_size, 2*self.spacer + 8.5*self.square_size,fill="white")
        self.canvas.create_text(self.square_size*8+3*self.spacer, 3*self.spacer + self.square_size, anchor = "nw", text = notation, font = "arial 10")

        self.canvas.create_rectangle(self.square_size*8+3*self.spacer + game_size, 2*self.spacer + self.square_size/2, self.square_size*8+3*self.spacer + 2*game_size, 2*self.spacer + self.square_size,fill="white")
        self.canvas.create_text(self.square_size*8+4*self.spacer + game_size, 3*self.spacer + self.square_size/2, text = "BEST PLAYERS", anchor = "nw", font = "arial 12")
        self.canvas.create_rectangle(self.square_size*8+3*self.spacer + game_size, 2*self.spacer + self.square_size, self.square_size*8+3*self.spacer + 2*game_size, 2*self.spacer + 8.5*self.square_size,fill="white")
        self.canvas.create_text(self.square_size*8+4*self.spacer+ game_size, 3*self.spacer + self.square_size, anchor = "nw", text = self.best_players, font = "arial 10")
        
        self.canvas.delete("on_move")
        if self.game_result is None:
            if self.on_move == self.player2:
                self.canvas.create_oval(2*self.spacer, 2*self.spacer, self.square_size/2 , self.square_size/2, fill = "ForestGreen", outline = "", tag = "on_move")
            elif self.on_move == self.player1:
                self.canvas.create_oval(2*self.spacer, self.square_size*8 + 4*self.spacer +self.square_size/2, self.square_size/2, self.square_size*9 +2*self.spacer , fill = "ForestGreen", outline = "", tag = "on_move")

        rating1 = str(self.player1.rating[0])
        rating2 = str(self.player2.rating[0])
        if self.game_result is not None:
            new_rating1 = self.player1.rating[1]-self.player1.rating[0]
            new_rating2 = self.player2.rating[1]-self.player2.rating[0]
            if new_rating1 < 0:
                rating1 += " " + str(new_rating1)
            else:
                rating1 += " +" + str(new_rating1)
            if new_rating2 < 0:
                rating2 += " " + str(new_rating2)
            else:
                rating2 += " +" + str(new_rating2)
        self.canvas.create_text(self.square_size/2 + 2*self.spacer, self.square_size*8 +3*self.spacer + self.square_size/2, text = f"{self.player1.name} {rating1}", anchor="nw", font='arial 24', fill = "white")
        self.canvas.create_text(self.square_size/2 + 2*self.spacer, self.spacer, text = f"{self.player2.name} {rating2}", anchor="nw", font='arial 24', fill = "white")

        for i, player in enumerate ([self.player1, self.player2]):
            for name, button in player.buttons.items():
                self.canvas.create_rectangle(button[0][0], button[0][1], button[1][0], button[1][1], fill = button[2])
                if name == "resign":
                    self.canvas.create_image((button[0][0] + button[1][0])/2, (button[0][1] + button[1][1])/2, image=self.flag)
                else:
                    self.canvas.create_image((button[0][0] + button[1][0])/2, (button[0][1] + button[1][1])/2, image=self.half)

            seconds = str(player.time%600)
            if len(seconds) == 2:
                seconds = "0" + seconds
            elif len(seconds) == 1:
                seconds = "00" + seconds
            seconds = seconds[:2]
            minutes = str(player.time//600)
            if len(minutes) == 1:
                minutes = "0" + minutes
            self.canvas.create_rectangle(player.timer[0],player.timer[1], player.timer[0] + 1.5*self.square_size ,player.timer[1] + 0.5*self.square_size, fill = "#333333")
            self.canvas.create_text(player.timer[0]+ 1.5*self.spacer - 2,player.timer[1], text=(f"{minutes}:{seconds}"), fill = "white", tag = f"timer{i}", anchor="nw", font='arial 24')

        if self.game_result == 1:
            for image in self.w_queen_anim:
                for piece in self.player1.pieces:
                    if piece["type"] == "q":
                        self.canvas.delete("w_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.create_image(self.spacer+self.square_size*piece["x"]+self.square_size/2, 2*self.spacer+self.square_size*piece["y"]+self.square_size, image=image, tag = "w_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.update()
                self.canvas.after(300)
        if self.game_result == -1:
            for image in self.b_queen_anim:
                for piece in self.player2.pieces:
                    if piece["type"] == "q":
                        self.canvas.delete("b_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.create_image(self.spacer+self.square_size*piece["x"]+self.square_size/2, 2*self.spacer+self.square_size*piece["y"]+self.square_size, image=image, tag = "b_queen" + str(piece["x"]) + str(piece["y"]))
                        self.canvas.update()
                self.canvas.after(300)

    def timer(self):
        if not self.do_tick:
            return

        if self.on_move == self.player1:
            i = 0
        else:
            i = 1
            
        seconds = str(self.on_move.time%600)
        if len(seconds) == 2:
            seconds = "0" + seconds
        elif len(seconds) == 1:
            seconds = "00" + seconds
        seconds = seconds[:2]
        minutes = str(self.on_move.time//600)
        if len(minutes) == 1:
            minutes = "0" + minutes
        self.canvas.delete(f"timer{i}")
        self.canvas.create_text(self.on_move.timer[0]+ 1.5*self.spacer - 2, self.on_move.timer[1], text=(f"{minutes}:{seconds}"), fill = "white", tag = f"timer{i}", anchor="nw", font='arial 24')
        
        if self.on_move.time == 0:
            if self.on_move == self.player1:
                Program.set_game_result(self, -1)
            else:
                Program.set_game_result(self, 1)
        else:
            self.on_move.time -= 1
            self.canvas.after(100, self.timer)

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
            Program.click(self, event)      
                    
    def click(self, event):
        # any player can offer/accept/decline draw or resign, so check if any of these buttons were clicked
        button_clicked = False
        for player in [self.player1, self.player2]:
            if button_clicked:
                break
            for name, coordinates in player.buttons.items():
                if button_clicked:
                    break
                if event.x >= coordinates[0][0] and event.y >= coordinates[0][1] and event.x <= coordinates[1][0] and event.y <=  coordinates[1][1]:
                    button_clicked = True
                    if name == "draw":
                        if player.offering_draw:
                            # made an offer and interrupted her
                            player.offering_draw = False                      
                            self.player2.buttons["draw"][2] = "grey"
                            self.player1.buttons["draw"][2] = "grey"
                            Program.board(self)
                        else:
                            if (player == self.player1 and self.player2.offering_draw) or (player == self.player2 and self.player1.offering_draw):
                                # end of game, accepted draw
                                Program.set_game_result(self, 0)
                            else:
                                # making an offer to draw
                                player.offering_draw = True
                                coordinates[2] = "maroon"
                                if player == self.player1:
                                    self.player2.buttons["draw"][2] = "navy"
                                else:
                                    self.player1.buttons["draw"][2] = "navy"
                                Program.board(self)
                    else:
                        # I resigned, end of game, my loss
                        if player == self.player1:
                            Program.set_game_result(self, -1)
                        else:
                            Program.set_game_result(self, 1)

        if button_clicked:
            self.current_move = {"piece": None, "to": None}
            Program.board(self)
            return None
        
        square = Program.find_square(self, event.x, event.y)
        if square is None:
            self.current_move = {"piece": None, "to": None}
            Program.board(self)
            return None
        
        if self.current_move["piece"] is None:
            for piece in self.on_move.pieces:
                if [piece["x"], piece["y"]] == square:
                    self.current_move["piece"] = piece
                    Program.board(self)
                    break
            return None   

        for moves in self.current_move["piece"]["moves"]:
            if square == moves[0]:
                self.current_move["to"] = moves
                break
            
        if self.current_move["to"] is None:
            self.current_move = {"piece": None, "to": None}
            Program.board(self)
            return None

        #making a move, calculating new available moves for each piece
        Program.make_move(self, [self.current_move["piece"]["type"],
            [self.current_move["piece"]["x"], self.current_move["piece"]["y"]],
            [self.current_move["to"][0][0], self.current_move["to"][0][1]],
            self.current_move["to"][1] != [None, None],
            self.current_move["to"][0][1] == 7 or self.current_move["to"][0][1] == 0
        ])
        # any move automatically decline offer on a draw
        self.player2.offering_draw = False
        self.player1.offering_draw = False
        self.player2.buttons["draw"][2] = "grey"
        self.player1.buttons["draw"][2] = "grey"
        
        if self.on_move == self.player1:
            opposite_player = self.player2
        else:
            opposite_player = self.player1
            
        if len(opposite_player.pieces) == 0:
            if opposite_player == self.player1:
                Program.set_game_result(self, -1)
            else:
                Program.set_game_result(self, 1)    
            return None
            
        has_available_move = False
        for piece in opposite_player.pieces:
            if len(piece["moves"]) > 0:
                has_available_move = True
                break
        if not has_available_move:
            if opposite_player == self.player1:
                Program.set_game_result(self, -1)
            else:
                Program.set_game_result(self, 1)
            return None

        # no capture, no promotion
        number_of_insignificant_moves = 0
        for move in self.moves[::-1]:
            if not move[3] and not move[4]:
                number_of_insignificant_moves += 1
            else:
                break
        if number_of_insignificant_moves >= 80:
            Program.set_game_result(self, 0)
            return None
        
        self.on_move = opposite_player
        self.current_move = {"piece": None, "to": None}
        Program.board(self)
        

    def make_move(self, move):
        i = len(self.moves)      
        alphabet = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"} 
        notation = ""
        
        if move[0] == "q":
            notation += "Q"
        if (i%2) == 0:
            pieces = self.player1.pieces
        else:
            pieces = self.player2.pieces
        move_possible_by_another = False    
        for piece in pieces:
            if not move_possible_by_another and piece["type"] == move[0] and [piece["x"], piece["y"]] != move[1]:
                for available_move in piece["moves"]:
                    if move[2] == available_move[0]:
                        move_possible_by_another = True
                        break
        if move_possible_by_another or (move[3] and "p" == move[0]):
            notation += alphabet[move[1][0]]
        if move[3]:
            notation += "x"
        notation += alphabet[move[2][0]] + str(8 - move[2][1])
        if move[4]:
            notation += "=Q"
            
        move.append(notation)
        self.moves.append(move)

        if self.on_move == self.player1:
            opponent_pieces = self.player2.pieces
        else:
            opponent_pieces = self.player1.pieces
                              
        if self.current_move["to"][1] is not [None, None]:
            #throwing piece out of the game
            for j in range(len(opponent_pieces)):
                if [opponent_pieces[j]["x"], opponent_pieces[j]["y"]] == self.current_move["to"][1]:
                    opponent_pieces.pop(j)
                    break
    
        #change of coordinates, the type of figure that made the move        
        self.current_move["piece"]["x"] = self.current_move["to"][0][0]
        self.current_move["piece"]["y"] = self.current_move["to"][0][1]
        if self.current_move["to"][0][1] == 7 or self.current_move["to"][0][1] == 0:
            self.current_move["piece"]["type"] = "q"
            
        Player.find_moves(self.player2, self.player1.pieces)
        Player.find_moves(self.player1, self.player2.pieces)

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
        
        game_file = open("game.txt", "w")
        for i, move in enumerate (self.moves):
            if i%2 == 0:       
                game_file.write(f"{i//2 +1}. {move[5]}")
            else:
                game_file.write(f" {move[5]}\n")
                
        notation = ""
        if len(self.moves) > 0:
            notation += "\n"
        if self.game_result == 1:
            notation += "1 - 0"
        elif self.game_result == 0:
            notation += "1/2 - 1/2"
        elif self.game_result == -1:
            notation += "0 - 1"
        game_file.write(notation)
        game_file.close()
        
        
        Player.update_rating(self.player1, result, self.player2.rating[0])
        Player.update_rating(self.player2, result*(-1), self.player1.rating[0])
        
        for player in [self.player1, self.player2]:
            if player.identifier is None:
                self.players_file_lines.append(f"{player.name} {player.rating[1]}\n")           
            else:
                self.players_file_lines[player.identifier] = (f"{player.name} {player.rating[1]}\n")

        players_file = open("players.txt", "w")        
        players_file.writelines(self.players_file_lines)
        players_file.close()
        
        Program.board(self)

class Player:
    def __init__(self, i, players_file_lines, player1_name):
        self.square_size = 72
        self.spacer = 10
        self.pieces = []
        if i == 1:
            for k in range(8):
                for j in range(6,8):
                    if (k%2) == 1 and (j%2) == 0:
                        self.pieces.append({"type":"p", "x":k , "y":j})
                    elif (k%2) == 0 and (j%2) == 1:
                        self.pieces.append({"type":"p", "x":k , "y":j})
            
                        
            self.name = input(f"Enter the name of the {i}st player:")
            while self.name == "" or " " in self.name or len(self.name) > 20:
                print("The name cannot be empty, cannot contain a space and cannot contain more than 20 characters.")
                self.name = input(f"Enter the name of the {i}st player:")
            self.buttons = {
                "draw": [[5.5*self.square_size - self.spacer, self.square_size*8 + 3*self.spacer +self.square_size/2],[6*self.square_size - self.spacer, self.square_size*9 + 3*self.spacer], "grey", .8],
                "resign": [[6*self.square_size, self.square_size*8 + 3*self.spacer +self.square_size/2],[6.5*self.square_size, self.square_size*9 + 3*self.spacer], "grey", .8],
            }
            self.timer = [6.5*self.square_size + self.spacer, self.square_size*8 + 3*self.spacer +self.square_size/2]
            self.directions = [[-1, -1], [1, -1]]           
        else:
            for k in range(8):
                for j in range(2):
                    if (k%2) == 1 and (j%2) == 0:
                        self.pieces.append({"type":"p", "x":k , "y":j})
                    elif (k%2) == 0 and (j%2) == 1:
                        self.pieces.append({"type":"p", "x":k , "y":j})

            self.name = input(f"Enter the name of the {i}nd player:")
            while self.name == "" or " " in self.name or self.name == player1_name or len(self.name) > 20:
                print("The name cannot be empty, cannot contain a space, cannot play with yourself, and cannot contain more than 20 characters.")
                self.name = input(f"Enter the name of the {i}nd player:")
            self.buttons = {
                "draw": [[5.5*self.square_size - self.spacer, self.spacer],[6*self.square_size - self.spacer, self.spacer+ self.square_size/2], "grey", .8],
                "resign": [[6*self.square_size, self.spacer],[6.5*self.square_size, self.spacer+ self.square_size/2], "grey", .8],
            }
            self.timer = [6.5*self.square_size + self.spacer, self.spacer]
            self.directions = [[-1, 1], [1, 1]]
            
        is_new_player = True
        for identifier, line in enumerate (players_file_lines):
            if " " not in line:
                continue
            name_in_line, rating_in_line = line.strip().split(" ")
            rating_in_line = int(rating_in_line)
            if self.name.lower() == name_in_line.lower():
                self.rating = [rating_in_line, None]
                self.identifier = identifier
                is_new_player = False
                break            
        if is_new_player:
            self.rating = [1500, None]
            self.identifier = identifier

        self.offering_draw = False
        self.time = 6000

    def find_moves(self, other_player_pieces):
        
        for piece in self.pieces:
            pole = []
            if piece["type"] == "q":
                directions = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
                for direction in directions:
                    moves = Player.queen_move(self, self.pieces, other_player_pieces, [piece["x"], piece["y"]], direction[0], direction[1])
                    for move in moves:
                        pole.append(move)
            else:             
                for direction in self.directions:
                    move = Player.pawn_move(self, self.pieces, other_player_pieces, [piece["x"], piece["y"]], direction[0], direction[1])
                    if [] != move:
                        pole.append(move)
            piece["moves"] = pole

                
    def pawn_move(self, my_pieces, opponent_pieces, square, x, y, first_call = True):
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
        for i in range (1,8):
            if (square[0] + x*i) < 0 or (square[0] + x*i) > 7 or (square[1] + y*i) < 0 or (square[1] + y*i) > 7:
                break 
            for piece in my_pieces:
                if piece["x"] == (square[0] + x*i) and piece["y"] == (square[1] + y*i):
                    is_my_pawn = True
                    break
            if is_my_pawn:
                break
            for piece in opponent_pieces:
                if piece["x"] == (square[0] + x*i) and piece["y"] == (square[1] + y*i):
                    if first_opponent_pawn == False:
                        first_opponent_pawn = True
                        first_opponent_pawn_place = [square[0] + x*i, square[1] + y*i]
                        vynechaj = True
                        break                         
                    else:
                        is_opponent_pawn = True            
            if vynechaj:
                vynechaj = False
                continue
            if first_opponent_pawn and is_opponent_pawn:
                break

            moves.append([[square[0] + x*i, square[1] + y*i], first_opponent_pawn_place])
        
        return moves
    
    def update_rating(self, gameResult, other_player_rating):
        #elo - rating calculation  
        expected_result_player = 1/(1+10**((other_player_rating - self.rating[0])/400))
        
        if gameResult == 1:
            self.rating[1] = round(self.rating[0] + 32*(1-expected_result_player))                
        elif gameResult == 0:
            self.rating[1] = round(self.rating[0] + 32*((1/2)-expected_result_player))
        else:
            self.rating[1] = round(self.rating[0] + 32*(0-expected_result_player))
                       
Program()       
    


