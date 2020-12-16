import json
import pygame

delay = 100
color_white = (255, 255, 255)
color_black = (0, 0, 0)
color_red = (255, 0, 0)
rect_size = 30
rect_margin = 3
board_size = 21  # number of printed rectangles in single line
window_size = (board_size*rect_size) + (board_size*rect_margin) + rect_margin
board = []
fontSize = 25
pygame.font.init()
font = pygame.font.SysFont('Calibri', fontSize, bold=True)


def initBoard():
    coordTop = rect_margin
    for i in range(board_size):
        boardLevel = []
        coordLeft = rect_margin
        for j in range(board_size):
            boardLevel.append(pygame.draw.rect(screen, color_white, pygame.Rect(coordLeft, coordTop, rect_size, rect_size)))
            coordLeft += rect_size + rect_margin
        board.append(boardLevel)
        coordTop += rect_size + rect_margin


screen = pygame.display.set_mode((window_size, window_size + fontSize + rect_margin))
initBoard()
pygame.init()

file = open("E:/Snake/new/1.txt", "r")

lines = file.readlines()
i = 0
for x in lines:
    i += 1
    jsonString = json.loads(x)
    snake = jsonString["snake"]
    apple = jsonString["apple"]
    for a in snake:
        pygame.draw.rect(screen, color_black, board[a[0]][a[1]])
    pygame.draw.rect(screen, color_red, board[apple[0]][apple[1]])
    message = "Wynik: " + str(len(snake) - 3) + "           Krok: " + str(i)
    text = font.render(message, True, color_white)
    screen.blit(text, [rect_margin, window_size + rect_margin])
    print("observations: " + str(jsonString["observations"]))
    pygame.display.flip()
    pygame.time.delay(delay)
    pygame.draw.rect(screen, color_black, pygame.Rect(0, window_size + rect_margin, window_size, fontSize))
    for a in snake:
        pygame.draw.rect(screen, color_white, board[a[0]][a[1]])