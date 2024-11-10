class GameInterface:
    def __init__(self):
        pass

    def processEvent(self, event):
        """Function to process game's window events"""
        pass

    def Run(self):
        """Function to run Game """
        pass

    def Draw(self):
        """Function to draw and update Game interface"""
        pass

    def allowChangeLvl(self):
        """Function to check if user can change to another lvl or not"""
        pass

    def currentPath(self):
        """Function to get the current Algorithm path"""
        pass

    def generatePath(self, Algo):
        """Function to generate state"""
        pass

    def setCurrentMap(self, id):
        """Function to set current map"""
        pass

    def hasCurrentPath(self):
        """Checker function for current path"""
        pass