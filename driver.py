import os
from agent import Agent
from env import Sokoban
import copy

def get_level(level):

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


if __name__=="__main__":
    # board=[
	# [' ',' ','#','#','#','#','#',' '],           
    # ['#','#','#',' ',' ',' ','#',' '],  
    # ['#','.','@','$',' ',' ','#',' '],    
    # ['#','#','#',' ','$','.','#',' '],  
    # ['#','.','#','#','$',' ','#',' '],  
    # ['#',' ','#',' ','.',' ','#','#'],  
    # ['#','$',' ','*','$','$','.','#'],
    # ['#',' ',' ',' ','.',' ',' ','#'],  
    # ['#','#','#','#','#','#','#','#']]

    level = 3
    board, boxWeights = get_level(level)

    # print(board)

    workerPosX=None
    workerPosY=None
    boxPos =[]
    goalPos= []
    if board:
        for x in range(len(board)):
            for y in range(len(board[x])):
                if board[x][y] == '@':
                    workerPosX=x
                    workerPosY=y
                    board[x][y]=' '
                if board[x][y] == '$':
                    boxPos.append((x,y))
                    board[x][y]=' '
                if board[x][y] =='.':
                    goalPos.append((x,y))
                    board[x][y]=' '
                if board[x][y] == '+':
                    workerPosX=x
                    workerPosY=y
                    goalPos.append((x,y))
                    board[x][y]=' '
                if board[x][y] == '*':
                    boxPos.append((x,y))
                    goalPos.append((x,y))
                    board[x][y]=' '

        print(boxPos)

        workerPos=(workerPosX,workerPosY)

        SBobj=Sokoban(board,boxPos,goalPos,workerPos,boxWeights)        

        agnt=Agent(SBobj)

        agnt.Interactive(level)

        # result,counter,weight=agnt.DFS()
        # result,counter,weight=agnt.BFS()
        

        # try:
        #     os.remove("path.txt")
        # except:
        #     pass
        # path=agnt.printPath(result,"path.txt")

        # print("Nodes explored: ", counter)
        # print("Steps taken: ", result.level)
        # print("Total weights pushed: ", weight)
        # print("List of weights: ", boxWeights)

        # agnt.Interactive(path)


    



            