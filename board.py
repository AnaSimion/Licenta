import copy

from piece import Rook
from piece import Knight
from piece import Bishop
from piece import Queen
from piece import King
from piece import Pawn
from piece import undo_enpassant, undo_enpassant2
import time


class Board:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # board este o matrice 2d si 0 reprezinta o pozitie goala pe tabla de sah
        self.board = [[Rook(0, 0, "b"), Knight(0, 1, "b"), Bishop(0, 2, "b"),
                       Queen(0, 3, "b"), King(0, 4, "b"), Bishop(0, 5, "b"),
                       Knight(0, 6, "b"), Rook(0, 7, "b")],
                      [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                      [Rook(7, 0, "w"), Knight(7, 1, "w"), Bishop(7, 2, "w"),
                       Queen(7, 3, "w"), King(7, 4, "w"), Bishop(7, 5, "w"),
                       Knight(7, 6, "w"), Rook(7, 7, "w")]]
        self.stalemate = False
        self.chess_mate = False
        self.turn_number = 0
        self.turn = 'w'
        self.chess_mate_value = 10000000
        self.stalemate_value = 0
        self.enpassant_undo_flag = False
        self.winner = 'w'
        #self.p1_1 = None
        #self.p2_2 = None

        # pozitionarea pionilor pe tabla
        for i in range(0, 8):
            self.board[1][i] = Pawn(1, i, "b")

        for i in range(0, 8):
            self.board[6][i] = Pawn(6, i, "w")

        self.moves_journal = []
        self.index_journal = []

    def change_turn(self):
        self.turn = 'b' if self.turn == 'w' else 'w'

    def draw(self, win):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    self.board[i][j].draw(win)

        # desenarea mutarilor posibile peste piese (fac asta pentru ca amrcajul sa nu fie desenat sub piesele albe)
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    self.board[i][j].draw_valid_moves(win, self.board, self)

    def select(self, row, col):
        # caut care a fost piesa selectata in miscarea anterioara
        # si ii memorez coordonatele in previous_selectious_select
        previous_select = (-1, -1)
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    if self.board[i][j].selected:
                        previous_select = (i, j)

        # daca apas de 2 ori pe aceasi piesa o deselectez
        if previous_select == (row, col):
            self.reset_selected()
            return

        if (row, col) != previous_select and self.board[row][col] != 0 and self.board[row][col].color == self.turn:
            self.board[row][col].selected = True

        if previous_select != (-1, -1):
            # verific daca este cazul de miscari
            moves = self.board[previous_select[0]][previous_select[1]].final_valid_moves(self.board, self)
            if (row, col) in moves and self.turn == self.board[previous_select[0]][previous_select[1]].color:
                self.move(previous_select, (row, col))
                # actualizarea randului
                self.change_turn()
                # verificam daca nu mai exista mutari posibile si jocul a ajuns la final
                self.game_over(self.turn)

            else:
                self.reset_selected()
                if self.board[row][col] != 0 and self.board[row][col].color == self.turn:
                    self.board[row][col].selected = True

    def reset_selected(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0:
                    self.board[i][j].selected = False

    def pawn_promotion(self, piece):

        if piece.color == 'w' and piece.row == 0:
            self.board[piece.row][piece.col] = Queen(piece.row, piece.col, 'w')
        elif piece.color == 'b' and piece.row == 7:
            self.board[piece.row][piece.col] = Queen(piece.row, piece.col, 'b')

    # ne returneaza pozitia regelui dupa culoare 'w' sau 'b'
    def get_king_pos(self, color):
        for row in self.board:
            for piece in row:
                if piece != 0:
                    if piece.color == color and type(piece) == King:
                        king_pos = (piece.row, piece.col)
                        return king_pos

    def move(self, start, end):

        """
        if self.turn == 'w':
            self.p1_1 = time.time()
        else:
            self.p2_2 = time.time()
        """

        self.enpassant_undo_flag = False
        self.turn_number = self.turn_number + 1
        self.moves_journal.append((copy.deepcopy(self.board[start[0]][start[1]]),
                                   copy.deepcopy(self.board[end[0]][end[1]])))
        self.index_journal.append((copy.deepcopy(start), copy.deepcopy(end)))

        if type(self.board[start[0]][start[1]]) == Pawn:
            # pawn first move check
            self.board[start[0]][start[1]].first = False
            if end[0] - start[0] == -2 or end[0] - start[0] == 2:
                self.board[start[0]][start[1]].enpassant_check(self.board, self.turn_number)
                self.enpassant_undo_flag = True

            # en passant
            if self.board[end[0]][end[1]] == 0 and end[1] != start[1]:
                if self.board[start[0]][start[1]].color == 'w':
                    self.moves_journal.append((copy.deepcopy(self.board[end[0]+1][end[1]]), -1))
                    self.index_journal.append(((end[0]+1, end[1]), -1))
                    self.board[end[0]+1][end[1]] = 0

                else:
                    self.moves_journal.append((copy.deepcopy(self.board[end[0]-1][end[1]]), -1))
                    self.index_journal.append(((end[0]-1, end[1]), -1))
                    self.board[end[0]-1][end[1]] = 0

        # pierderea dreptului de rocada pe acea parte
        if type(self.board[start[0]][start[1]]) == Rook:
            self.board[start[0]][start[1]].castling = False

        # rocada
        if type(self.board[start[0]][start[1]]) == King:
            self.board[start[0]][start[1]].castling = False
            if abs(start[1] - end[1]) == 2:
                # pe partea dreapta
                if start[1] - end[1] == -2:
                    self.moves_journal.append((copy.deepcopy(self.board[start[0]][7]), -2))
                    self.index_journal.append(((start[0], 7), (start[0], 5)))
                    self.board[start[0]][5] = self.board[start[0]][7]
                    self.board[start[0]][5].col = 5
                    self.board[start[0]][7] = 0
                # pe partea stanga
                if start[1] - end[1] == 2:
                    self.moves_journal.append((copy.deepcopy(self.board[start[0]][0]), -2))
                    self.index_journal.append(((start[0], 0), (start[0], 3)))
                    self.board[start[0]][3] = self.board[start[0]][0]
                    self.board[start[0]][3].col = 3
                    self.board[start[0]][0] = 0

        self.board[end[0]][end[1]] = self.board[start[0]][start[1]]
        self.board[end[0]][end[1]].row = end[0]
        self.board[end[0]][end[1]].col = end[1]
        self.board[start[0]][start[1]] = 0

        # pawn promotion
        if type(self.board[end[0]][end[1]]) == Pawn:
            self.pawn_promotion(self.board[end[0]][end[1]])

        self.reset_selected()

    def undo_move(self):
        if len(self.moves_journal) > 0:
            self.turn_number = self.turn_number - 1
            m1 = self.moves_journal.pop()
            m2 = self.index_journal.pop()
            # en passant caz special
            if m1[1] == -1:
                undo_enpassant(self.turn_number)
                self.board[m2[0][0]][m2[0][1]] = m1[0]
                self.undo_move()

            # rocada caz special
            elif m1[1] == -2:
                self.board[m2[0][0]][m2[0][1]] = m1[0]
                self.board[m2[1][0]][m2[1][1]] = 0
                self.undo_move()

            else:
                # caz obisnuit pentru tot ce nu e en-passant
                self.board[m2[0][0]][m2[0][1]] = m1[0]
                self.board[m2[0][0]][m2[0][1]].row = m1[0].row
                self.board[m2[0][0]][m2[0][1]].col = m1[0].col
                self.board[m2[1][0]][m2[1][1]] = m1[1]
                if m1[1] != 0:
                    self.board[m2[1][0]][m2[1][1]].row = m1[1].row
                    self.board[m2[1][0]][m2[1][1]].col = m1[1].col
                self.change_turn()
                self.reset_selected()
            self.stalemate = False
            self.chess_mate = False

            # en-passant ai
            if self.enpassant_undo_flag:
                undo_enpassant2()

    def get_all_moves(self, check_color):
        all_moves = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == check_color:
                    all_moves = all_moves + piece.final_valid_moves(self.board, self)
        return all_moves

    def game_over(self, check_color):

        if len(self.get_all_moves(self.turn)) == 0:
            if self.get_king_pos(self.turn) in self.get_all_moves("w" if self.turn == 'b' else "b"):
                # ramane de implementat un mesaj grafic si pentru final de joc si pentru stalemate
                print("game over, winner is", "white" if self.turn == 'b' else "black")
                self.chess_mate = True
                self.winner = 'w' if self.turn == 'b' else 'b'
            else:
                print("game over, stalemate")
                self.stalemate = True

    def get_pieces_by_color(self, check_color):
        all_pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == check_color:
                    all_pieces.append(piece)
        return all_pieces

    def get_moves_ai(self, check_color):
        moves_for_ai = []
        pieces = self.get_pieces_by_color(check_color)
        for piece in pieces:
            moves = piece.final_valid_moves(self.board, self)
            for move in moves:
                moves_for_ai.append(((piece.row, piece.col), move))
        return moves_for_ai
