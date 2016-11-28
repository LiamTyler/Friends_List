class Request:
    # Class for clients sending requests to server
    def __init__(self, typeOfReq, reqData):
        self.typeOfReq_ = typeOfReq
        self.reqData_ = reqData

    def getType(self):
        return self.typeOfReq_

    def getData(self):
        return self.reqData_

class Response:
    # class for server sending back a processed response from client.
    # Response contains a status (success / failure) and the data
    def __init__(self, status, data):
        self.status_ = status
        self.data_ = data

    def getStatus(self):
        return self.status_

    def getData(self):
        return self.data_
