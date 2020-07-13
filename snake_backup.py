import pygame
import random
from direction import Direction


speed = 500 #przerwa pomiędzu ruchami węża w ms (szybkosć węża)
done = False
isPointAvaiable = False
#RGB colors:
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)
colorRed = (255, 0, 0)
rectSize = 30
rectMargin = 3
boardSize = 21  #number of printed rectangles in single line
windowSize = (boardSize*rectSize) + (boardSize*rectMargin) + rectMargin
board = []
#head and tail are tuples which holds board indexes of snake's head and tail
snake = [[10,11], [10,10], [10,9]]
point = []  #czerwony punkt
direction = Direction.east
rectangle = pygame.Surface((100, 100))


#----------------------------------------------------------------------------------------------
# tworzy planszę, board to odpowiednik dwuwymiarowej tablicy z obiektami kwadratów
# druga pętla (j) tworzy poziomy rząd kwadratów, pierwsza pętla dodaje poziomy rząd do głównej tablicy planszy
def initBoard():
    coordTop = rectMargin
    for i in range(boardSize):
        boardLevel = []
        coordLeft = rectMargin
        for j in range(boardSize):
            boardLevel.append(pygame.draw.rect(screen, colorWhite, pygame.Rect(coordLeft, coordTop, rectSize, rectSize)))
            coordLeft += rectSize + rectMargin
        board.append(boardLevel)
        coordTop += rectSize + rectMargin
        

def initSnake():
    pygame.draw.rect(screen, colorBlack, board[snake[0][0]][snake[0][1]])
    pygame.draw.rect(screen, colorBlack, board[snake[1][0]][snake[1][1]])
    pygame.draw.rect(screen, colorBlack, board[snake[2][0]][snake[2][1]])
    

def move(head, addPoint):
    global isPointAvaiable
    if addPoint:
        addPoint = False
        isPointAvaiable = False
    else:
        tail = snake[len(snake)-1][:]   # [:] oznacza, że kopiujemy wartosc obiektu, a nie jego adres, a to jest tutaj ważne
        pygame.draw.rect(screen, colorWhite, board[tail[0]][tail[1]])
        snake.remove(tail)
    snake.insert(0,head)
    pygame.draw.rect(screen, colorBlack, board[head[0]][head[1]])
   

def randomPoint():
    global isPointAvaiable #mówi, że ma korzystać ze zmiennej globalnej, a nie tworzyć nową lokalną w metodzie
    global point
    while not isPointAvaiable:
        x = random.randint(0, boardSize-1)
        y = random.randint(0, boardSize-1)
        if snake.count([x,y])==0:
            pygame.draw.rect(screen, colorRed, board[x][y])
            isPointAvaiable = True    
            point = [x,y]
            
def colision():
    global done
    addPoint = False
    head = snake[0][:]
    if(direction==Direction.east):
        head[1]+=1
    elif(direction==Direction.north):
        head[0]-=1
    elif(direction==Direction.west):
        head[1]-=1
    elif(direction==Direction.south):
        head[0]+=1
    
    if head==point:
        addPoint = True
    elif snake.count(head)>0:
        done = True
    move(head, addPoint)
        
#-----------------------------------------------------------------------------------------------

screen = pygame.display.set_mode((windowSize, windowSize))
initBoard()
initSnake()
pygame.init()

while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True       
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            direction=Direction.north
        elif pressed[pygame.K_DOWN]:
            direction=Direction.south
        elif pressed[pygame.K_LEFT]:
            direction=Direction.west
        elif pressed[pygame.K_RIGHT]:
            direction=Direction.east
        
        if(pygame.time.get_ticks()%speed==0): #warunek jest spełniany co sekundę
            pygame.time.delay(1)    #usypia program na 1 milisekundę, musiałem to dodać bo czasem w ciągu jednej milisekundy pętla potrafiła wykonać się dwa razy i szły dwa ruchy węża na raz.
            colision()
            if not isPointAvaiable: randomPoint()
            pygame.display.flip()
        