class SokobanInterface:
    def __init__(self, Map):
        pass

    def setCurrentMap(self, id):
        """Set current map """
        pass

    def DFS(self):
        """DFS generate state"""
        pass

    def BFS(self):
        """BFS generate state"""
        pass

    def UCS(self):
        """UCS generate state"""
        pass

    def Astar(self):
        """A* generate state"""
        pass

    def generatePath(self, node):
        """A function return path of algorithm"""
        pass

    def printOutput(self, Algo, states, steps, weights, directions, time_taken, peak_memory):
        """A function to print output"""
        pass

    def statistics_init(self, directions):
        """A function to generate statistics step by step"""
        pass

    def update_statistics(self, index, cur_cost, cur_weight):
        """Update step statistics function"""
        pass

    def statistics_calculation(self, index):
        """Get statistics"""
        pass