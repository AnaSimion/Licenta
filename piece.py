import copy

import pygame

# incarcarea imaginilor pentru fiecare piesa

w = [pygame.image.load("img/white_bishop.png"), pygame.image.load("img/white_king.png"),
     pygame.image.load("img/white_knight.png"), pygame.image.load("img/white_pawn.png"),
     pygame.image.load("img/white_queen.png"), pygame.image.load("img/white_rook.png")]

b = [pygame.image.load("img/black_bishop.png"), pygame.image.load("img/black_king.png"),
     pygame.image.load("img/black_knight.png"), pygame.image.load("img/black_pawn.png"),
     pygame.image.load("img/black_queen.png"), pygame.image.load("img/black_rook.png")]


# scalam piesele la dimensiunea dorita
W = [pygame.transform.scale(img, (80, 80)) for img in w]
B = [pygame.transform.scale(img, (80, 80)) for img in b]

# scalam piesele la dimensiunea dorita pentru afisarea pieselor capturate
W2 = [pygame.transform.scale(img, (40, 40)) for img in w]
B2 = [pygame.transform.scale(img, (40, 40)) for img in b]

en_passant = []

x_captured_white = 850
y_captured_white = 150
x_captured_black = 850
y_captured_black = 550


def reset_coord():
    global x_captured_white, y_captured_white, x_captured_black, y_captured_black
    x_captured_white = 850
    y_captured_white = 150
    x_captured_black = 850
    y_captured_black = 550


def undo_enpassant(turn_number):
    global en_passant
    new = []
    for i in en_passant:
        if i[5] - 1 == turn_number-1:
            new.append((i[0], i[1], i[2], i[3], i[4],  turn_number-1))
        else:
            new.append((i[0], i[1], i[2], i[3], i[4], i[5]))
    en_passant = new


def undo_enpassant2():
    global en_passant
    new = []
    if len(en_passant) > 0:
        index = en_passant[len(en_passant)-1][5]
        for i in en_passant:
            if i[5] != index:
                new.append(i)
        en_passant = new


class Piece:

    img_index = -1
    name = "generic_piece"
    position_value = [[0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0]]

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.selected = False
        self.move_list = []
        self.king = False
        self.pawn = False

    def is_selected(self):
        return self.selected

    def draw(self, win):
        if self.color == "w":
            drawThis = W[self.img_index]
        else:
            drawThis = B[self.img_index]

        win.blit(drawThis, (self.col * 100 + 10, self.row * 100 + 10))

    def draw2(self, win):

        global x_captured_white, y_captured_white, x_captured_black, y_captured_black

        if self.color == "w":
            drawThis = W2[self.img_index]
            x = x_captured_white
            y = y_captured_white
            if x_captured_white + 45 + 40 < 1200:
                x_captured_white = x_captured_white + 45
            else:
                x_captured_white = 850
                y_captured_white = y_captured_white + 45

        else:
            drawThis = B2[self.img_index]
            x = x_captured_black
            y = y_captured_black
            if x_captured_black + 45 + 40 < 1200:
                x_captured_black = x_captured_black + 45
            else:
                x_captured_black = 850
                y_captured_black = y_captured_black + 45
        win.blit(drawThis, (x, y))

    def draw_valid_moves(self, win, board, full_board):
        if self.selected:
            moves = self.final_valid_moves(board, full_board)
            for move in moves:
                x = (move[1] * 100) + 50
                y = (move[0] * 100) + 50
                pygame.draw.circle(win, (252, 177, 3), (x, y), 10)

        x = (self.col * 100) + 3
        y = (self.row * 100) + 3

        if self.selected:
            pygame.draw.rect(win, (252, 177, 3), (x, y, 93, 93), 3)

    '''
    def __str__(self):
        return str(self.col) + " " + str(self.row)
    '''

    def valid_moves(self, board, turn_number):
        return []

    def final_valid_moves(self, board, full_board):
        return []

    # verifica sa nu mutam o piesa si sa punem regele in sah/sah-mat.
    # treebuie sa o apelam in fiecare valid_moves pt fiecare piesa.
    def filter_valid_moves(self, moves, full_board):
        valid_moves = []
        check_color = 'w' if self.color == 'b' else 'b'
        king_color = 'w' if check_color == 'b' else 'b'

        for move in moves:
            copy_full_board = copy.deepcopy(full_board)
            copy_full_board.board[move[0]][move[1]] = self
            copy_full_board.board[self.row][self.col] = 0

            all_moves = []
            king_pos = 0
            i = -1
            for row in copy_full_board.board:
                i = i + 1
                j = -1
                for piece in row:
                    j = j + 1
                    if piece != 0 and piece.color == check_color:
                        all_moves = all_moves + piece.valid_moves(copy_full_board.board, full_board.turn_number)

                    if piece != 0:
                        if piece.color == king_color and type(piece) == King and king_pos == 0:
                            king_pos = (i, j)

            ok = False if king_pos in all_moves else True

            if ok is True:
                valid_moves.append(move)
        return valid_moves

    def aux_get_moves_brq(self, direction, board):
        moves = []
        i = self.row
        j = self.col
        for d in direction:
            for k in range(1, 8):
                new_row = i + d[0] * k
                new_col = j + d[1] * k
                # verificam pozitiile libere
                if 0 <= new_col <= 7 and 0 <= new_row <= 7:
                    if board[new_row][new_col] == 0:
                        moves.append((new_row, new_col))
                    # verificam daca am ajuns la o piesa ce poate fi capturata
                    elif 0 <= new_col <= 7 and 0 <= new_row <= 7 \
                            and (board[new_row][new_col].color != board[i][j].color):
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        return moves

    def aux_get_moves_kn(self, direction, board):
        i = self.row
        j = self.col

        moves = []

        for d in direction:
            new_row = i + d[0]
            new_col = j + d[1]
            if 0 <= new_row <= 7 and 0 <= new_col <= 7 and (
                    board[new_row][new_col] == 0 or board[new_row][new_col].color != self.color):
                moves.append((new_row, new_col))

        return moves


class Bishop(Piece):
    img_index = 0
    name = "Bishop"
    value = 330
    position_value = [[-20,-10,-10,-10,-10,-10,-10,-20],
                    [-10,  5,  0,  0,  0,  0,  5,-10],
                    [-10,  10,  10, 10, 10,  10,  10,-10],
                    [-10,  5,  5, 10, 10,  5,  5,-10],
                    [-10,  0, 10, 10, 10, 10,  0,-10],
                    [-10, 10, 10, 10, 10, 10, 10,-10],
                    [-10,  5,  0,  0,  0,  0,  5,-10],
                    [-20,-10,-10,-10,-10,-10,-10,-20]]

    def valid_moves(self, board, turn_number):

        # stanga-jos (1, -1), stanga-sus (-1, -1), dreapta-jos (1, 1), dreapta-sus (-1, 1)
        direction = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        moves = self.aux_get_moves_brq(direction, board)
        return moves

    def final_valid_moves(self, board, full_board):
        return self.filter_valid_moves(self.valid_moves(board, full_board.turn_number), full_board)


class King(Piece):
    img_index = 1
    name = "King"
    value = 20000
    position_value_white = [[-30,-40,-40,-50,-50,-40,-40,-30],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                        [-20,-30,-30,-40,-40,-30,-30,-20],
                        [-10,-20,-20,-20,-20,-20,-20,-10],
                         [20, 20,  0,  0,  0,  0, 20, 20],
                         [20, 30, 10,  0,  0, 10, 30, 20]]


    position_value_black = [ [20, 30, 10,  0,  0, 10, 30, 20],
                        [20, 20,  0,  0,  0,  0, 20, 20],
                        [-10,-20,-20,-20,-20,-20,-20,-10],
                        [-20,-30,-30,-40,-40,-30,-30,-20],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                         [-30,-40,-40,-50,-50,-40,-40,-30],
                         [-30,-40,-40,-50,-50,-40,-40,-30]]

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.king = True
        self.castling = True

    def get_castling(self):
        return self.castling

    def valid_moves(self, board, turn_number):

        direction = [(1, 1), (-1, -1), (-1, 1), (1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        moves = self.aux_get_moves_kn(direction, board)

        # verificam daca putem face rocada
        if self.castling:
            for row in board:
                for piece in row:
                    if piece != 0 and piece.color == self.color and type(piece) == Rook:
                        castling_right = piece.get_castling()
                        if castling_right:
                            if piece.row == self.row:
                                check = True
                                # verificam daca am gasit tura din stanga sau din dreapta
                                if self.col > piece.col:
                                    start = 1
                                    end = self.col
                                else:
                                    start = self.col + 1
                                    end = 7

                                for col_to_rook in range(start, end):
                                    if board[self.row][col_to_rook] != 0:
                                        check = False
                                if check:
                                    if self.col > piece.col:
                                        # tura din stanga
                                        moves.append((self.row, self.col - 2))
                                    else:
                                        moves.append((self.row, self.col + 2))

        return moves

    def final_valid_moves(self, board, full_board):
        return self.filter_valid_moves(self.valid_moves(board, full_board.turn_number), full_board)


class Knight(Piece):
    img_index = 2
    name = "Knight"
    value = 320

    position_value = [[-50,-40,-30,-30,-30,-30,-40,-50],
                    [-40,-20,  0,  0,  0,  0,-20,-40],
                    [-30,  0, 10, 15, 15, 10,  0,-30],
                    [-30,  5, 15, 20, 20, 15,  5,-30],
                    [-30,  0, 15, 20, 20, 15,  0,-30],
                    [-30,  5, 10, 15, 15, 10,  5,-30],
                    [-40,-20,  0,  5,  5,  0,-20,-40],
                    [-50,-40,-30,-30,-30,-30,-40,-50]]

    def valid_moves(self, board, turn_number):
        direction = [(2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1)]
        moves = self.aux_get_moves_kn(direction, board)

        return moves

    def final_valid_moves(self, board, full_board):
        return self.filter_valid_moves(self.valid_moves(board, full_board.turn_number), full_board)


class Pawn(Piece):
    img_index = 3
    name = "Pawn"
    value = 100

    position_value_white = [[70, 70, 70, 70, 70, 70, 70, 70],
                        [50, 50, 50, 50, 50, 50, 50, 50],
                        [10, 10, 20, 30, 30, 20, 10, 10],
                         [5,  5, 10, 25, 25, 10,  5,  5],
                         [0,  0,  0, 20, 20,  0,  0,  0],
                         [5, -5,-10,  0,  0,-10, -5,  5],
                         [5, 10, 10,-20,-20, 10, 10,  5],
                         [0,  0,  0,  0,  0,  0,  0,  0]]

    position_value_black = [[0,   0,   0,   0,   0,   0,   0,   0],
              [5, 10, 10,-20,-20, 10, 10,  5],
              [5, -5,-10,  0,  0,-10, -5,  5],
              [0,  0,  0, 20, 20,  0,  0,  0],
              [5,  5, 10, 25, 25, 10,  5,  5],
               [10, 10, 20, 30, 30, 20, 10, 10],
              [50, 50, 50, 50, 50, 50, 50, 50],
              [70, 70, 70, 70, 70, 70, 70, 70]]

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.first = True
        self.queen = False
        self.pawn = True

    def enpassant_check(self, board, turn_number):
        if self.color == 'b':
            if 0 <= self.row + 2 <= 7 and 0 <= self.col + 1 <= 7:
                if type(board[self.row+2][self.col+1]) == Pawn and board[self.row+2][self.col+1].color == 'w':
                    en_passant.append(('w', self.row + 2, self.col + 1, self.row+1, self.col, turn_number))
            if 0 <= self.row + 2 <= 7 and 0 <= self.col - 1 <= 7:
                if type(board[self.row+2][self.col-1]) == Pawn and board[self.row+2][self.col-1].color == 'w':
                    en_passant.append(('w', self.row + 2, self.col - 1, self.row+1, self.col, turn_number))
        if self.color == 'w':
            if 0 <= self.row - 2 <= 7 and 0 <= self.col + 1 <= 7:
                if type(board[self.row-2][self.col+1]) == Pawn and board[self.row-2][self.col+1].color == 'b':
                    en_passant.append(('b', self.row - 2, self.col + 1, self.row-1, self.col, turn_number))
            if 0 <= self.row - 2 <= 7 and 0 <= self.col - 1 <= 7:
                if type(board[self.row-2][self.col-1]) == Pawn and board[self.row-2][self.col-1].color == 'b':
                    en_passant.append(('b', self.row - 2, self.col - 1, self.row-1, self.col, turn_number))

    def valid_moves(self, board, turn_number):
        i = self.row
        j = self.col

        moves = []
        global en_passant
        for x in en_passant:
            if x[0] == self.color and x[1] == self.row and x[2] == self.col:
                if x[5] == turn_number:
                    moves.append((x[3], x[4]))

        if self.color == "b":
            if i <= 6:
                p = board[i + 1][j]
                if p == 0:
                    moves.append((i + 1, j))

                # diagonal din dreapta
                if j <= 6:
                    p = board[i + 1][j + 1]
                    if p != 0:
                        if p.color != self.color:
                            moves.append((i + 1, j + 1))

                # diagonal din stanga
                if j >= 1:
                    p = board[i + 1][j - 1]
                    if p != 0:
                        if p.color != self.color:
                            moves.append((i + 1, j - 1))

            if self.first:
                p = board[i + 2][j]
                if p == 0:  # este pozitia finala libera
                    if board[i + 1][j] == 0:  # nu exista alta piesa intre pozitia initiala si cea finala
                        moves.append((i + 2, j))

        # piese albe
        else:

            if i >= 1:
                p = board[i - 1][j]
                if p == 0:
                    moves.append((i - 1, j))

            if j <= 6:
                p = board[i - 1][j + 1]
                if p != 0:
                    if p.color != self.color:
                        moves.append((i - 1, j + 1))

            if j >= 1:
                p = board[i - 1][j - 1]
                if p != 0:
                    if p.color != self.color:
                        moves.append((i - 1, j - 1))

            if self.first:
                p = board[i - 2][j]
                if p == 0:
                    if board[i - 1][j] == 0:
                        moves.append((i - 2, j))
        return moves

    def final_valid_moves(self, board, full_board):
        return self.filter_valid_moves(self.valid_moves(board, full_board.turn_number), full_board)


class Queen(Piece):
    img_index = 4
    name = "Queen"
    value = 900
    position_value = [[-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
               [-10,  0,  5,  5,  5,  5,  0,-10],
                [ -5,  0,  5,  5,  5,  5,  0, -5],
                  [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]]

    def valid_moves(self, board, turn_number):

        direction = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        moves = self.aux_get_moves_brq(direction, board)

        direction = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        moves = moves + self.aux_get_moves_brq(direction, board)

        return moves

    def final_valid_moves(self, board, full_board):
        return self.filter_valid_moves(self.valid_moves(board, full_board.turn_number), full_board)


class Rook(Piece):
    img_index = 5
    name = "Rook"
    value = 500
    position_value = [ [0,  0,  0,  0,  0,  0,  0,  0],
                      [5, 10, 10, 10, 10, 10, 10,  5],
                     [-5,  0,  0,  0,  0,  0,  0, -5],
                     [-5,  0,  0,  0,  0,  0,  0, -5],
                     [-5,  0,  0,  0,  0,  0,  0, -5],
                     [-5,  0,  0,  0,  0,  0,  0, -5],
                     [-5,  0,  0,  0,  0,  0,  0, -5],
                      [0,  0,  0,  5,  5,  0,  0,  0]]

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.castling = True

    def get_castling(self):
        return self.castling

    def valid_moves(self, board, turn_number):
        direction = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        moves = self.aux_get_moves_brq(direction, board)
        return moves

    def final_valid_moves(self, board, full_board):
        return self.filter_valid_moves(self.valid_moves(board, full_board.turn_number), full_board)
