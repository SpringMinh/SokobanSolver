from env import Sokoban,Node
from queue import PriorityQueue
import copy
import time
import pygame
import sys
import tracemalloc
import os


class Agent:

    def __init__(self, sokoban):
        self.sokoban = sokoban
        self.frontier = PriorityQueue()
        self.explored = {}
        self.stack=[]
        self.lastnode = None

    def PBCheck(self, boxR,boxC, boxPos, parent,depth):
        board = self.sokoban.board
        goalPos = self.sokoban.goal

        if depth>len(boxPos):
            return True

        hBlocked=None
        vBlocked=None

        # Pakke Wale Status       
        # Horizontal check
        if (board[boxR][boxC-1]==" " and (boxR,boxC-1) not in boxPos) and (board[boxR][boxC+1]==" " and (boxR,boxC+1) not in boxPos):
            return False
        # vertical check
        elif (board[boxR-1][boxC]==" " and (boxR-1,boxC) not in boxPos) and (board[boxR+1][boxC]==" " and (boxR+1,boxC) not in boxPos):
            return False
        
        # checking for wall
        # wall in horizontal dir
        if board[boxR][boxC-1]=="#" or board[boxR][boxC+1]=="#":
            hBlocked=True
        # wall in vertical dir
        if board[boxR-1][boxC]=="#" or board[boxR+1][boxC]=="#":
            vBlocked=True


        # checking for boxes
        # Left or Right position containing box
        if not hBlocked and ((boxR,boxC-1) in boxPos or (boxR,boxC+1) in boxPos):
            
            # Checking if Left box if free or not.
            lbox=rbox=None
            if (boxR,boxC-1) in boxPos:
                if (boxR,boxC-1)==parent:
                    lbox=True
                else:
                    lbox= self.PBCheck(boxR,boxC-1,boxPos,(boxR,boxC),depth+1)
                
            # Checking if Right box if free or not
            if (boxR,boxC+1) in boxPos:
                if (boxR,boxC+1) == parent:
                    rbox=True
                else:
                    rbox = self.PBCheck(boxR,boxC+1,boxPos,(boxR,boxC),depth+1)

            # If both left and right boxes are movable(false) then return false
            # else return true
            # if lbox==False and rbox==False:
            if not (lbox or rbox):
                hBlocked=False
            else:
                hBlocked=True
        
        # box at up or down position
        if not vBlocked and ((boxR-1,boxC) in boxPos or (boxR+1,boxC) in boxPos):
            
            # Checking if upper box if free or not
            ubox=dbox=None
            if (boxR-1,boxC) in boxPos:
                if (boxR-1,boxC)==parent:
                    ubox=True
                else:
                    ubox=self.PBCheck(boxR-1,boxC,boxPos,(boxR,boxC),depth+1)
                
            # Checking if lower(down) box if free or not
            if (boxR+1,boxC) in boxPos:
                if (boxR+1,boxC) == parent:
                    dbox=True
                else:
                    dbox = self.PBCheck(boxR+1,boxC,boxPos,(boxR,boxC),depth+1)

            # If both up and down boxes are movable(false) then return false
            # else return true
            # if lbox==False and rbox==False:
            if not (ubox or dbox):
                vBlocked=False
            else:
                vBlocked=True
            
        # deadlock
        if hBlocked and vBlocked:
            return True
        else:
            return False

    def isGoal(self,node):
        goal=self.sokoban.goal
        boxPos=node.boxPos

        if set(goal)==set(boxPos):
            return True
        else:
            return False

    def heuristic(self,node,goal):
        boxPos=copy.deepcopy(node.boxPos)
        boxPos.sort(key = lambda x: x[0] + x[1])

        cost=0

        for i in range(len(boxPos)):
            cost+=abs(boxPos[i][0]-goal[i][0])+abs(boxPos[i][1]-goal[i][1])

        return cost


    def conf2str(self,node):
        """
           Function to convert boxPos and workerPos to string 
           This function is used for hashing of configuration
        """
        result=""

        srted=set(node.boxPos)

        for r,c in srted:
            result=result+str(r)+str(c)

        result=result+str(node.workerPosX)+str(node.workerPosY)

        return result


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
        if level < 10:
            filename = "output-0" + str(level) + ".txt"
        else:
            filename = "output-" + str(level) + ".txt"
        outputfile = filepath + filename
        time_ms = int(time_taken * 1000)  # Convert seconds to milliseconds
        memory_mb = peak_memory / (1024 * 1024)  # Convert bytes to MB
        output = f"{action}\n" \
                 f"Steps: {steps}, Weight: {weight}, Node: {counter}, " \
                 f"Time (ms): {time_ms}, Memory (MB): {memory_mb:.2f}\n" \
                 f"{directions}\n"
        if os.path.exists(outputfile):
            with open(outputfile, 'r') as file:
                content = file.read()
            # If the action already exists, skip appending
            if action in content:
                print(f"{action} already exists in {outputfile}, skipping append.")
                return
        else:
            content = ""
        
        # Append the new output to the file
        with open(outputfile, 'a') as file:
            file.write(output)

    def DFS(self):
        direction_map = {(-1, 0): 'u', (1, 0): 'd', (0, -1): 'l', (0, 1): 'r'}

        tracemalloc.start()
        start_time = time.time()

        self.frontier = []  # Clear the stack to start fresh
        self.explored = {}  # Clear the explored set

        frontier = self.stack
        explored = self.explored
        goal = self.sokoban.goal
        weights = self.sokoban.boxWeights
    
        frontier.append((self.sokoban.root,0,""))
        counter=0

        while len(frontier)>0:
            
            node, path_weight, directions = frontier.pop(-1)
            # node.Print(self.sokoban)
            if counter%10000==0:
                print(counter)
                
            counter+=1            
            
            # Add current node to explored
            explored[self.conf2str(node)]=None

            # Check if current node is goal node
            if self.isGoal(node):
                end_time = time.time()
                _, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                time_taken = end_time - start_time
                return node,counter,path_weight,directions,time_taken,peak_memory

            # Find children of current node
            children=self.sokoban.moves(node)

            # Check for deadlock in all children's configuration which are not on goal pos
            # Calculate heuristic value for all valid child
            # Push them to frontier
            for child, boxIdx, move in children:

                configurationStr = self.conf2str(child)
                if configurationStr not in explored:

                # flag-> false means current configuration has no deadlock and is default behaviour    
                # If any box which is not on goal position and is permanent blocked then there is a deadlock
                    flag=False
                    for (boxR,boxC) in child.boxPos:
                        if (boxR,boxC) not in goal:
                            if self.PBCheck(boxR,boxC,child.boxPos,(-1,-1),1):
                                flag=True
                                break
                    # deadlock -> prun the branch
                    if flag:
                        del(child)
                        continue
                    direction = direction_map[move]
                    if boxIdx==-1:
                        child_weight = 0
                        direction = direction.lower()
                    else:
                        child_weight = weights[boxIdx]
                        direction = direction.upper()
                    total_path_weight = path_weight + child_weight  # Update total weight with the current child's boxes
                    # print(total_path_weight, " ", path_weight, " ", child_weight, "\n")
                    # print(child.boxPos)
                    frontier.append((child, total_path_weight, directions + direction))

                # already visited (infinite loop)
                else:
                    del(child)
        
        end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        time_taken = end_time - start_time

        return None, counter, None, "", time_taken, peak_memory

    def BFS(self):
        direction_map = {(-1, 0): 'u', (1, 0): 'd', (0, -1): 'l', (0, 1): 'r'}

        tracemalloc.start()
        start_time = time.time()

        self.stack = []
        self.explored = {}

        frontier = self.stack
        explored = self.explored
        goal = self.sokoban.goal
        weights = self.sokoban.boxWeights

        frontier.append((self.sokoban.root, 0, ""))  # Add the root node and initial weight 0
        counter = 0

        while len(frontier) > 0:
            
            node, path_weight, directions = frontier.pop(0)  # Pop from the front of the list for BFS
            if counter % 10000 == 0:
                print(counter)

            counter += 1

            # Add current node to explored
            explored[self.conf2str(node)] = None

            # Check if current node is goal node
            if self.isGoal(node):
                end_time = time.time()
                _, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                time_taken = end_time - start_time
                return node, counter, path_weight, directions, time_taken, peak_memory

            # Find children of current node
            children = self.sokoban.moves(node)

            # Check for deadlock in all children's configuration which are not on goal pos
            # Calculate heuristic value for all valid child
            # Push them to frontier
            for child, boxIdx, move in children:

                configurationStr = self.conf2str(child)
                if configurationStr not in explored:

                    # flag-> false means current configuration has no deadlock and is default behaviour    
                    # If any box which is not on goal position and is permanently blocked, there is a deadlock
                    flag = False
                    for (boxR, boxC) in child.boxPos:
                        if (boxR, boxC) not in goal:
                            if self.PBCheck(boxR, boxC, child.boxPos, (-1, -1), 1):
                                flag = True
                                break
                    # deadlock -> prune the branch
                    if flag:
                        del(child)
                        continue
                    direction = direction_map[move]
                    # If no deadlock, calculate child weight and add to path weight
                    if boxIdx == -1:
                        child_weight = 0
                        direction = direction.lower()
                    else:
                        child_weight = weights[boxIdx]
                        direction = direction.upper()
                    total_path_weight = path_weight + child_weight  # Update total weight with the current child's boxes

                    frontier.append((child, total_path_weight, directions + direction))

                # Already visited (infinite loop prevention)
                else:
                    del(child)

        end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        time_taken = end_time - start_time   

        return None, counter, None, "", time_taken, peak_memory


    # [OLD]
    # def BFS(self):
    #     frontier = self.frontier
    #     explored = self.explored
    #     goal=self.sokoban.goal
    
    #     frontier.put(self.sokoban.root)
    #     counter=0

    #     while not frontier.empty():
            
    #         node = frontier.get()
    #         # node.Print(self.sokoban,"path.txt")
    #         if counter%10000==0:
    #             print(counter)
                
    #         counter+=1            
            
    #         # Add current node to explored
    #         explored[self.conf2str(node)]=None

    #         # Check if current node is goal node
    #         if self.isGoal(node):
    #             return node,counter

    #         # Find children of current node
    #         children=self.sokoban.moves(node)

    #         # Check for deadlock in all children's configuration which are not on goal pos
    #         # Calculate heuristic value for all valid child
    #         # Push them to frontier
    #         for child in children:

    #             configurationStr = self.conf2str(child)
    #             if configurationStr not in explored:

    #             # flag-> false means current configuration has no deadlock and is default behaviour    
    #             # If any box which is not on goal position and is permanent blocked then there is a deadlock
    #                 flag=False
    #                 for boxR,boxC in child.boxPos:
    #                     if (boxR,boxC) not in goal:
    #                         if self.PBCheck(boxR,boxC,child.boxPos,(-1,-1),1):
                                
    #                             flag=True
    #                             break
                            
    #                 if flag:
    #                     del(child)
    #                     continue
                    
    #                 # h(x) is included while computing cost -> A*
    #                 child.cost=self.heuristic(child,goal)+child.level     # cost = h(x) + g(x)
                    
    #                 # only g(x) is considered -> breadth first search
    #                 # child.cost=child.level
    #                 frontier.put(child)

    #             else:
    #                 del(child)
                
    #     return None

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

    # def run_algorithm(self, algorithm):
    #     if algorithm == "DFS":
    #         result, _, _ = self.DFS()
    #     elif algorithm == "BFS":
    #         result, _, _ = self.BFS()
    #     else:
    #         return []
    #     return self.printPath(result, "path.txt")  # Generate the path for visualization

    # def reset_state(self):
    #     # Reset the Sokoban board and other relevant states to their initial configuration.
    #     self.sokoban.reset()  # Assuming Sokoban has a reset method
    #     print("[+] Game state reset to initial configuration.")

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
        buttons = [
            button('black', margin, WINDOW_HEIGHT + 4, 36, 36, 'Prev', id='navLeft'),
            button('black', 2 * margin + 36, WINDOW_HEIGHT + 4, 36, 36, 'Next', id='navRight'),
            button('black', 3 * margin + 2 * 36, WINDOW_HEIGHT + 4, 36, 36, 'Auto', id='navAuto'),
            button('red', 4 * margin + 3 * 36, WINDOW_HEIGHT + 4, 36, 36, 'Reset', id='navReset'),

            button('black', margin, WINDOW_HEIGHT + 50, 36, 36, 'DFS', id='navDFS'),
            button('black', 2 * margin + 36, WINDOW_HEIGHT + 50, 36, 36, 'BFS', id='navBFS'),
            button('black', 3 * margin + 2 * 36, WINDOW_HEIGHT + 50, 36, 36, 'UCS', id='navUCS'),
            button('black', 4 * margin + 3 * 36, WINDOW_HEIGHT + 50, 36, 36, 'A*', id='navAstar')
        ]

        current_node = self.sokoban.root
        path = []
        current_index = 0
        autoplay = False
        autodelay = 100
        last_auto_update = pygame.time.get_ticks()

        # print("[+] Rendering graphics...")
        # i=0
        # choice = 1
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            # Draw the current state and check for button actions
            if path:
                current_node = path[current_index]
            else:
                current_node = self.sokoban.root
            self.drawGrid(current_node, buttons)

            if autoplay:
                if path:
                    action = self.handleButtons(choice = 0, buttons = buttons)
            else:
                action = self.handleButtons(choice = 1, buttons = buttons)
            # Handle actions based on button presses from drawGrid
            if action != 'NOTCLICKEDWHILEAUTO':  # Only process if valid action is returned
                path, current_index, autoplay = self.process_action(action, path, current_index, buttons, autoplay, level)
            
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

    # Helper function to handle actions
    def process_action(self, action, path, current_index, buttons, autoplay, level):
        if action == 'DFS':
            print("DFS selected")
            result, counter, weight, directions, time_taken, peak_memory = self.DFS()

        elif action == 'BFS':
            print("BFS selected")
            result, counter, weight, directions, time_taken, peak_memory = self.BFS()

        elif action == 'UCS':
            print("UCS selected")
            result, counter, weight, directions, time_taken, peak_memory  = self.UCS()

        elif action == 'ASTAR':
            print("A* selected")
            result, counter, weight, directions, time_taken, peak_memory  = self.Astar()

        elif action == 'RESET':
            print("Resetting to initial state")
            path = []
            self.drawGrid(self.sokoban.root, buttons)
            return [], 0, False

        elif action == -1:
            if path and current_index > 0:
                current_index -= 1
                autoplay = False
                # self.drawGrid(path[current_index], buttons)

        elif action == 1:
            if path and current_index < len(path) - 1:
                current_index += 1
                autoplay = False
                # self.drawGrid(path[current_index], buttons)

        elif action == 0:
            autoplay = not autoplay

        if action in ['DFS', 'BFS', 'UCS', 'ASTAR']:
            path = self.printPath(result, "path.txt")
            self.printOutput(action, counter, result.level, weight, directions, time_taken, peak_memory, level)
            print(f"{action}: Nodes explored: {counter}, Steps taken: {result.level}, Total weights pushed: {weight}, Time taken (s): {time_taken}, Memory usage (B): {peak_memory}")
            # self.draw_solution_path(path, buttons, autoplay = False)
            return path, 0, False  # Reset index after a new path is generated
        # if autoplay and path:
        #     pygame.time.delay(100)
        #     if current_index < len(path) - 1:
        #         current_index += 1
        #     else:
        #         autoplay = False  # Stop auto-play at the last state

        return path, current_index, autoplay  # Return updated path and index

    def drawGrid(self,node,buttons):
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

            for button in buttons:
                button.draw(display_surface, outline='white')

            pygame.display.update()
    
    def handleButtons(self, choice, buttons):
        # print("choice ", choice)
        if choice != 0:
            # Wait for a button press if not in auto-play mode
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        for btn in buttons:
                            if btn.isOver(pos):
                                # Return appropriate action based on button pressed
                                if btn.id == 'navLeft':
                                    return -1
                                elif btn.id == 'navRight':
                                    return 1
                                elif btn.id == 'navAuto':
                                    return 0  # Toggle auto-play mode
                                elif btn.id == 'navReset':
                                    print("Reset button clicked")
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
                    for btn in buttons:
                        if btn.isOver(pos):
                            # Return appropriate action for button clicks in auto mode
                            if btn.id == 'navLeft':
                                return -1
                            elif btn.id == 'navRight':
                                return 1
                            elif btn.id == 'navAuto':
                                return 0  # Toggle auto-play
                            elif btn.id == 'navReset':
                                print("Reset button clicked")
                                return 'RESET'

                if event.type == pygame.QUIT:
                    print("[+] Quitting...")
                    pygame.quit()
                    sys.exit()
            # In auto-play, return 0 to keep progressing unless a button event occurs
            return 'NOTCLICKEDWHILEAUTO'
            # [OLD!]
            # # Auto-play timing mechanism to allow the game to progress smoothly
            # start_time = time.time()
            # while True:
            #     current_time = time.time()
            #     elapsed_time = current_time - start_time

            #     if elapsed_time > 0.05:
            #         return 0  # Progress in auto-play mode after delay

            #     # Check for quit events and limited button actions
            #     for event in pygame.event.get():
            #         if event.type == pygame.MOUSEBUTTONDOWN:
            #             pos = pygame.mouse.get_pos()
            #             for btn in buttons:
            #                 if btn.isOver(pos):
            #                     # Return appropriate action for button clicks in auto mode
            #                     if btn.id == 'navLeft':
            #                         return -1
            #                     elif btn.id == 'navRight':
            #                         return 1
            #                     elif btn.id == 'navAuto':
            #                         return 0  # Toggle auto-play
            #                     elif btn.id == 'navReset':
            #                         print("Reset button clicked")
            #                         return 'RESET'

            #         if event.type == pygame.QUIT:
            #             print("[+] Quitting...")
            #             pygame.quit()
            #             sys.exit()
        


class button:
    def __init__(self, color, x,y,width,height, text='',id=None):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.id = id

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:

            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 15)
            text = font.render(self.text, 1, (255,255,255))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False