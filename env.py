
import sys
from tabulate import tabulate
import copy
from os import system


class Sokoban:

    # workerPos -> (Tuple) initial position of Worker
    # boxPos -> (List of tuples) initial position of all boxes
    # goal -> (List of tuples) position of all goals

    def __init__(self,board,boxPos,goal,workerPos,boxWeights):

        self.board=board
        self.goal=goal
        self.root=Node(None,boxPos,workerPos[0],workerPos[1])
        self.boxWeights = boxWeights

    def moves(self,node):
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

            if self.board[newWPX][newWPY]=="#":
                continue

            elif self.board[newWPX][newWPY]==" ":
                
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

                if self.board[newBPX][newBPY]==" " and (newBPX,newBPY) not in node.boxPos:
                    newBoxPos=copy.deepcopy(node.boxPos)
                    newBoxPos[boxIdx]=(newBPX,newBPY)
                    result.append((Node(node,newBoxPos,newWPX,newWPY),boxIdx,mv))

                else:
                    continue

        return result

class Node:

    def __init__(self,parent,boxPos,workerPosX,workerPosY):
        self.parent=parent
        self.boxPos=boxPos
        self.workerPosX=workerPosX
        self.workerPosY=workerPosY
        try:
            self.level=parent.level+1
        except:
            self.level=0
        self.cost=0

    # def __eq__(self,other):
    #     if (self.workerPosX,self.workerPosY)==(other.workerPosX,other.workerPosY) and set(self.boxPos)==set(self.boxPos):
    #         return True
    #     else:
    #         return False

    def __lt__(self,other):
        return self.cost<other.cost

    # workerPos -> (Tuple) initial position of Worker
    # boxPos -> (List of tuples) initial position of all boxes
    # goal -> (List of tuples) position of all goals
    def Print(self,SBobj,filename):
        cls = lambda: system('cls')
        board=copy.deepcopy(SBobj.board)
        row=len(SBobj.board)
        col=len(SBobj.board[0])

        for i in range(row):
            for j in range(col):
                if (i,j) in self.boxPos :
                    board[i][j]="$"
                    
                if (i,j) in SBobj.goal :
                    board[i][j]="."
                    if (i,j) in self.boxPos :
                        board[i][j]="*"

        board[self.workerPosX][self.workerPosY]="@"
        if (self.workerPosX,self.workerPosY) in SBobj.goal:
            board[self.workerPosX][self.workerPosY]="+"

        config = board
        table = tabulate(config, tablefmt="fancy_grid")
        fp=open(filename,'a+',encoding="utf-8")
        fp.write(table)
        fp.write("\n")
        fp.close()