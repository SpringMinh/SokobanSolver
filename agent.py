import pygame
import sys
import os
class Agent:

    def __init__(self, sokoban, search):
        self.sokoban = sokoban
        self.search = search
        self.lastnode = None

    def is_valid_value(self,char):
        if ( char == ' ' or #floor
            char == '#' or #wall
            char == '@' or #worker on floor
            char == '.' or #goal
            char == '*' or #box on goal
            char == '$' or #box
            char == '+' ): #worker on goal
            return True
        else:
            return False
    
    def MakeLevel(self,filename,level):
        # self.queue = Queue.LifoQueue()
        self.matrix = []
        #        if level < 1 or level > 50:
        if level < 1:
            print ("ERROR: Level "+str(level)+" is out of range")
            sys.exit(1)
        else:
            file = open(filename,'r')
            level_found = False
            for line in file:
                row = []
                if not level_found:
                    if  "Level "+str(level) == line.strip():
                        level_found = True
                else:
                    if line.strip() != "":
                        row = []
                        for c in line:
                            if c != '\n' and self.is_valid_value(c):
                                row.append(c)
                            elif c == '\n': #jump to next row when newline
                                continue
                            else:
                                print ("ERROR: Level "+str(level)+" has invalid value "+c)
                                sys.exit(1)
                        self.matrix.append(row)
                    else:
                        break
            if not level_found:
                print ("ERROR: Level "+str(level)+" not found")
                sys.exit(1)
            file.close()
            return self.matrix
        
    def Interactive(self,level):
        board=self.sokoban.board

        BLACK = (0, 0, 0)
        WINDOW_HEIGHT = len(board)*36
        WINDOW_WIDTH = len(board[0])*36

        pygame.display.set_caption('Sokoban')
        print("[+] Initializing game...")

        pygame.init()
        SCREEN = pygame.display.set_mode((max(WINDOW_WIDTH,52), WINDOW_HEIGHT+50))
        # display_surface = pygame.display.set_mode((max(WINDOW_WIDTH,52), WINDOW_HEIGHT+50))
        CLOCK = pygame.time.Clock()
        SCREEN.fill(BLACK)

        margin = (max(WINDOW_WIDTH, 52) - (36 * 4)) / 5
        Buttons = [
            Button('black', margin, WINDOW_HEIGHT + 4, 36, 36, 'Prev', id='navLeft'),
            Button('black', 2 * margin + 36, WINDOW_HEIGHT + 4, 36, 36, 'Next', id='navRight'),
            Button('black', 3 * margin + 2 * 36, WINDOW_HEIGHT + 4, 36, 36, 'Auto', id='navAuto'),
            Button('red', 4 * margin + 3 * 36, WINDOW_HEIGHT + 4, 36, 36, 'Reset', id='navReset'),

            Button('black', margin, WINDOW_HEIGHT + 50, 36, 36, 'DFS', id='navDFS'),
            Button('black', 2 * margin + 36, WINDOW_HEIGHT + 50, 36, 36, 'BFS', id='navBFS'),
            Button('black', 3 * margin + 2 * 36, WINDOW_HEIGHT + 50, 36, 36, 'UCS', id='navUCS'),
            Button('black', 4 * margin + 3 * 36, WINDOW_HEIGHT + 50, 36, 36, 'A*', id='navAstar')
        ]

        current_node = self.sokoban.root
        path = []
        current_index = 0
        autoplay = False
        autodelay = 100
        last_auto_update = pygame.time.get_ticks()

        running = True
        while running:
            current_time = pygame.time.get_ticks()
            # Draw the current state and check for Button actions
            if path:
                current_node = path[current_index]
            else:
                current_node = self.sokoban.root
            self.drawGrid(current_node, Buttons)

            if autoplay:
                if path:
                    action = self.handleButtons(choice = 0, Buttons = Buttons)
            else:
                action = self.handleButtons(choice = 1, Buttons = Buttons)
            # Handle actions based on Button presses from drawGrid
            if action != 'NOTCLICKEDWHILEAUTO':  # Only process if valid action is returned
                path, current_index, autoplay = self.process_action(action, path, current_index, Buttons, autoplay, level)
            
            if autoplay and path and (current_time - last_auto_update > autodelay):
                if current_index < len(path) - 1:
                    current_index += 1
                else:
                    autoplay = False  # Stop auto-play at end of path
                last_auto_update = current_time  # Reset timer for next auto-play step

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("[+] Quitting...")
                    pygame.quit()
                    sys.exit()

    def printPath(self, node, filename):
        path = []  # List to store the path
        result = []  # List to store the result in the correct order

        # Traverse from the given node back to the root node
        while node is not None:
            path.append(node)  # Add the current node to the path
            node = node.parent  # Move up to the parent node

        # Since we gathered nodes from target to root, we reverse the path for correct order
        path.reverse()

        # Print each node in the correct order and collect it in the result list
        for step in path:
            step.Print(self.sokoban, filename)
            result.append(step)

        return result  # Return the full path from root to target node
    
    def printOutput(self, action, counter, steps, weight, directions, time_taken, peak_memory, level):
        filepath = "output/"
        filename = f"output-{level:02d}.txt"
        outputfile = filepath + filename
        time_ms = int(time_taken * 1000)  # Convert seconds to milliseconds
        memory_mb = peak_memory / (1024 * 1024)  # Convert bytes to MB

        output = (
            f"{action}\n"
            f"Steps: {steps}, Weight: {weight}, Node: {counter}, "
            f"Time (ms): {time_ms}, Memory (MB): {memory_mb:.2f}\n"
            f"{directions}\n"
        )

        if os.path.exists(outputfile):
            with open(outputfile, 'r') as file:
                if action in file.read():
                    print(f"{action} already exists in {outputfile}, skipping append.")
                    return
        with open(outputfile, 'a') as file:
            file.write(output)

    # Helper function to handle actions
    def process_action(self, action, path, current_index, Buttons, autoplay, level):
        if action == 'DFS':
            print("DFS selected")
            result, counter, weight, directions, time_taken, peak_memory = self.search.DFS()

        elif action == 'BFS':
            print("BFS selected")
            result, counter, weight, directions, time_taken, peak_memory = self.search.BFS()

        elif action == 'UCS':
            print("UCS selected")
            result, counter, weight, directions, time_taken, peak_memory  = self.search.UCS()

        elif action == 'ASTAR':
            print("A* selected")
            result, counter, weight, directions, time_taken, peak_memory  = self.search.Astar()

        elif action == 'RESET':
            print("Resetting to initial state")
            path = []
            self.drawGrid(self.sokoban.root, Buttons)
            return [], 0, False

        elif action == -1:
            if path and current_index > 0:
                current_index -= 1
                autoplay = False
                # self.drawGrid(path[current_index], Buttons)

        elif action == 1:
            if path and current_index < len(path) - 1:
                current_index += 1
                autoplay = False
                # self.drawGrid(path[current_index], Buttons)

        elif action == 0:
            autoplay = not autoplay

        if action in ['DFS', 'BFS', 'UCS', 'ASTAR']:
            path = self.printPath(result, "path.txt")
            self.printOutput(action, counter, result.level, weight, directions, time_taken, peak_memory, level)
            print(f"{action}: Nodes explored: {counter}, Steps taken: {result.level}, Total weights pushed: {weight}, Time taken (s): {time_taken}, Memory usage (B): {peak_memory}")
            # self.draw_solution_path(path, Buttons, autoplay = False)
            return path, 0, False  # Reset index after a new path is generated

        return path, current_index, autoplay  # Return updated path and index

    def drawGrid(self,node,Buttons):
        if not hasattr(self, 'lastnode') or self.lastnode != node:
            self.lastnode = node
            board=self.sokoban.board

            if not hasattr(self, 'display_surface'):
                WINDOW_HEIGHT = len(board)*36
                WINDOW_WIDTH = len(board[0])*36

                display_surface = pygame.display.set_mode((max(WINDOW_WIDTH,52), WINDOW_HEIGHT+100))

            # Load level images
            wall = pygame.image.load('images\\wall.png').convert()
            box = pygame.image.load('images\\box.png').convert()
            box_on_target = pygame.image.load('images\\box_on_target.png').convert()
            player_on_target = pygame.image.load('images\\player_on_target.jpeg').convert()
            space = pygame.image.load('images\\space.png').convert()
            target = pygame.image.load('images\\target.png').convert()
            player = pygame.image.load('images\\player.png').convert()

            margin=(max(WINDOW_WIDTH,52)-(36*4))/5
        
            font = pygame.font.SysFont(None, 24)

            blockSize = 36  # Set the size of the grid block

            for x in range(0, WINDOW_HEIGHT, blockSize):
                for y in range(0, WINDOW_WIDTH, blockSize):

                    # print(f"({x//blockSize},{y//blockSize})    ====>    {mat[x//blockSize][y//blockSize]}")
                    if board[x//blockSize][y//blockSize] == "#":
                        display_surface.blit(wall, (y, x))

                    elif board[x//blockSize][y//blockSize] == " ":
                        display_surface.blit(space, (y, x))
                    
                    if (x//blockSize,y//blockSize) in self.sokoban.goal:
                        display_surface.blit(target, (y, x))

                    box_index = None
                    if (x//blockSize,y//blockSize) in node.boxPos :
                        # Find the box index
                        box_index = node.boxPos.index((x // blockSize, y // blockSize))

                        if (x // blockSize, y // blockSize) in self.sokoban.goal:
                            display_surface.blit(box_on_target, (y, x))  # Use target image
                        else:
                            display_surface.blit(box, (y, x))  # Use regular box image
                        # Draw the box weight on top of the box
                        # White color for text and adjust position for visibility  
                        weight_text = font.render(str(self.sokoban.boxWeights[box_index]), True, (255, 255, 255))
                        text_rect = weight_text.get_rect(center=(y + blockSize // 2, x + blockSize // 2))  # Center in the box
                        display_surface.blit(weight_text, text_rect)  # Draw the centered text

                    if (x//blockSize,y//blockSize) == (node.workerPosX,node.workerPosY):
                        display_surface.blit(player, (y, x))
                        if (x//blockSize,y//blockSize) in self.sokoban.goal:
                            display_surface.blit(player_on_target, (y, x))

            for Button in Buttons:
                Button.draw(display_surface, outline='white')

            pygame.display.update()
    
    def handleButtons(self, choice, Buttons):
        if choice != 0:
            # Wait for a Button press if not in auto-play mode
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        for btn in Buttons:
                            if btn.isOver(pos):
                                # Return appropriate action based on Button pressed
                                if btn.id == 'navLeft':
                                    return -1
                                elif btn.id == 'navRight':
                                    return 1
                                elif btn.id == 'navAuto':
                                    return 0  # Toggle auto-play mode
                                elif btn.id == 'navReset':
                                    print("Reset Button clicked")
                                    return 'RESET'
                                elif btn.id == 'navDFS':
                                    print("DFS algorithm chosen")
                                    return 'DFS'
                                elif btn.id == 'navBFS':
                                    print("BFS algorithm chosen")
                                    return 'BFS'
                                elif btn.id == 'navUCS':
                                    print("UCS algorithm chosen")
                                    return 'UCS'
                                elif btn.id == 'navAstar':
                                    print("A* algorithm chosen")
                                    return 'ASTAR'

                    if event.type == pygame.QUIT:
                        print("[+] Quitting...")
                        pygame.quit()
                        sys.exit()

        else:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for btn in Buttons:
                        if btn.isOver(pos):
                            # Return appropriate action for Button clicks in auto mode
                            if btn.id == 'navLeft':
                                return -1
                            elif btn.id == 'navRight':
                                return 1
                            elif btn.id == 'navAuto':
                                return 0  # Toggle auto-play
                            elif btn.id == 'navReset':
                                print("Reset Button clicked")
                                return 'RESET'

                if event.type == pygame.QUIT:
                    print("[+] Quitting...")
                    pygame.quit()
                    sys.exit()
            # In auto-play, return 0 to keep progressing unless a Button event occurs
            return 'NOTCLICKEDWHILEAUTO'
class Button:
    def __init__(self, color, x,y,width,height, text='',id=None):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.id = id
        self.font = pygame.font.SysFont('comicsans', 12)

    def draw(self,win,outline=None):
        #Call this method to draw the Button on the screen
        if outline:

            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            text_x = self.x + (self.width - text_surface.get_width()) // 2
            text_y = self.y + (self.height - text_surface.get_height()) // 2
            win.blit(text_surface, (text_x, text_y))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height