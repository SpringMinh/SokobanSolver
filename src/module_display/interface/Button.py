class ButtonInterface:
    def __init__(self, color, x, y, width, height, outline_color, outline_weight, text = '', id = None):
        pass

    def draw(self, canvas):
        """Draw function"""
        pass

    def isMouseOver(self, mousePos):
        """Check if mouse is over this button"""
        pass

    