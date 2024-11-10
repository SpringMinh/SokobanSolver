from ..interface.Sokoban import SokobanInterface
from ..content.Algorithm import Algorithm
from ..content.Node import Node
import os
import copy

class Sokoban(SokobanInterface):
    def __init__(self, Map):
        self.Map = Map
        self.currentMap = 0
        self.Algorithm = Algorithm()
        self.root = None
        self.direction_map = {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)}
        self.statBusy = False

    def setCurrentMap(self, id):
        self.currentMap = id
        if (self.Map[self.currentMap].exist):
            self.root = Node(None, self.Map[self.currentMap].boxPos, self.Map[self.currentMap].workerPosX, self.Map[self.currentMap].workerPosY)

    def DFS(self):
        goalNode, states, weights, directions, time_taken, peak_memory = self.Algorithm.DFS(self.root, self.Map[self.currentMap])
        if weights != -1:
            self.printOutput('DFS', states, goalNode.depth, weights, directions, time_taken, peak_memory)
        else:
            self.printOutput('DFS', states, None, weights, directions, time_taken, peak_memory)
            return [], []
        while (self.statBusy):
            continue
        self.statBusy = True
        self.statistics_init(directions)
        self.statBusy = False
        return self.generatePath(goalNode), self.statistics

    def BFS(self):
        goalNode, states, weights, directions, time_taken, peak_memory =  self.Algorithm.BFS(self.root, self.Map[self.currentMap])
        if weights != -1:
            self.printOutput('BFS', states, goalNode.depth, weights, directions, time_taken, peak_memory)
        else:
            self.printOutput('BFS', states, None, weights, directions, time_taken, peak_memory)
            return [], []
        while (self.statBusy):
            continue
        self.statBusy = True
        self.statistics_init(directions)
        self.statBusy = False
        return self.generatePath(goalNode), self.statistics
    
    def UCS(self):
        goalNode, states, weights, directions, time_taken, peak_memory =  self.Algorithm.UCS(self.root, self.Map[self.currentMap])
        if weights != -1:
            self.printOutput('UCS', states, goalNode.depth, weights, directions, time_taken, peak_memory)
        else:
            self.printOutput('UCS', states, None, weights, directions, time_taken, peak_memory)
            return [], []
        while (self.statBusy):
            continue
        self.statBusy = True
        self.statistics_init(directions)
        self.statBusy = False
        return self.generatePath(goalNode), self.statistics

    def Astar(self):
        goalNode, states, weights, directions, time_taken, peak_memory =  self.Algorithm.Astar(self.root, self.Map[self.currentMap])
        if weights != -1:
            self.printOutput('A*', states, goalNode.depth, weights, directions, time_taken, peak_memory)
        else:
            self.printOutput('A*', states, None, weights, directions, time_taken, peak_memory)
            return [], []
        while (self.statBusy):
            continue
        self.statBusy = True
        self.statistics_init(directions)
        self.statBusy = False
        return self.generatePath(goalNode), self.statistics

    def printOutput(self, Algo, states, steps, weights, directions, time_taken, peak_memory):
        filepath = "output/"
        filename = f"output-{self.currentMap:02d}.txt"
        outputfile = filepath + filename
        time_ms = int(time_taken * 1000)  # Convert seconds to milliseconds
        memory_mb = peak_memory / (1024 * 1024)  # Convert bytes to MB

        if weights == -1:
            output = (
                    f"{Algo}: Unsolvable\n Node: {states}, "
                    f"Time (ms): {time_ms}, Memory (MB): {memory_mb:.2f}\n"
            )
        else:
            output = (
                f"{Algo}\nSteps: {steps}, Weight: {weights}, Node: {states}, "
                f"Time (ms): {time_ms}, Memory (MB): {memory_mb:.2f}\n{directions}\n"
            )

        if os.path.exists(outputfile):
            with open(outputfile, 'r') as file:
                if Algo in file.read():
                    print(f"{Algo} already exists in {outputfile}, skipping append.")
                    return
        with open(outputfile, 'a') as file:
            file.write(output)

    def generatePath(self, node):
        path = []  # List to store the path

        # Traverse from the given node back to the root node
        while node is not None:
            path.append(node)  # Add the current node to the path
            node = node.parent  # Move up to the parent node

        # Since we gathered nodes from target to root, we reverse the path for correct order
        path.reverse()

        return path  # Return the full path from root to target node
    
    def statistics_init(self, directions):
        self.statistics = []
        boxPos = self.root.boxPos
        weights = self.Map[self.currentMap].boxWeights
        board = copy.deepcopy(self.Map[self.currentMap].board)
        Mainx = copy.deepcopy(self.root.workerPosX)
        Mainy = copy.deepcopy(self.root.workerPosY)
        n = len(board)
        m = len(board[0])
        cnt = 0
        
        for i in range(n):
            for j in range(m):
                if (i, j) in boxPos:
                    board[i][j] = weights[cnt]
                    cnt += 1
                if board[i][j] == ' ':
                    board[i][j] = 0
        cnt = 0
        total_cost = 0
        for c in directions:
            nextX = Mainx + self.direction_map[c.lower()][0]
            nextY = Mainy + self.direction_map[c.lower()][1]
            print(f"Step {cnt+1}: Direction: {c}, Next Position: ({nextX}, {nextY}), Weight: {board[nextX][nextY]}")
            cur_weight = board[nextX][nextY]
            Mainx = nextX
            Mainy = nextY
            if not c.islower():
                total_cost += board[nextX][nextY]
                board[nextX + self.direction_map[c.lower()][0]][nextY + self.direction_map[c.lower()][1]] = board[nextX][nextY]
                print(f"Step {cnt+1}: Weight: {cur_weight}, board next:{board[nextX][nextY]}, the next board next: {board[nextX + self.direction_map[c.lower()][0]][nextY + self.direction_map[c.lower()][1]]}")
                board[nextX][nextY] = 0
            total_cost += 1
            self.update_statistics(cnt, total_cost, cur_weight)
            cnt += 1

    def update_statistics(self, index, cur_cost, cur_weight):
        if index < len(self.statistics):
            self.statistics[index] = [cur_cost, cur_weight]
        else:
            self.statistics.append([cur_cost, cur_weight])

    def statistics_calculation(self, index):
        if index < len(self.statistics):
            return self.statistics[index]
        else:
            return [-1, -1]