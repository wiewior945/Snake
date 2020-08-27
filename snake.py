# @@@ import pygame
import random
import numpy as np

from direction import Direction
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts


class Snake(py_environment.PyEnvironment):

    debugMode = False
    # speed = 500  # przerwa pomiędzu ruchami węża w ms (szybkosć węża)
    done = False
    # RGB colors:
    # colorWhite = (255, 255, 255)
    # colorBlack = (0, 0, 0)
    # colorRed = (255, 0, 0)
    # rectSize = 30
    # rectMargin = 3
    boardSize = 21  # number of printed rectangles in single line
    # windowSize = (boardSize*rectSize) + (boardSize*rectMargin) + rectMargin
    rewardWrongStep = -1
    rewardCorrectStep = 1
    rewardPoint = 100
    rewardEndGame = -100
    #board = []
    point = []  # czerwony punkt
    direction = Direction.east
    # @@@ screen = pygame.display.set_mode((windowSize, windowSize))


    def debug(self, text):
        if self.debugMode:
            print(text)

    def __init__(self):
        self.learningStep = 0
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(shape=(5, 2), dtype=np.int32, minimum=0, name='observation')
        self._reset()
        # to na dole to jakby się chciało ręcznie poklikać
        # pygame.init()
        # while(True):
        #     inp = input()
        #     action = np.array(inp, dtype=np.int32)
        #     self._step(action)
        #     pygame.display.flip()
        #     pygame.time.delay(1000)

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        filename = "logs\\new\\" + str(self.learningStep) + ".txt"
        self.logFile = open(filename, "w+")
        self.done = False
        #self.board = []
        self.direction = Direction.east
        #self.initBoard()
        self.initSnake()
        self.randomPoint()
        observation = np.array([[0, 0], [1, 0], [2, 0], [10, 11], self.point], dtype=np.int32)
        self.learningStep += 1
        return ts.restart(observation)

    # Action: 0 = nic, 1 = w lewo, 2 = w prawo
    def _step(self, action):
        self.debug("--------------------------------------------")
        self.debug("Action: " + str(action))
        if(self.done):  # jeśli tutaj jest true to oznacza, że w poprzednim kroku było zderzenie i jest reset gry
            self.debug("--- RESET ---")
            return self._reset()
        if(action!=0):  # jeśli coś innego od 0 to agent chce zmienić kierunek węża
            self.changeDirection(action)
        self.debug("Direction: " + str(self.direction))
        colisionOutput = self.colision() # przesunięcie węża, zwraca otoczenie głowy[0], głowę[1] i nagrodę[2]
        observation = colisionOutput[0]
        observation = np.vstack((observation, colisionOutput[1]))
        observation = np.vstack((observation, self.point))
        reward = colisionOutput[2]
        self.debug("Reward: " + str(reward))
        self.debug("Head: " + str(colisionOutput[1]))
        self.debug("Observation: " + str(observation))
        jsonString = '{"snake":' + str(self.snake) + ', "observations":' + str(observation.tolist()) + ', "reward":' + str(reward) + ', "apple":' + str(self.point) + '}'
        if(self.done):  # true jest jeśli doszło do zderzenia
            return ts.termination(observation, reward)
        else:
            self.logFile.write(jsonString + "\n")
            return ts.transition(observation, reward)


    # tworzy planszę, board to odpowiednik dwuwymiarowej tablicy z obiektami kwadratów
    # druga pętla (j) tworzy poziomy rząd kwadratów, pierwsza pętla dodaje poziomy rząd do głównej tablicy planszy
    def initBoard(self):
        coordTop = self.rectMargin
        for i in range(self.boardSize):
            boardLevel = []
            coordLeft = self.rectMargin
            for j in range(self.boardSize):
                # @@@ boardLevel.append(pygame.draw.rect(self.screen, self.colorWhite, pygame.Rect(coordLeft, coordTop, self.rectSize, self.rectSize)))
                coordLeft += self.rectSize + self.rectMargin
            self.board.append(boardLevel)
            coordTop += self.rectSize + self.rectMargin


    def initSnake(self):
        self.snake = [[10,11], [10,10], [10,9]]
        # @@@ pygame.draw.rect(self.screen, self.colorBlack, self.board[self.snake[0][0]][self.snake[0][1]])
        # @@@ pygame.draw.rect(self.screen, self.colorBlack, self.board[self.snake[1][0]][self.snake[1][1]])
        # @@@ pygame.draw.rect(self.screen, self.colorBlack, self.board[self.snake[2][0]][self.snake[2][1]])

    # action 1 = lewo, action 2 = prawo
    def changeDirection(self, action):
        if(self.direction == Direction.east):
            if(action == 1):
                self.direction = Direction.north
            elif(action == 2):
                self.direction = Direction.south
        elif(self.direction == Direction.south):
            if(action == 1):
                self.direction = Direction.east
            elif(action == 2):
                self.direction = Direction.west
        elif(self.direction == Direction.west):
            if(action == 1):
                self.direction = Direction.south
            elif(action == 2):
                self.direction = Direction.north
        elif(self.direction == Direction.north):
            if(action == 1):
                self.direction = Direction.west
            elif(action == 2):
                self.direction = Direction.east


    # rysuje głowę w nowym miejscu i ucina ogon lub go zostawia jeśli nowa głowa jest równa jabłku
    def move(self, head, addPoint):
        if not addPoint:  # jeśli zjadł jabłko to nie ucinam ogona
            tail = self.snake[len(self.snake)-1][:]   # [:] oznacza, że kopiujemy wartosc obiektu, a nie jego adres, a to jest tutaj ważne
            # @@@ pygame.draw.rect(self.screen, self.colorWhite, self.board[tail[0]][tail[1]])
            self.snake.remove(tail)
        self.snake.insert(0,head)  # dodaje do węża głowę w nowym miejscu
        # @@@ pygame.draw.rect(self.screen, self.colorBlack, self.board[head[0]][head[1]]) #rysuje głowę w nowym miejscu
        if(addPoint):
            self.randomPoint()

    def randomPoint(self):
        isPointAvailable = False
        while not isPointAvailable:
            x = random.randint(0, self.boardSize-1)
            y = random.randint(0, self.boardSize-1)
            if self.snake.count([x, y])==0:
                # @@@ pygame.draw.rect(self.screen, self.colorRed, self.board[x][y])
                isPointAvailable = True
                self.point = [x,y]


    def surroundings(self, head):
        surroundings = np.array([99, 99], dtype=np.int32)  # te wartości 99 są tylko do stworzenia tablicy i nadania jej odpowiedniego shape, bez tego tablica nie chciała się zainicjalizować. Na końcu metody te wartości są usunięte

        # poniżej przesuwa nową głowę odpowiednio do obecnego kierunku
        # ustala nagrodę w zależności od zbliżania się do jabłka lub oddalania się od niego
        if (self.direction == Direction.east):
            right = [head[0] + 1, head[1]]
            left = [head[0] - 1, head[1]]
            front = [head[0], head[1] + 1]
            if (self.snake.count(front) > 0 or front[1] >= self.boardSize):
                surroundings = np.vstack((surroundings, [0, 1]))
            else:
                surroundings = np.vstack((surroundings, [0, 0]))
            if (self.snake.count(left) > 0 or left[0] < 0):
                surroundings = np.vstack((surroundings, [1, 1]))
            else:
                surroundings = np.vstack((surroundings, [1, 0]))
            if (self.snake.count(right) > 0 or right[0] >= self.boardSize):
                surroundings = np.vstack((surroundings, [2, 1]))
            else:
                surroundings = np.vstack((surroundings, [2, 0]))
        elif (self.direction == Direction.north):
            front = [head[0] - 1, head[1]]
            left = [head[0], head[1] - 1]
            right = [head[0], head[1] + 1]
            if (self.snake.count(front) > 0 or front[0] < 0):
                surroundings = np.vstack((surroundings, [0, 1]))
            else:
                surroundings = np.vstack((surroundings, [0, 0]))
            if (self.snake.count(left) > 0 or left[1] < 0):
                surroundings = np.vstack((surroundings, [1, 1]))
            else:
                surroundings = np.vstack((surroundings, [1, 0]))
            if (self.snake.count(right) > 0 or right[1] >= self.boardSize):
                surroundings = np.vstack((surroundings, [2, 1]))
            else:
                surroundings = np.vstack((surroundings, [2, 0]))
        elif (self.direction == Direction.west):
            front = [head[0], head[1] - 1]
            left = [head[0] + 1, head[1]]
            right = [head[0] - 1, head[1]]
            if (self.snake.count(front) > 0 or front[1] < 0):
                surroundings = np.vstack((surroundings, [0, 1]))
            else:
                surroundings = np.vstack((surroundings, [0, 0]))
            if (self.snake.count(left) > 0 or left[0] >= self.boardSize):
                surroundings = np.vstack((surroundings, [1, 1]))
            else:
                surroundings = np.vstack((surroundings, [1, 0]))
            if (self.snake.count(right) > 0 or right[0] < 0):
                surroundings = np.vstack((surroundings, [2, 1]))
            else:
                surroundings = np.vstack((surroundings, [2, 0]))
        elif (self.direction == Direction.south):
            front = [head[0] + 1, head[1]]
            left = [head[0], head[1] + 1]
            right = [head[0], head[1] - 1]
            if (self.snake.count(front) > 0 or front[0] >= self.boardSize):
                surroundings = np.vstack((surroundings, [0, 1]))
            else:
                surroundings = np.vstack((surroundings, [0, 0]))
            if (self.snake.count(left) > 0 or left[1] >= self.boardSize):
                surroundings = np.vstack((surroundings, [1, 1]))
            else:
                surroundings = np.vstack((surroundings, [1, 0]))
            if (self.snake.count(right) > 0 or right[1] < 0):
                surroundings = np.vstack((surroundings, [2, 1]))
            else:
                surroundings = np.vstack((surroundings, [2, 0]))
        surroundings = np.delete(surroundings, 0, axis=0)  # usunięcie pierwszego wiersza ([99, 99]), który był potrzebny do zainicjowania tablicy
        return surroundings

    # zwraca: otoczenie głowy (w którą stronę można wykonać ruch bez kolizjii), głowę i nagrodę
    def colision(self):
        addPoint = False
        reward = 0
        head = self.snake[0][:]  # snake[0] to głowa węża. [:] kopiuje wartość obiektu, a nie jego adres. Head jest nowym obiektem z taką samą wartością jak głowa węża.

        # poniżej przesuwa nową głowę odpowiednio do obecnego kierunku
        # ustala nagrodę w zależności od zbliżania się do jabłka lub oddalania się od niego
        if(self.direction==Direction.east):
            head[1] += 1
            if(self.point[1] >= head[1]):
                reward = self.rewardCorrectStep
            elif(self.point[1] < head[1]):
                reward = self.rewardWrongStep

        elif(self.direction==Direction.north):
            head[0] -= 1
            if(self.point[0] <= head[0]):
                reward = self.rewardCorrectStep
            elif(self.point[0] > head[0]):
                reward = self.rewardWrongStep

        elif(self.direction==Direction.west):
            head[1] -= 1
            if(self.point[1] <= head[1]):
                reward = self.rewardCorrectStep
            elif(self.point[1] > head[1]):
                reward = self.rewardWrongStep

        elif(self.direction==Direction.south):
            head[0] += 1
            if(self.point[0] >= head[0]):
                reward = self.rewardCorrectStep
            elif(self.point[0] < head[0]):
                reward = self.rewardWrongStep

        if head==self.point:  # jeśli nowa głowa jest równa koordynatom jabłka
            addPoint = True
            reward = self.rewardPoint
        # jeśli nowa głowa znajduje się w ciele węża lub jeśli wyjedzie poza planszę
        elif (self.snake.count(head) > 0 or head[0] < 0 or head[0] >= self.boardSize or head[1] < 0 or head[1] >= self.boardSize):
            self.done = True
            return np.array([[0, 1], [1, 1], [2, 1]]), head, self.rewardEndGame  # kolizja więc nie potrzeba dalej rysować
        self.move(head, addPoint)
        surroundings = self.surroundings(self.snake[0])
        return surroundings, head, reward