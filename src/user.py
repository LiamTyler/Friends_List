class User:
    def __init__(self, username, onlineStatus=False, inGameStatus=False):
        self.username_ = username
        self.onlineStatus_ = onlineStatus
        self.inGameStatus_ = inGameStatus

    def getUserName(self):
        return self.username_

    def setOnlineStatus(self, b):
        if type(b) == bool:
            self.onlineStatus_ = b

    def getOnlineStatus(self):
        return self.onlineStatus_

    def setInGameStatus(self, b):
        if type(b) == bool:
            self.inGameStatus_ = b

    def getInGameStatus(self):
        return self.inGameStatus_
