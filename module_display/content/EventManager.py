from ..interface.EventManager import EventManagerInterface
import pygame

class EventManager(EventManagerInterface):
    def pollEvent(buttons):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn.isOver(pos):
                        # Return appropriate action based on button pressed
                        if btn.id == 'navLeft':
                            return -1
                        elif btn.id == 'navRight':
                            return 1
                        elif btn.id == 'navAuto':
                            return 0  # Toggle auto-play mode
                        elif btn.id == 'navReset':
                            print("Reset button clicked")
                            return 'RESET'
                        elif btn.id == 'navDFS':
                            print("DFS algorithm chosen")
                            return 'DFS'
                        elif btn.id == 'navBFS':
                            print("BFS algorithm chosen")
                            return 'BFS'
                        elif btn.id == 'navUCS':
                            print("UCS algorithm chosen")
                            return 'UCS'
                        elif btn.id == 'navAstar':
                            print("A* algorithm chosen")
                            return 'ASTAR'

            if event.type == pygame.QUIT:
                return 'QUIT'