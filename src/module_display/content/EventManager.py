from ..interface.EventManager import EventManagerInterface
import pygame

class EventManager(EventManagerInterface):
    def pollEvent(self, buttons):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn.isMouseOver(pos):
                        # Return appropriate action based on button pressed
                        if btn.id == 'navLeft':
                            return 'LEFT'
                        elif btn.id == 'navRight':
                            return 'RIGHT'
                        elif btn.id == 'navAuto':
                            return 'TOGGLE_AUTO'  # Toggle auto-play mode
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
                        elif btn.id == 'navPrev':
                            return 'PREV'
                        elif btn.id == 'navNext':
                            return 'NEXT'

            if event.type == pygame.QUIT:
                return 'QUIT'