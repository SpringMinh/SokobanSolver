from ..interface.Map import MapInterface
import os

class Map(MapInterface):
    def __init__(self, level):
        self.exist = False
        self.board, self.boxWeights = self.get_level(level)
        self.workerPosX=None
        self.workerPosY=None
        self.boxPos =[]
        self.goalPos= []
        if self.board:
            self.exist = True
            for x in range(len(self.board)):
                for y in range(len(self.board[x])):
                    if self.board[x][y] == '@':
                        self.workerPosX=x
                        self.workerPosY=y
                        self.board[x][y]=' '
                    if self.board[x][y] == '$':
                        self.boxPos.append((x,y))
                        self.board[x][y]=' '
                    if self.board[x][y] =='.':
                        self.goalPos.append((x,y))
                        self.board[x][y]=' '
                    if self.board[x][y] == '+':
                        self.workerPosX=x
                        self.workerPosY=y
                        self.goalPos.append((x,y))
                        self.board[x][y]=' '
                    if self.board[x][y] == '*':
                        self.boxPos.append((x,y))
                        self.goalPos.append((x,y))
                        self.board[x][y]=' '

    def get_level(self, level):
        """ Get level from file """
        filepath = "levels/"
        if level < 10:
            filename = "input-0" + str(level) + ".txt"
        else:
            filename = "input-" + str(level) + ".txt"
        inputfile = filepath + filename
        if not os.path.exists(inputfile):
            print(f"File '{filename}' does not exist in '{filepath}'!")
            return None, None
        with open(inputfile, "r") as file:
            # Read the weights from the first line and store them as integers in a list
            weights = list(map(int, file.readline().strip().split()))

            # Read the rest of the file for the level layout
            allLevels = file.readlines()

        # Initialize variables to store the level layout
        maxSize = 0
        ll = [""] * len(allLevels)

        # Build the level matrix from the lines
        for i in range(len(allLevels)):
            tmp = allLevels[i].rstrip()  # Remove trailing spaces and newline characters
            ll[i] = tmp
            if len(ll[i]) > maxSize:
                maxSize = len(ll[i])

        # Adjust each row in the level layout to match the max width
        for i in range(len(ll)):
            if len(ll[i]) < maxSize:
                ll[i] += " " * (maxSize - len(ll[i]))

        # Convert the level layout into a 2D list of characters
        lll = []
        for row in ll:
            lll.append([char for char in row])

        # Return both the level matrix and the weights list
        return lll, weights

    