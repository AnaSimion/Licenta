import copy
import random
from piece import *

minimax_move = None
negamax_move = None
counter = 0
DEPTH = 2


def random_move(board):
    pieces = board.get_pieces_by_color(board.turn)
    while True:
        i = random.randint(0, len(pieces)-1)
        moves = pieces[i].final_valid_moves(board.board, board)
        if len(moves) > 0:
            j = random.randint(0, len(moves)-1)
            return (pieces[i].row, pieces[i].col), moves[j]


def get_ai_move(board, depth, turn_color):
    global negamax_move, counter, DEPTH
    DEPTH = depth
    negamax_move = None
    counter = 0
    #minimax(board, depth, 'b', board.get_moves_ai('b'))
    #negamax(board, depth, -1, board.get_moves_ai('b'))
    shuffled_moves = board.get_moves_ai(turn_color)
    random.shuffle(shuffled_moves)
    turn_multiplier = -1 if turn_color == 'b' else 1
    if turn_color == 'b':
        negamax_alpha_beta(board, depth, turn_multiplier, shuffled_moves, -board.chess_mate_value, board.chess_mate_value)
    else:
        negamax_alpha_beta(board, depth, turn_multiplier, shuffled_moves, board.chess_mate_value, -board.chess_mate_value)

    #print(counter)
    return negamax_move


def negamax(board, depth, turnMultiplier, validMoves):
    global negamax_move, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * board_evaluation(board)

    maxScore = -board.chess_mate_value
    for move in validMoves:
        board.move(move[0], move[1])
        nextMoves = board.get_moves_ai('w' if turnMultiplier == 1 else 'b')
        score = -negamax(board, depth-1, -1 * turnMultiplier, nextMoves)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                negamax_move = move
        board.undo_move()
    return maxScore


def minimax(board, depth, turn, validMoves):
    global minimax_move
    if depth == 0:
        return board_evaluation(board)

    if turn == 'w':
        maxScore = -board.chess_mate_value
        for move in validMoves:
            board.move(move[0], move[1])
            nextMoves = board.get_moves_ai('b')
            score = minimax(board, depth - 1, 'b', nextMoves)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    minimax_move = move
            board.undo_move()
        return maxScore

    else:

        minScore = board.chess_mate_value
        for move in validMoves:
            board.move(move[0], move[1])
            nextMoves = board.get_moves_ai('w')
            score = minimax(board, depth - 1, 'w', nextMoves)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    minimax_move = move
            board.undo_move()
        return minScore


def negamax_alpha_beta(board, depth, turnMultiplier, validMoves, alpha, beta):
    board = copy.deepcopy(board)
    global negamax_move, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * board_evaluation(board)

    maxScore = -board.chess_mate_value
    for move in validMoves:
        board.move(move[0], move[1])
        nextMoves = board.get_moves_ai('w' if turnMultiplier == 1 else 'b')
        score = -negamax_alpha_beta(board, depth-1, -1 * turnMultiplier, nextMoves, -beta, -alpha)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                negamax_move = move
        board.undo_move()
        # alpha beta pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def pawn_chain(piece, board):
    PAWN_ADVANTAGE1 = 10
    PAWN_ADVANTAGE2 = 22
    p1 = False
    p2 = False
    if piece.color == 'w':
        if 0 <= piece.row + 1 <= 7 and 0 <= piece.col - 1 <= 7:
            if type(board[piece.row+1][piece.col-1]) == Pawn and board[piece.row+1][piece.col-1].color == 'w':
                p1 = True
        if 0 <= piece.row + 1 <= 7 and 0 <= piece.col + 1 <= 7:
            if type(board[piece.row+1][piece.col+1]) == Pawn and board[piece.row+1][piece.col+1].color == 'w':
                p2 = True
    else:
        if 0 <= piece.row - 1 <= 7 and 0 <= piece.col - 1 <= 7:
            if type(board[piece.row-1][piece.col-1]) == Pawn and board[piece.row-1][piece.col-1].color == 'w':
                p1 = True
        if 0 <= piece.row - 1 <= 7 and 0 <= piece.col + 1 <= 7:
            if type(board[piece.row-1][piece.col+1]) == Pawn and board[piece.row-1][piece.col+1].color == 'w':
                p2 = True

    if p1 and p2:
        return PAWN_ADVANTAGE2
    else:
        return PAWN_ADVANTAGE1


def watched_over(piece, board):
    score = 0
    copy_board = copy.deepcopy(board)
    copy_board.board[piece.row][piece.col] = 0
    all_moves = copy_board.get_all_moves(piece.color)
    for move in all_moves:
        if move[0] == piece.row and move[1] == piece.col:
            score = score + 10
    return score


def board_evaluation(board):

    if board.chess_mate:
        if board.turn == 'w':
            return -board.chess_mate_value
        else:
            return board.chess_mate_value
    elif board.stalemate:
        return board.stalemate_value

    value = 0
    for row in board.board:
        for piece in row:
            if piece != 0:
                if piece.color == 'w':

                    if type(piece) != Pawn and type(piece) != King:
                        value = value + piece.value + piece.position_value[piece.row][piece.col]
                    else:
                        value = value + piece.value + piece.position_value_white[piece.row][piece.col]
                    value = value + pawn_chain(piece, board.board) #+ watched_over(piece, board)

                else:
                    if type(piece) != Pawn and type(piece) != King:
                        value = value - piece.value - piece.position_value[piece.row][piece.col]
                    else:
                        value = value - piece.value - piece.position_value_black[piece.row][piece.col]
                    value = value - pawn_chain(piece, board.board) #- watched_over(piece, board)
    return value
