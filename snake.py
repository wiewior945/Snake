import pygame


done = False
#RGB colors:
colorWhite = (255, 255, 255)
rectSize = 30
rectMargin = 3
boardSize = 20  #number of printed rectangles in single line
windowSize = (boardSize*rectSize) + (boardSize*rectMargin) + rectMargin
board = []


#----------------------------------------------------------------------------------------------
# tworzy planszę, board to odpowiednik dwuwymiarowej tablicy z obiektami kwadratów
# druga pętla (j) tworzy poziomy rząd kwadratów, pierwsza pętla dodaje poziomy rząd do głównej tablicy planszy
def prepareBoard():
    coordTop = rectMargin
    for i in range(boardSize):
        boardLevel = []
        coordLeft = rectMargin
        for j in range(boardSize):
            boardLevel.append(pygame.draw.rect(screen, colorWhite, pygame.Rect(coordLeft, coordTop, rectSize, rectSize)))
            coordLeft += rectSize + rectMargin
        board.append(boardLevel)
        coordTop += rectSize + rectMargin
    
#-----------------------------------------------------------------------------------------------


pygame.init()
screen = pygame.display.set_mode((windowSize, windowSize))
prepareBoard()

while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                
        
        pygame.display.flip()
        