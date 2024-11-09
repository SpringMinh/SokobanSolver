from queue import PriorityQueue
from collections import deque
import tracemalloc
import time
import os

class SearchAlgorithm:
    def __init__(self, sokoban):
        self.sokoban = sokoban
        self.frontier = PriorityQueue()
        self.explored = set()  # Use a set for faster lookups
        self.stack = []
        self.lastnode = None

    def PBCheck(self, boxR, boxC, boxPos, parent, depth):
        """Optimized deadlock checker with memoization to avoid redundant checks."""
        board = self.sokoban.board
        goalPos = self.sokoban.goal

        if depth > len(boxPos):  # Limit recursive depth to prevent stack overflow
            return True

        # Basic directional checks
        h_blocked = board[boxR][boxC - 1] == "#" or board[boxR][boxC + 1] == "#"
        v_blocked = board[boxR - 1][boxC] == "#" or board[boxR + 1][boxC] == "#"

        # Deadlock: If both h_blocked and v_blocked are true
        return h_blocked and v_blocked

    def isGoal(self, node):
        return set(self.sokoban.goal) == set(node.boxPos)

    def heuristic(self, node, goal):
        """Manhattan distance heuristic with optional weights for A*."""
        return sum(
            abs(boxR - goalR) + abs(boxC - goalC)
            for (boxR, boxC), (goalR, goalC) in zip(sorted(node.boxPos), goal)
        )

    def conf2str(self, node):
        """Creates a unique identifier for the node configuration for hashing purposes."""
        srted = tuple(sorted(node.boxPos))
        return "".join(str(r) + str(c) for r, c in srted) + str(node.workerPosX) + str(node.workerPosY)

    def printPath(self, node, filename):
        """Prints and returns the path from the root to the target node."""
        path, result = [], []
        while node:
            path.append(node)
            node = node.parent
        path.reverse()
        for step in path:
            step.Print(self.sokoban, filename)
            result.append(step)
        return result

    def printOutput(self, action, counter, steps, weight, directions, time_taken, peak_memory, level):
        """Prints the output to a file and handles memory and time metrics."""
        outputfile = f"output/output-{level:02d}.txt"
        time_ms = int(time_taken * 1000)
        memory_mb = peak_memory / (1024 * 1024)

        output = (
            f"{action}\nSteps: {steps}, Weight: {weight}, Node: {counter}, "
            f"Time (ms): {time_ms}, Memory (MB): {memory_mb:.2f}\n{directions}\n"
        )

        if os.path.exists(outputfile):
            with open(outputfile, 'r') as file:
                if action in file.read():
                    print(f"{action} already exists in {outputfile}, skipping append.")
                    return
        with open(outputfile, 'a') as file:
            file.write(output)

    def search(self, strategy="DFS"):
        """Unified search algorithm that supports DFS, BFS, UCS, and A*."""
        direction_map = {(-1, 0): 'u', (1, 0): 'd', (0, -1): 'l', (0, 1): 'r'}
        start_time = time.time()
        tracemalloc.start()

        if strategy == "BFS":
            frontier = deque([(self.sokoban.root, 0, "")])
            pop_front = True
        elif strategy == "DFS":
            frontier = [(self.sokoban.root, 0, "")]
            pop_front = False
        else:
            frontier = PriorityQueue()
            frontier.put((0, self.sokoban.root, 0, ""))
            pop_front = False

        self.explored = set()
        counter = 0
        goal = self.sokoban.goal

        while frontier:
            if strategy in {"DFS", "BFS"}:
                node, path_weight, directions = frontier.pop() if not pop_front else frontier.popleft()
            else:
                _, node, path_weight, directions = frontier.get()

            if counter % 10000 == 0:
                print(counter)

            counter += 1
            config_str = self.conf2str(node)
            if config_str in self.explored:
                continue

            self.explored.add(config_str)
            if self.isGoal(node):
                end_time = time.time()
                _, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                time_taken = end_time - start_time
                return node, counter, path_weight, directions, time_taken, peak_memory

            children = self.sokoban.moves(node)
            for child, boxIdx, move in children:
                child_config = self.conf2str(child)
                if child_config in self.explored:
                    continue

                if any(self.PBCheck(r, c, child.boxPos, (-1, -1), 1) for r, c in child.boxPos if (r, c) not in goal):
                    continue

                direction = direction_map[move].upper() if boxIdx != -1 else direction_map[move].lower()
                child_weight = self.sokoban.boxWeights[boxIdx] if boxIdx != -1 else 0
                total_path_weight = path_weight + child_weight

                if strategy == "A*":
                    frontier.put((self.heuristic(child, goal) + total_path_weight, child, total_path_weight, directions + direction))
                elif strategy == "UCS":
                    frontier.put((total_path_weight, child, total_path_weight, directions + direction))
                elif strategy == "BFS":
                    frontier.append((child, total_path_weight, directions + direction))
                else:
                    frontier.append((child, total_path_weight, directions + direction))

        end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        time_taken = end_time - start_time

        return None, counter, None, "", time_taken, peak_memory
