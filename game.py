import copy

import pygame
from board import Board
import piece
import minimax
import time

pygame.init()
p1 = time.time()
p2 = time.time()
p1_1 = time.time()
p2_2 = time.time()
Total_time1 = None
Total_time2 = None


def redraw_game_state(win, current_board):  # functia se ocupa de partea grafica pentru fiecare stadiu al jocului
    # desenarea tablei de joc si pozitionarea coltului din stanga sus
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                square_color = (215, 222, 245)
            else:
                square_color = (86, 100, 145)
            pygame.draw.rect(win, square_color, pygame.Rect(j*100, i*100,
                                                            100, 100))

    # locurile pentru ceas
    #pygame.draw.rect(win, (255, 255, 255), pygame.Rect(820, 350, 100, 30))
    #pygame.draw.rect(win, (255, 255, 255), pygame.Rect(820, 760, 100, 30))
    '''
    time1 = p1 - current_board.p1_1
    time2 = p2 - current_board.p2_2

    formatTime1 = str(int(time1//60)) + ":" + str(int(time1 % 60))
    formatTime2 = str(int(time2 // 60)) + ":" + str(int(time2 % 60))
    if int(time1 % 60) < 10:
        formatTime1 = formatTime1[:-1] + "0" + formatTime1[-1]
    if int(time2 % 60) < 10:
        formatTime2 = formatTime2[:-1] + "0" + formatTime2[-1]

    font = pygame.font.SysFont("Calibri", 25, bold=True)

    txt = font.render("Time: " + str(formatTime2), 1, (0, 0, 0))
    txt2 = font.render("Time: " + str(formatTime1), 1, (0, 0, 0))
    win.blit(txt, (820, 350))
    win.blit(txt2, (820, 760))
    '''
    current_board.draw(win)
    pygame.display.update()


def redraw_capture_piece(win, current_board):
    piece.reset_coord()
    pygame.draw.rect(win, (215, 222, 245), pygame.Rect(810, 150, 390, 170))
    pygame.draw.rect(win, (215, 222, 245), pygame.Rect(810, 500, 390, 230))

    for captured_piece in current_board.moves_journal:
        if captured_piece[1] == -2:
            pass
        elif captured_piece[1] == -1:
            if captured_piece[0] != 0:
                captured_piece[0].draw2(win)
        elif captured_piece[1] != 0:
            captured_piece[1].draw2(win)

    pygame.display.update()


# memoreaza toate miscarile facute pana la finalul jocului
moves_journal = []


def captured_piece_UI(win):
    pygame.font.init()
    win.fill((215, 222, 245))
    myfont = pygame.font.SysFont('Calibri', 30, bold=True)
    textsurface = myfont.render('Piesele albe capturate', False, (0, 0, 0))
    win.blit(textsurface, (860, 50))
    textsurface = myfont.render('Piesele negre capturate', False, (0, 0, 0))
    win.blit(textsurface, (860, 450))
    pygame.draw.line(win, (0, 0, 0), (800, 0), (800, 800), 10)
    pygame.draw.line(win, (0, 0, 0), (800, 400), (1200, 400), 6)


def start_menu():
    # dimensiunile tablei de sah
    width = 1200
    height = 800
    global Total_time2, Total_time1
    # dimensiunea ferestrei jocului
    win = pygame.display.set_mode((width, height))
    win.fill((215, 222, 245))

    run = True
    while run:
        myfont = pygame.font.SysFont('Calibri', 30, bold=True)
        textsurface = myfont.render('Bine ati venit la jocul de sah', False, (86, 100, 145))
        win.blit(textsurface, (370, 100))
        # player vs player button
        smallfont = pygame.font.SysFont('Corbel', 30)
        text = smallfont.render('Jucator vs Jucator', True, (215, 222, 245))
        pygame.draw.rect(win, (86, 100, 145), [315, 395, 235, 40])
        win.blit(text, (325, 400))

        text = smallfont.render('Jucator vs IA 2', True, (215, 222, 245))
        pygame.draw.rect(win, (86, 100, 145), [615, 395, 200, 40])
        win.blit(text, (625, 400))

        text = smallfont.render('Jucator vs IA 1', True, (215, 222, 245))
        pygame.draw.rect(win, (86, 100, 145), [615, 350, 200, 40])
        win.blit(text, (625, 355))

        text = smallfont.render('Jucator vs IA 3', True, (215, 222, 245))
        pygame.draw.rect(win, (86, 100, 145), [615, 440, 200, 40])
        win.blit(text, (625, 445))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 315 <= mouse[0] <= 550 and 395 <= mouse[1] <= 435:
                    main(False)
                    Total_time1 = 15
                    Total_time2 = 15
                if 615 <= mouse[0] <= 815 and 350 <= mouse[1] <= 390:
                    main(True, 1)
                if 615 <= mouse[0] <= 815 and 395 <= mouse[1] <= 435:
                    main(True, 2)
                if 615 <= mouse[0] <= 815 and 440 <= mouse[1] <= 490:
                    main(True, 3)


def main(kind_of_game, DEPTH = 1):
    global moves_journal

    # dimensiunile tablei de sah
    width = 1200
    height = 800

    # dimensiunea ferestrei jocului
    win = pygame.display.set_mode((width, height))

    # partea dreapta a interfetei grafice
    captured_piece_UI(win)

    # titlul jocului
    pygame.display.set_caption("Vremea sahului")

    board = Board(8, 8)
    clock = pygame.time.Clock()
    run = True
    redraw_game_state(win, board)

    while run and board.stalemate is False and board.chess_mate is False:
        '''
        global p1, p2, p1_1, p2_2
        if board.turn == 'w':
            p1 = time.time()
        else:
            p2 = time.time()
        '''
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                moves_journal = copy.deepcopy(board.moves_journal)
                quit()
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                if 0 <= mouse_position[1] <= 800 and 0 <= mouse_position[0] <= 800:
                    # impartim la dimensiunea unui patrat si rotunjim
                    row = mouse_position[1]//100
                    col = mouse_position[0]//100
                    board.select(row, col)

            if event.type == pygame.KEYDOWN:
                # 122 este codul pentru 'z'
                if event.key == 122:
                    board.undo_move()

            redraw_game_state(win, board)
            redraw_capture_piece(win, board)

            if kind_of_game:
                # ai turn
                if board.turn == 'b':
                    move = minimax.get_ai_move(board, DEPTH, 'b')
                    if move is None:
                        board.chess_mate = True
                        print("White won")
                        board.winner = 'w'
                    else:
                        board.move(move[0], move[1])
                        board.turn = 'w'

        # reset game
        if board.stalemate is True or board.chess_mate is True:
            restart = False
            myfont = pygame.font.SysFont('Calibri', 35, bold=True)
            pygame.draw.rect(win, (86, 100, 145), pygame.Rect(15, 280, 760, 70))
            if board.stalemate:
                textsurface = myfont.render('Stalemate | Press r to restart | Press q to quit', False, (0, 0, 0))

            else:
                if board.winner == 'w':
                    textsurface = myfont.render('Alb a castigat | Press r to restart | Press q to quit', False, (0, 0, 0))
                else:
                    textsurface = myfont.render('Negru a castigat | Press r to restart | Press q to quit', False, (0, 0, 0))

            win.blit(textsurface, (20, 300))
            pygame.display.update()

            while not restart:
                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        run = False
                        moves_journal = copy.deepcopy(board.moves_journal)
                        quit()
                        pygame.quit()

                    if event.type == pygame.KEYDOWN:
                        # 122 este codul pentru 'r'
                        if event.key == 114:
                            board.undo_move()
                            restart = True
                            start_menu()
                            break

                    if event.type == pygame.KEYDOWN:
                        # 122 este codul pentru 'q'
                        if event.key == 113:
                            quit()
                            pygame.quit()

            board = Board(8, 8)
            clock = pygame.time.Clock()
            run = True
            win = pygame.display.set_mode((width, height))
            piece.reset_coord()
            captured_piece_UI(win)
            redraw_capture_piece(win, board)
            redraw_game_state(win, board)
            moves_journal = []

#main()
start_menu()