class AlgorithmInterface:
    def __init__():
        pass

    def conf2str(self,node):
        """
        Convert configuration to a unique, consistent string representation.
        Uses sorted tuple of box positions to ensure consistent ordering.
        """
        pass

    def PBCheck(self, boxR, boxC, boxPos, parent, depth):
        """Checker for permanently blocked state"""
        pass

    def move(self, node, map):
        """Generate neighbor state from a state"""
        pass
        
    def DFS(self, root, map):
        """DFS generate state"""
        pass

    def BFS(self, root, map):
        """BFS generate state"""
        pass

    def UCS(self, root, map):
        """UCS generate state"""
        pass

    def heuristic(self, node, map):
        """Heuristic estimated"""
        pass       

    def Astar(self, root, map):
        """A* generate state"""
        pass

    def isGoal(self, node, map):
        """Checker function for goal state"""
        pass

