import pygame
import random

from direction import Direction
from tf_agents.environments import py_environment


class Snake(py_environment.PyEnvironment):
    
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
    screen = pygame.display.set_mode((windowSize, windowSize))
    
    
    #----------------------------------------------------------------------------------------------
    def __init__(self):
        print("poszlo")
        self.initBoard()
        print("1")
        self.initSnake()
        print("2")
        pygame.init()
        print("3")
        
        while not self.done:
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.done = True       
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    self.direction=Direction.north
                elif pressed[pygame.K_DOWN]:
                    self.direction=Direction.south
                elif pressed[pygame.K_LEFT]:
                    self.direction=Direction.west
                elif pressed[pygame.K_RIGHT]:
                    self.direction=Direction.east
                    
                if(pygame.time.get_ticks()%self.speed==0): #warunek jest spełniany co sekundę
                    pygame.time.delay(1)    #usypia program na 1 milisekundę, musiałem to dodać bo czasem w ciągu jednej milisekundy pętla potrafiła wykonać się dwa razy i szły dwa ruchy węża na raz.
                    self.colision()
                    if not self.isPointAvaiable: self.randomPoint()
                    pygame.display.flip()
    
    
    # tworzy planszę, board to odpowiednik dwuwymiarowej tablicy z obiektami kwadratów
    # druga pętla (j) tworzy poziomy rząd kwadratów, pierwsza pętla dodaje poziomy rząd do głównej tablicy planszy
    def initBoard(self):
        coordTop = self.rectMargin
        for i in range(self.boardSize):
            boardLevel = []
            coordLeft = self.rectMargin
            for j in range(self.boardSize):
                boardLevel.append(pygame.draw.rect(self.screen, self.colorWhite, pygame.Rect(coordLeft, coordTop, self.rectSize, self.rectSize)))
                coordLeft += self.rectSize + self.rectMargin
            self.board.append(boardLevel)
            coordTop += self.rectSize + self.rectMargin
            
    
    def initSnake(self):
        pygame.draw.rect(self.screen, self.colorBlack, self.board[self.snake[0][0]][self.snake[0][1]])
        pygame.draw.rect(self.screen, self.colorBlack, self.board[self.snake[1][0]][self.snake[1][1]])
        pygame.draw.rect(self.screen, self.colorBlack, self.board[self.snake[2][0]][self.snake[2][1]])
        
    
    def move(self, head, addPoint):
        if addPoint:
            addPoint = False
            self.isPointAvaiable = False
        else:
            tail = self.snake[len(self.snake)-1][:]   # [:] oznacza, że kopiujemy wartosc obiektu, a nie jego adres, a to jest tutaj ważne
            pygame.draw.rect(self.screen, self.colorWhite, self.board[tail[0]][tail[1]])
            self.snake.remove(tail)
        self.snake.insert(0,head)
        pygame.draw.rect(self.screen, self.colorBlack, self.board[head[0]][head[1]])
       
    
    def randomPoint(self):
        while not self.isPointAvaiable:
            x = random.randint(0, self.boardSize-1)
            y = random.randint(0, self.boardSize-1)
            if self.snake.count([x,y])==0:
                pygame.draw.rect(self.screen, self.colorRed, self.board[x][y])
                self.isPointAvaiable = True    
                self.point = [x,y]
                
    def colision(self):
        addPoint = False
        head = self.snake[0][:]
        if(self.direction==Direction.east):
            head[1]+=1
        elif(self.direction==Direction.north):
            head[0]-=1
        elif(self.direction==Direction.west):
            head[1]-=1
        elif(self.direction==Direction.south):
            head[0]+=1
        
        if head==self.point:
            addPoint = True
        elif self.snake.count(head)>0:
            self.done = True
        self.move(head, addPoint)
            
    #-----------------------------------------------------------------------------------------------
    
s = Snake()