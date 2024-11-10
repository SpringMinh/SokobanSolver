import os
from agent import Agent
from env import Sokoban
from algorithm import SearchAlgorithm

def get_level(level):
    filename = f"levels/input-{str(level).zfill(2)}.txt"
    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist!")
        return None, None
    
    with open(filename, "r") as file:
        weights = list(map(int, file.readline().strip().split()))
        all_levels = [line.rstrip() for line in file]
    
    max_size = max(len(line) for line in all_levels)
    ll = [line.ljust(max_size) for line in all_levels]
    level_layout = [[char for char in row] for row in ll]

    return level_layout, weights

def parse_board(board):
    worker_pos, box_pos, goal_pos = None, [], []
    for x, row in enumerate(board):
        for y, char in enumerate(row):
            if char == '@':
                worker_pos = (x, y)
                board[x][y] = ' '
            elif char == '$':
                box_pos.append((x, y))
                board[x][y] = ' '
            elif char == '.':
                goal_pos.append((x, y))
                board[x][y] = ' '
            elif char == '+':
                worker_pos = (x, y)
                goal_pos.append((x, y))
                board[x][y] = ' '
            elif char == '*':
                box_pos.append((x, y))
                goal_pos.append((x, y))
                board[x][y] = ' '
    return worker_pos, box_pos, goal_pos

if __name__ == "__main__":
    level = 1
    running = True

    while running:
        board, box_weights = get_level(level)
        if not board:
            print(f"Level {level} could not be loaded.")
            break

        worker_pos, box_pos, goal_pos = parse_board(board)
        sokoban_obj = Sokoban(board, box_pos, goal_pos, worker_pos, box_weights)
        search = SearchAlgorithm(sokoban_obj)
        agent = Agent(sokoban_obj, search)

        # Start the interactive session for the current level
        level_action = agent.Interactive(level)

        # Check if we need to change levels
        if level_action == 'NEXT_LEVEL':
            if level >= 10:
                level = 10
            else:
                level += 1
        elif level_action == 'PREV_LEVEL':
            if level <= 1:
                level = 1
            else:
                level -= 1