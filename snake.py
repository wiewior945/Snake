import random
import math
import numpy as np

from direction import Direction
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts


class Snake(py_environment.PyEnvironment):

    debug_mode = False
    done = False
    board_size = 21
    reward_wrong_step = -3
    reward_correct_step = 1
    reward_point = 10
    rewardEndGame = -100
    point = []  # apple
    direction = Direction.east


    def debug(self, text):
        if self.debug_mode:
            print(text)

    def __init__(self):
        self.learningStep = 0
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(shape=(4,), dtype=np.float, minimum=-1., name='observation')
        self._reset()

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        filename = "E:\\Snake\\new\\" + str(self.learningStep) + ".txt"
        self.logFile = open(filename, "w+")
        self.done = False
        self.direction = Direction.east
        self.init_snake()
        self.random_point()
        observation = np.append(self.surroundings(self.snake[0]), self.calculate_angle())
        self.learningStep += 1
        return ts.restart(observation)

    # Action: 0 = go forward, 1 = go left, 2 = go right
    def _step(self, action):
        self.debug("--------------------------------------------")
        self.debug("Action: " + str(action))
        if(self.done):  # if true, it means that snake had a crash in previous step and game needs to be restarted
            self.debug("--- RESET ---")
            return self._reset()
        if(action!=0):
            self.changeDirection(action)
        self.debug("Direction: " + str(self.direction))
        colisionOutput = self.colision()
        observation = colisionOutput[0]
        observation = np.append(observation, colisionOutput[2])
        reward = colisionOutput[1]
        self.debug("Reward: " + str(reward))
        self.debug("Head: " + str(colisionOutput[1]))
        self.debug("Observation: " + str(observation))
        jsonString = '{"snake":' + str(self.snake) + ', "observations":' + str(observation.tolist()) + ', "reward":' + str(reward) + ', "apple":' + str(self.point) + '}'
        self.logFile.write(jsonString + "\n")
        if(self.done):  # if true, it means that move was illegal
            self.debug("@@@ koniec")
            return ts.termination(observation, reward)
        else:
            return ts.transition(observation, reward)


    def init_snake(self):
        self.snake = [[10, 11], [10, 10], [10, 9]]

    # action 1 = turn left, action 2 = turn right
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


    # add new head to the snake and cut snake's tail if apple has not been eaten
    def move(self, head, addPoint):
        if not addPoint:
            tail = self.snake[len(self.snake)-1][:]
            self.snake.remove(tail)
        self.snake.insert(0, head)
        if(addPoint):
            self.random_point()

    def random_point(self):
        isPointAvailable = False
        while not isPointAvailable:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if self.snake.count([x, y])==0:
                isPointAvailable = True
                self.point = [x, y]


    def surroundings(self, head):
        surroundings = np.array([], dtype=np.int32)
        if (self.direction == Direction.east):
            right = [head[0] + 1, head[1]]
            left = [head[0] - 1, head[1]]
            front = [head[0], head[1] + 1]
            if (self.snake.count(front) > 0 or front[1] >= self.board_size):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(left) > 0 or left[0] < 0):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(right) > 0 or right[0] >= self.board_size):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
        elif (self.direction == Direction.north):
            front = [head[0] - 1, head[1]]
            left = [head[0], head[1] - 1]
            right = [head[0], head[1] + 1]
            if (self.snake.count(front) > 0 or front[0] < 0):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(left) > 0 or left[1] < 0):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(right) > 0 or right[1] >= self.board_size):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
        elif (self.direction == Direction.west):
            front = [head[0], head[1] - 1]
            left = [head[0] + 1, head[1]]
            right = [head[0] - 1, head[1]]
            if (self.snake.count(front) > 0 or front[1] < 0):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(left) > 0 or left[0] >= self.board_size):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(right) > 0 or right[0] < 0):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
        elif (self.direction == Direction.south):
            front = [head[0] + 1, head[1]]
            left = [head[0], head[1] + 1]
            right = [head[0], head[1] - 1]
            if (self.snake.count(front) > 0 or front[0] >= self.board_size):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(left) > 0 or left[1] >= self.board_size):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
            if (self.snake.count(right) > 0 or right[1] < 0):
                surroundings = np.append(surroundings, 1)
            else:
                surroundings = np.append(surroundings, 0)
        return surroundings
    
    
    def calculate_angle(self):
        snakeVector = np.array(self.snake[0]) - np.array(self.snake[1])
        foodVector = np.array(self.point) - np.array(self.snake[0])
        a = snakeVector / np.linalg.norm(snakeVector)
        b = foodVector / np.linalg.norm(foodVector)
        angle = math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]) / math.pi
        return angle
    

    # returns: head surroundings, new snake's head and reward
    def colision(self):
        addPoint = False
        reward = 0
        head = self.snake[0][:]  # snake[0] is snake's head. [:] copies object's value, not its address. Head is new object with the same value as snake's head

        # changing new head coords according to snake's direction
        # establish reward which will be returned by function, based on approaching or moving away from apple
        if(self.direction==Direction.east):
            head[1] += 1
            if(self.point[1] >= head[1]):
                reward = self.reward_correct_step
            elif(self.point[1] < head[1]):
                reward = self.reward_wrong_step

        elif(self.direction==Direction.north):
            head[0] -= 1
            if(self.point[0] <= head[0]):
                reward = self.reward_correct_step
            elif(self.point[0] > head[0]):
                reward = self.reward_wrong_step

        elif(self.direction==Direction.west):
            head[1] -= 1
            if(self.point[1] <= head[1]):
                reward = self.reward_correct_step
            elif(self.point[1] > head[1]):
                reward = self.reward_wrong_step

        elif(self.direction==Direction.south):
            head[0] += 1
            if(self.point[0] >= head[0]):
                reward = self.reward_correct_step
            elif(self.point[0] < head[0]):
                reward = self.reward_wrong_step

        if head==self.point:  # whether new head is the same as apple coordinates
            addPoint = True
            reward = self.reward_point
        # if new head is the same as piece of snake's body or it's out of game board
        elif (self.snake.count(head) > 0 or head[0] < 0 or head[0] >= self.board_size or head[1] < 0 or head[1] >= self.board_size):
            self.done = True
            self.debug("-----------------koniec---------------------")
            self.debug(self.snake)
            self.debug("head")
            self.debug(head)
            return np.array([1, 1, 1]), self.rewardEndGame, -1.  # colision, so no need to calculate observations
        self.move(head, addPoint)
        surroundings = self.surroundings(self.snake[0])
        angle = self.calculate_angle()
        return surroundings, reward, angle