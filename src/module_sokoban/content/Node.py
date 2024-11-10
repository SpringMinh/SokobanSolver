from ..interface.Node import NodeInterface

class Node(NodeInterface):
    def __init__(self, parent, boxPos, workerPosX, workerPosY):
        self.parent = parent
        self.boxPos = boxPos
        self.workerPosX = workerPosX
        self.workerPosY = workerPosY
        try:
            self.depth = parent.depth + 1
        except:
            self.depth = 0
        self.cost = 0

    def __lt__(self,other):
        return self.cost<other.cost