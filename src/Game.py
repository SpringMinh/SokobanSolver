from .GameInterface import GameInterface
from src.module_sokoban.zip import Map
from src.module_sokoban.zip import Sokoban
from src.module_display.zip import Button
from src.module_display.zip import EventManager
import pygame
import sys
import threading

class Game(GameInterface):
    def __init__(self):
        self.Map = []
        self.Map.append(None)
        self.WINDOW_WIDTH = 0
        self.WINDOW_HEIGHT = 0
        self.currentMapId = 0
        self.currentMap = None
        self.curPath = None
        self.curStat = None
        curMapID = 0
        for i in range (1,11):
            newMap = Map(i)
            self.Map.append(newMap)
            if (newMap.exist and curMapID == 0):
                curMapID = i
            self.WINDOW_WIDTH = max(self.WINDOW_WIDTH, len(newMap.board))
            self.WINDOW_HEIGHT = max(self.WINDOW_HEIGHT, len(newMap.board[0]))

        # Initialize pygame
        self.WINDOW_WIDTH *= 36
        self.WINDOW_HEIGHT *= 36
        self.BUTTON_WIDTH = 40  # Width of each button
        self.BUTTON_HEIGHT = 40 # Height of each button
        self.BUTTON_MARGIN = 20  # Space between buttons
        self.BUTTON_AREA_WIDTH = (self.BUTTON_WIDTH + self.BUTTON_MARGIN) * 5 + self.BUTTON_MARGIN  # Width for 5 buttons in a row
        
        self.WINDOW_WIDTH = self.WINDOW_WIDTH + self.BUTTON_AREA_WIDTH
        self.WINDOW_HEIGHT = max(self.WINDOW_HEIGHT, (self.BUTTON_HEIGHT + self.BUTTON_MARGIN) * 5 + self.BUTTON_MARGIN) + 90

        total_buttons = 10
        buttons_per_row = 2
        start_y = self.BUTTON_MARGIN
        start_x = self.BUTTON_MARGIN

        self.Buttons = []
        button_labels = [
            ('Prev', 'navLeft'), ('Next', 'navRight'), ('Auto', 'navAuto'), ('Reset', 'navReset'), ('DFS', 'navDFS'),
            ('BFS', 'navBFS'), ('UCS', 'navUCS'), ('A*', 'navAstar'), ('PMap', 'navPrev'), ('NMap', 'navNext')
        ]

        self.Sokoban = Sokoban(self.Map)
        self.EventManager = EventManager()
        self.BLACK = (0, 0, 0)

        pygame.display.set_caption('Sokoban')
        print("[+] Initializing game...")

        pygame.init()
        # self.SCREEN = pygame.display.set_mode((max(self.WINDOW_WIDTH,52), self.WINDOW_HEIGHT+50))
        self.CLOCK = pygame.time.Clock()
        # self.SCREEN.fill(self.BLACK)
        self.display_surface = pygame.display.set_mode((max(self.WINDOW_WIDTH, 52), self.WINDOW_HEIGHT))
        # self.margin = (max(self.WINDOW_WIDTH, 52) - (36 * 4)) / 5
        # self.Buttons = [
        #     Button('black', self.margin, self.WINDOW_HEIGHT + 4, 36, 36, 'white', 2, 12, 'white', 'Prev', id='navLeft'),
        #     Button('black', 2 * self.margin + 36, self.WINDOW_HEIGHT + 4, 36, 36, 'white', 2, 12, 'white', 'Next', id='navRight'),
        #     Button('black', 3 * self.margin + 2 * 36, self.WINDOW_HEIGHT + 4, 36, 36, 'white', 2, 12, 'white', 'Auto', id='navAuto'),
        #     Button('red', 4 * self.margin + 3 * 36, self.WINDOW_HEIGHT + 4, 36, 36, 'white', 2, 12, 'white', 'Reset', id='navReset'),
        #     Button('black', self.margin, self.WINDOW_HEIGHT + 50, 36, 36, 'white', 2, 12, 'white', 'DFS', id='navDFS'),
        #     Button('black', 2 * self.margin + 36, self.WINDOW_HEIGHT + 50, 36, 36, 'white', 2, 12, 'white', 'BFS', id='navBFS'),
        #     Button('black', 3 * self.margin + 2 * 36, self.WINDOW_HEIGHT + 50, 36, 36, 'white', 2, 12, 'white', 'UCS', id='navUCS'),
        #     Button('black', 4 * self.margin + 3 * 36, self.WINDOW_HEIGHT + 50, 36, 36, 'white', 2, 12, 'white', 'A*', id='navAstar')
        # ]
        for i in range(total_buttons):
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + col * (self.BUTTON_WIDTH + self.BUTTON_MARGIN)
            y = start_y + row * (self.BUTTON_HEIGHT + self.BUTTON_MARGIN)
            label, button_id = button_labels[i]
            if (label != 'Reset'):
                self.Buttons.append(Button('black', x, y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT, 'white', 2, 12, 'white', label, id=button_id))
            else: 
                self.Buttons.append(Button('red', x, y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT, 'white', 2, 12, 'white', label, id=button_id))

        self.wall = pygame.image.load('images\\wall.png').convert()
        self.box = pygame.image.load('images\\box.png').convert()
        self.box_on_target = pygame.image.load('images\\box_on_target.png').convert()
        self.player_on_target = pygame.image.load('images\\player_on_target.jpeg').convert()
        self.space = pygame.image.load('images\\space.png').convert()
        self.target = pygame.image.load('images\\target.png').convert()
        self.player = pygame.image.load('images\\player.png').convert()

        self.font = pygame.font.SysFont('comicsans', 16)
        self.blockSize = 36

        self.stepText = self.font.render('Steps: ', 1, 'white')
        self.costText = self.font.render('Current cost: ', 1, 'white')
        self.weightText = self.font.render('Weight being pushed: ', 1, 'white')
        self.doneText = self.font.render('', 1, 'white')
        self.stepPlainText = 'Steps: '
        self.costPlainText = 'Current cost: '
        self.weightPlainText = 'Weight being pushed: '
        self.donePos = (18, self.WINDOW_HEIGHT - 85)
        self.stepPos = (18, self.WINDOW_HEIGHT - 65)
        self.costPos = (18, self.WINDOW_HEIGHT - 45)
        self.weightPos = (18, self.WINDOW_HEIGHT - 25)

        # Initialize backend
        self.setCurrentMap(curMapID)
        self.pathDFS = []
        self.pathBFS = []
        self.pathUCS = []
        self.pathAstar = []
        self.statDFS = []
        self.statBFS = []
        self.statUCS = []
        self.statAstar = []
        self.current_index = 0
        self.current_Algo = ''
        self.DFS = True
        self.BFS = True
        self.UCS = True
        self.Astar = True

        # Initialize frontend status
        self.autoplay = False
        self.autodelay = 100
        self.last_auto_update = pygame.time.get_ticks()
        self.current_time = pygame.time.get_ticks()
        self.running = True

    def allowChangeLvl(self):
        return (self.DFS and self.BFS and self.UCS and self.Astar)
    
    def currentPath(self):
        if (self.current_Algo == 'DFS'):
            return self.pathDFS, self.statDFS
        elif (self.current_Algo == 'BFS'):
            return self.pathBFS, self.statBFS
        elif (self.current_Algo == 'UCS'):
            return self.pathUCS, self.statUCS
        elif (self.current_Algo == 'ASTAR'):
            return self.pathAstar, self.statAstar
        return [], []
    
    def hasCurrentPath(self):
        if (self.current_Algo == 'DFS'):
            return True
        elif (self.current_Algo == 'BFS'):
            return True
        elif (self.current_Algo == 'UCS'):
            return True
        elif (self.current_Algo == 'ASTAR'):
            return True
        return False

    def processEvent(self, event):
        if (event == 'QUIT'):
            print("[+] Quitting...")
            pygame.quit()
            sys.exit()
        elif (event == 'DFS'):
            if (not self.autoplay):
                self.current_Algo = event
                self.current_index = 0
                self.stepPlainText = 'Steps: '
                self.costPlainText = 'Current cost: '
                self.weightPlainText = 'Weight being pushed: '
                self.curPath = []
                self.curStat = []
            if (self.DFS and not self.pathDFS):
                self.DFS = False
                thread = threading.Thread(target = self.generatePath, args = ('DFS',))
                thread.start()
        elif (event == 'BFS'):
            if (not self.autoplay):
                self.current_Algo = event
                self.current_index = 0
                self.stepPlainText = 'Steps: '
                self.costPlainText = 'Current cost: '
                self.weightPlainText = 'Weight being pushed: '
                self.curPath = []
                self.curStat = []
            if (self.BFS and not self.pathBFS):
                self.BFS = False
                thread = threading.Thread(target = self.generatePath, args = ('BFS',))
                thread.start()
        elif (event == 'UCS'):
            if (not self.autoplay):
                self.current_Algo = event
                self.current_index = 0
                self.stepPlainText = 'Steps: '
                self.costPlainText = 'Current cost: '
                self.weightPlainText = 'Weight being pushed: '
                self.curPath = []
                self.curStat = []
            if (self.UCS and not self.pathUCS):
                self.UCS = False
                thread = threading.Thread(target = self.generatePath, args = ('UCS',))
                thread.start()
        elif (event == 'ASTAR'):
            if (not self.autoplay):
                self.current_Algo = event
                self.current_index = 0
                self.stepPlainText = 'Steps: '
                self.costPlainText = 'Current cost: '
                self.weightPlainText = 'Weight being pushed: '
                self.curPath = []
                self.curStat = []
            if (self.Astar and not self.pathAstar):
                self.Astar = False
                thread = threading.Thread(target = self.generatePath, args = ('ASTAR',))
                thread.start()
        elif (event == 'RESET'):
            self.current_index = 0
            self.autoplay = False
        elif (event == 'LEFT'):
            path = self.hasCurrentPath()
            if (path and self.current_index > 0):
                self.current_index -= 1
                self.autoplay = False
                self.stepText = self.font.render('Steps: ' + str(self.current_index), 1, 'white')
                self.costText = self.font.render('Current cost: ' + str(self.curStat[0]), 1, 'white')
                self.weightText = self.font.render('Weight being pushed: ' + str(self.curStat[1]), 1, 'white')
        elif (event == 'RIGHT'):
            path = self.hasCurrentPath()
            if (path and self.current_index < len(path) - 1):
                self.current_index += 1
                self.autoplay = True
                self.stepText = self.font.render('Steps: ' + str(self.current_index), 1, 'white')
                self.costText = self.font.render('Current cost: ' + str(self.curStat[0]), 1, 'white')
                self.weightText = self.font.render('Weight being pushed: ' + str(self.curStat[1]), 1, 'white')
        elif (event == 'TOGGLE_AUTO'):
            path = self.hasCurrentPath()
            if (path):
                self.autoplay = not self.autoplay
        elif (event == 'PREV'):
            if (not self.allowChangeLvl()):
                return
            newID = self.currentMapId - 1
            if (newID < 1):
                newID += 10
            self.setCurrentMap(newID)
            self.pathDFS = []
            self.pathBFS = []
            self.pathUCS = []
            self.pathAstar = []
            self.statDFS = []
            self.statBFS = []
            self.statUCS = []
            self.statAstar = []
            self.current_index = 0
            self.current_Algo = ''
            self.stepText = self.font.render('Steps: ', 1, 'white')
            self.costText = self.font.render('Current cost: ', 1, 'white')
            self.weightText = self.font.render('Weight being pushed: ', 1, 'white')
            self.doneText = self.font.render('', 1, 'white')
            self.stepPlainText = 'Steps: '
            self.costPlainText = 'Current cost: '
            self.weightPlainText = 'Weight being pushed: '
        elif (event == 'NEXT'):
            if (not self.allowChangeLvl()):
                return
            newID = self.currentMapId + 1
            if (newID > 10):
                newID -= 10
            self.setCurrentMap(newID)
            self.pathDFS = []
            self.pathBFS = []
            self.pathUCS = []
            self.pathAstar = []
            self.statDFS = []
            self.statBFS = []
            self.statUCS = []
            self.statAstar = []
            self.current_index = 0
            self.current_Algo = ''
            self.stepText = self.font.render('Steps: ', 1, 'white')
            self.costText = self.font.render('Current cost: ', 1, 'white')
            self.weightText = self.font.render('Weight being pushed: ', 1, 'white')
            self.doneText = self.font.render('', 1, 'white')
            self.stepPlainText = 'Steps: '
            self.costPlainText = 'Current cost: '
            self.weightPlainText = 'Weight being pushed: '

    def Run(self):
        while self.running:
            self.current_time = pygame.time.get_ticks()

            event = self.EventManager.pollEvent(self.Buttons)
            self.processEvent(event)

            if (not self.curPath):
                self.curPath, self.curStat = self.currentPath()
                if (self.current_Algo != ''):
                    self.doneText = self.font.render('Waiting for processing ...', 1, 'white')
                else:
                    self.doneText = self.font.render('', 1, 'white')

            if (self.curPath):
                self.doneText = self.font.render('Done!', 1, 'green')
                if (self.stepPlainText == 'Steps: '):
                    self.stepText = self.font.render('Steps: 0', 1, 'white')
                    self.stepPlainText = 'Steps: 0'
                if (self.costPlainText == 'Current cost: '):
                    self.costText = self.font.render('Current cost: 0', 1, 'white')
                    self.costPlainText = 'Current cost: 0'
                if (self.weightPlainText == 'Weight being pushed: '):
                    self.weightText = self.font.render('Weight being pushed: 0', 1, 'white')
                    self.weightPlainText = 'Weight being pushed: 0'
                if (self.autoplay and self.curPath and (self.current_time - self.last_auto_update > self.autodelay)):
                    if self.current_index < len(self.curPath) - 1:
                        self.current_index += 1
                        self.stepPlainText = 'Steps: ' + str(self.current_index)
                        self.costPlainText = 'Current cost: ' + str(self.curStat[self.current_index - 1][0])
                        self.weightPlainText = 'Weight being pushed: ' + str(self.curStat[self.current_index - 1][1])
                        self.stepText = self.font.render('Steps: ' + str(self.current_index), 1, 'white')
                        self.costText = self.font.render('Current cost: ' + str(self.curStat[self.current_index - 1][0]), 1, 'white')
                        self.weightText = self.font.render('Weight being pushed: ' + str(self.curStat[self.current_index - 1][1]), 1, 'white')
                    else:
                        self.autoplay = False  # Stop auto-play at end of path
                    self.last_auto_update = self.current_time  # Reset timer for next auto-play step

                self.currentNode = self.curPath[self.current_index]
            self.Draw()

    def generatePath(self, Algo):
        if (Algo == 'DFS'):
            self.pathDFS, self.statDFS = self.Sokoban.DFS()
            self.DFS = True
        elif (Algo == 'BFS'):
            self.pathBFS, self.statBFS = self.Sokoban.BFS()
            self.BFS = True
        elif (Algo == 'UCS'):
            self.pathUCS, self.statUCS = self.Sokoban.UCS()
            self.UCS = True
        elif (Algo == 'ASTAR'):
            self.pathAstar, self.statAstar = self.Sokoban.Astar()
            self.Astar = True
    
    def setCurrentMap(self, id):
        self.Sokoban.setCurrentMap(id)
        self.currentNode = self.Sokoban.root
        self.currentMapId = id
        self.currentMap = self.Map[id]

    def Draw(self):
        self.display_surface.fill(self.BLACK)
        board_start_x = self.BUTTON_AREA_WIDTH / 2
        for x in range(0, len(self.currentMap.board)*36, self.blockSize):
            for y in range(0, len(self.currentMap.board[0])*36, self.blockSize):

                screen_x = y + board_start_x
                screen_y = x

                # print(f"({x//blockSize},{y//blockSize})    ====>    {mat[x//blockSize][y//blockSize]}")
                if self.currentMap.board[x//self.blockSize][y//self.blockSize] == "#":
                    self.display_surface.blit(self.wall, (screen_x, screen_y))

                elif self.currentMap.board[x//self.blockSize][y//self.blockSize] == " ":
                    self.display_surface.blit(self.space, (screen_x, screen_y))
                
                if (x//self.blockSize, y//self.blockSize) in self.currentMap.goalPos:
                    self.display_surface.blit(self.target, (screen_x, screen_y))

                box_index = None
                if (x//self.blockSize,y//self.blockSize) in self.currentNode.boxPos :
                    # Find the box index
                    box_index = self.currentNode.boxPos.index((x // self.blockSize, y // self.blockSize))

                    if (x // self.blockSize, y // self.blockSize) in self.currentMap.goalPos:
                        self.display_surface.blit(self.box_on_target, (screen_x, screen_y))  # Use target image
                    else:
                        self.display_surface.blit(self.box, (screen_x, screen_y))  # Use regular box image
                    # Draw the box weight on top of the box
                    # White color for text and adjust position for visibility  
                    weight_text = self.font.render(str(self.currentMap.boxWeights[box_index]), True, (255, 255, 255))
                    text_rect = weight_text.get_rect(center=(screen_x + self.blockSize // 2, screen_y + self.blockSize // 2))  # Center in the box
                    self.display_surface.blit(weight_text, text_rect)  # Draw the centered text

                if (x//self.blockSize, y//self.blockSize) == (self.currentNode.workerPosX, self.currentNode.workerPosY):
                    self.display_surface.blit(self.player, (screen_x, screen_y))
                    if (x//self.blockSize,y//self.blockSize) in self.currentMap.goalPos:
                        self.display_surface.blit(self.player_on_target, (screen_x, screen_y))

        for Button in self.Buttons:
            Button.draw(self.display_surface)
        self.display_surface.blit(self.doneText, self.donePos)
        self.display_surface.blit(self.stepText, self.stepPos)
        self.display_surface.blit(self.costText, self.costPos)
        self.display_surface.blit(self.weightText, self.weightPos)
        
        pygame.display.update()
        