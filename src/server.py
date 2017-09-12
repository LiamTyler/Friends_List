from database import Database
from packets import Response, Request
import socket
import cPickle

class Server:
    BLOCK = 4096
    def __init__(self, host='127.0.0.1', port=45678, listen=10):
        self.host_ = host
        self.port_ = port
        self.queue_size_ = listen
        self.sock_ = None
    
    def Init(self):
        if self.sock_:
            self.sock_.close()
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_.bind((self.host_, self.port_))
        self.sock_.listen(self.queue_size_)

    def AcceptRequests(self):
        while True:
            c, addr = self.sock_.accept()
            r = c.recv(self.BLOCK)
            req = cPickle.loads(r)
            self.ProcessRequest(req, c)

    def ProcessRequest(self, req, c):
            t = req.getType()
            if t == "CreateUser":
                print "In create user"
            elif t == "Login":
                print "In Login"
            elif t == "ViewFriendRequests":
                print "In View friends reqs"
            elif t == "SendFriendRequest":
                print "In Send friend req"
            elif t == "RejectFriendRequest":
                print "In Reject friend request"
            elif t == "AcceptFriendRequest":
                print "In accept friend request"
            elif t == "ViewFriendsList":
                print "In view friends list"
            elif t == "RemoveFriend":
                print "In remove friend"
            else:
                print "Unknown request"
            resp = Response("Valid", "Test")
            c.send(cPickle.dumps(resp))
            c.close()
