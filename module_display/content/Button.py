from ..interface.Button import ButtonInterface
import pygame

class Button(ButtonInterface):
    def __init__(self, color, x, y, width, height, outline_color, outline_weight, fontsize, text_color, text = '', id = None):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.outline_color = outline_color
        self.outline_weight = outline_weight
        self.text = text
        self.id = id
        self.fontsize = fontsize
        self.text_color = text_color

    def draw(self, canvas):
        if self.outline_color:
            pygame.draw.rect(canvas, self.outline_color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(canvas, self.color, (self.x + self.outline_weight, self.y + self.outline_weight, self.width - 2 * self.outline_weight, self.height - 2 * self.outline_weight))
        else:
            pygame.draw.rect(canvas, self.color, (self.x, self.y, self.width, self.height))
        
        if (self.text != ''):
            font = pygame.font.SysFont('comicsans', self.fontsize)
            text = font.render(self.text, 1, self.text_color)
            canvas.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))
    
    def isMouseOver(self, mousePos):
        if mousePos[0] > self.x and mousePos[0] < self.x + self.width:
            if mousePos[1] > self.y and mousePos[1] < self.y + self.height:
                return True
            
        return False