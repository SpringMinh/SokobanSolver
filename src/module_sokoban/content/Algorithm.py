from ..interface.Algorithm import AlgorithmInterface
from ..content.Node import Node
import copy
import tracemalloc
import time
from queue import PriorityQueue

class Algorithm(AlgorithmInterface):
    def __init__(self):
        self.direction_map = {(-1, 0): 'u', (1, 0): 'd', (0, -1): 'l', (0, 1): 'r'}

    def conf2str(self, node):
        # sorted_boxes = sorted(node.boxPos)

        return "".join(str(r) + str(',') + str(c) + str(';') for r, c in node.boxPos) + str('|') + str(node.workerPosX) + str(',') + str(node.workerPosY)

    def isGoal(self, node, map):
        return set(map.goalPos) == set(node.boxPos)
    
    def PBCheck(self, map, boxR, boxC, boxPos, parent, depth):
        board = map.board

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
                    lbox= self.PBCheck(map, boxR,boxC-1,boxPos,(boxR,boxC),depth+1)
                
            # Checking if Right box if free or not
            if (boxR,boxC+1) in boxPos:
                if (boxR,boxC+1) == parent:
                    rbox=True
                else:
                    rbox = self.PBCheck(map, boxR,boxC+1,boxPos,(boxR,boxC),depth+1)

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
                    ubox=self.PBCheck(map, boxR-1,boxC,boxPos,(boxR,boxC),depth+1)
                
            # Checking if lower(down) box if free or not
            if (boxR+1,boxC) in boxPos:
                if (boxR+1,boxC) == parent:
                    dbox=True
                else:
                    dbox = self.PBCheck(map, boxR+1,boxC,boxPos,(boxR,boxC),depth+1)

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

    def move(self, node, map):
        u=(-1,0)
        d=(1,0)
        l=(0,-1)
        r=(0,1)
        # moves=[(-1,0),(0,-1),(1,0),(0,1)]
        moves=[
            r,u,d,l
        ]
        result=[]

        for mv in moves:
            newWPX=node.workerPosX +mv[0]
            newWPY=node.workerPosY +mv[1]

            if map.board[newWPX][newWPY]=="#":
                continue

            elif map.board[newWPX][newWPY]==" ":
                
                boxIdx=-1

                #Finding which box will move
                for i in range(len(node.boxPos)):
                    if node.boxPos[i]==(newWPX,newWPY):
                        boxIdx=i

                if boxIdx==-1:
                    result.append((Node(node,node.boxPos,newWPX,newWPY),boxIdx,mv))
                    continue


                newBPX=newWPX+mv[0]
                newBPY=newWPY+mv[1]  

                if map.board[newBPX][newBPY]==" " and (newBPX,newBPY) not in node.boxPos:
                    newBoxPos=copy.deepcopy(node.boxPos)
                    newBoxPos[boxIdx]=(newBPX,newBPY)
                    result.append((Node(node,newBoxPos,newWPX,newWPY),boxIdx,mv))

                else:
                    continue

        return result

    def DFS(self, root, map):
        if not map.exist:
            return None, None, None, None, None, None

        tracemalloc.start()
        start_time = time.time()

        frontier = []
        explored = {}
        goal = map.goalPos
        weights = map.boxWeights
    
        frontier.append((root, 0, ""))
        counter = 0

        while len(frontier) > 0:
            
            node, path_weight, directions = frontier.pop(-1)
            # node.Print(self.sokoban)
            if counter%10000==0:
                print(counter)
                
            counter += 1            
            
            # Add current node to explored
            explored[self.conf2str(node)]=None

            # Check if current node is goal node
            if self.isGoal(node, map):
                end_time = time.time()
                _, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                time_taken = end_time - start_time
                return node,counter,path_weight,directions,time_taken,peak_memory

            # Find children of current node
            children=self.move(node, map)

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
                            if self.PBCheck(map, boxR,boxC,child.boxPos,(-1,-1),1):
                                flag=True
                                break
                    # deadlock -> prune the branch
                    if flag:
                        del(child)
                        continue
                    direction = self.direction_map[move]
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

        return None, counter, -1, "", time_taken, peak_memory
    
    def BFS(self, root, map):
        if not map.exist:
            return None, None, None, None, None, None
        
        tracemalloc.start()
        start_time = time.time()

        frontier = []
        explored = {}
        goal = map.goalPos
        weights = map.boxWeights

        frontier.append((root, 0, ""))  # Add the root node and initial weight 0
        counter = 0

        while len(frontier) > 0:
            
            node, path_weight, directions = frontier.pop(0)  # Pop from the front of the list for BFS
            if counter % 10000 == 0:
                print(counter)

            counter += 1

            # Add current node to explored
            explored[self.conf2str(node)] = None

            # Check if current node is goal node
            if self.isGoal(node, map):
                end_time = time.time()
                _, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                time_taken = end_time - start_time
                return node, counter, path_weight, directions, time_taken, peak_memory

            # Find children of current node
            children = self.move(node, map)

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
                            if self.PBCheck(map, boxR, boxC, child.boxPos, (-1, -1), 1):
                                flag = True
                                break
                    # deadlock -> prune the branch
                    if flag:
                        del(child)
                        continue
                    direction = self.direction_map[move]
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

        return None, counter, -1, "", time_taken, peak_memory
    
    def UCS(self, root, map):
        if not map.exist:
            return None, None, None, None, None, None

        tracemalloc.start()
        start_time = time.time()

        frontier = PriorityQueue()
        explored = {}
        goal = map.goalPos
        weights = map.boxWeights

        frontier.put((0, root, 0, ""))  # Add the root node with priority 0
        counter = 0

        explored[self.conf2str(root)] = 0

        while not frontier.empty():

            path_cost, node, path_weight, directions = frontier.get()

            if counter % 10000 == 0:
                print(counter)

            counter += 1

            # Calculate the unique configuration string for the current node
            configurationStr = self.conf2str(node)
            
            # If this configuration has been explored with a lower cost, skip this path
            # if configurationStr in explored and explored[configurationStr] <= path_weight:
            if explored[configurationStr] < path_cost:
                # print("already a better path!")
                continue

            # Add current node's configuration to explored with the minimum cost
            # explored[configurationStr] = path_weight

            # Check if the current node is the goal node
            if self.isGoal(node, map):
                end_time = time.time()
                _, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                time_taken = end_time - start_time
                return node, counter, path_weight, directions, time_taken, peak_memory

            # Find children of the current node
            children = self.move(node, map)

            for child, boxIdx, move in children:
                child_configurationStr = self.conf2str(child)
                
                # Check for deadlock in the child's configuration
                flag = False
                for (boxR, boxC) in child.boxPos:
                    if (boxR, boxC) not in goal:
                        if self.PBCheck(map, boxR, boxC, child.boxPos, (-1, -1), 1):
                            flag = True
                            break
                # deadlock -> prune the branch
                if flag:
                    del(child)
                    continue

                # Determine the direction and cost for this child
                direction = self.direction_map[move]
                if boxIdx == -1:
                    child_weight = 0
                    direction = direction.lower()
                else:
                    child_weight = weights[boxIdx]
                    direction = direction.upper()

                # Calculate total cost (path weight + step cost)
                total_path_weight = path_weight + child_weight  # Add step cost of 1 for each move

                # Only add child if it has not been explored with a lower cost
                # print("Direction: ", directions + direction, "Total: ", total_path_weight, " path: ", path_weight, " child: ", child_weight, "\n")
                # time.sleep(0.01)

                if child_configurationStr not in explored or explored[child_configurationStr] > total_path_weight + child.depth:
                    frontier.put((total_path_weight + child.depth, child, total_path_weight, directions + direction))
                    explored[child_configurationStr] = total_path_weight + child.depth

        
            # print("Frontier: ", frontier.queue, "\n")

        # If no solution is found, return the search metrics
        end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        time_taken = end_time - start_time

        return None, counter, -1, "", time_taken, peak_memory
    
    def heuristic(self, node, map):
        boxPos = copy.deepcopy(node.boxPos)
        weights = map.boxWeights
        goal = map.goalPos

        # Calculate the Manhattan distance between the worker and the closest box
        #closest_box_distance = min(abs(workerR - boxR) + abs(workerC - boxC) for boxR, boxC in boxPos)

        # Calculate the weighted Manhattan distance from each box to its closest goal
        cost = 0  # Start with the closest box distance for the worker
        for i, (boxR, boxC) in enumerate(boxPos):
            weight = weights[i] if i < len(weights) else 1  # Default weight of 1 if no specific weight provided
            min_goal_distance = min(abs(boxR - goalR) + abs(boxC - goalC) for goalR, goalC in goal)
            cost += weight * min_goal_distance

        return cost
    
    def Astar(self, root, map):
        if not map.exist:
            return None, None, None, None, None, None

        tracemalloc.start()
        start_time = time.time()

        frontier = PriorityQueue()
        explored = {}
        goal = map.goalPos
        weights = map.boxWeights

        frontier.put((0, root, 0, ""))
        counter = 0

        explored[self.conf2str(root)] = 0

        while not frontier.empty():

            # Get the node with the lowest cost
            path_cost, node, path_weight, directions = frontier.get()
            # node.Print(self.sokoban)
            if counter % 10000 == 0:
                print(counter)
                
            counter += 1

            # Add current node to explored
            configurationStr = self.conf2str(node)
            
            if explored[configurationStr] < path_cost:
                # print("already a better path!")
                continue
            
            # Check if current node is goal node
            if self.isGoal(node, map):
                end_time = time.time()
                _, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                time_taken = end_time - start_time
                return node, counter, path_weight, directions, time_taken, peak_memory
            
            # Find children of current node
            children = self.move(node, map)

            # Check for deadlock in all children's configuration which are not on goal pos
            # Calculate heuristic value for all valid child

            for child, boxIdx, move in children:
                child_configurationStr = self.conf2str(child)
                # flag-> false means current configuration has no deadlock and is default behaviour
                # If any box which is not on goal position and is permanently blocked, there is a deadlock
                flag = False
                for (boxR, boxC) in child.boxPos:
                    if (boxR, boxC) not in goal:
                        if self.PBCheck(map, boxR, boxC, child.boxPos, (-1, -1), 1):
                            flag = True
                            break
                # deadlock -> prune the branch
                if flag:
                    # del(child)
                    continue
                direction = self.direction_map[move]
                if boxIdx == -1:
                    child_weight = 0
                    direction = direction.lower()
                else:
                    child_weight = weights[boxIdx]
                    direction = direction.upper()
                total_path_weight = path_weight + child_weight
                # Calculate the cost of the child node
                child_cost = self.heuristic(child, map) + total_path_weight + child.depth

                if child_configurationStr not in explored or explored[child_configurationStr] > child_cost:
                    frontier.put((child_cost, child, total_path_weight, directions + direction))
                    explored[child_configurationStr] = child_cost

        end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        time_taken = end_time - start_time

        return None, counter, -1, "", time_taken, peak_memory