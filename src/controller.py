import socket
import re
from user import User
from packets import *
import sys
import cPickle

class Controller:
    BLOCK = 4096 
    LOGIN_CHOICES = ("1: Login\n"
                     "2: Create User\n")
    MENU_CHOICES  = ("1: View Friends List\n"
                     "2: Search For User\n"
                     "3: Send Friend Request\n"
                     "4: Manage Pending Friend Requests\n"
                     "5: Remove Friend\n")
    
    def __init__(self):
        self.current_user_ = None
        self.server_sock_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def ConnectToServer(self, host="127.0.0.1", port=45678):
        try:
            self.server_sock_.connect((host, port))
            print "Successfully connected"
            return True
        except:
            print "Failed to connect"
            return False

    # Repeatedly attempt to login until login is valid (username exists in the
    # db) or the user types "exit". Assume that connection to server is
    # already in place
    def Login(self):
        status = False
        while not status:
            name = "!"
            while not re.match(r'\w+$', name):
                name = raw_input("Enter in your new username, or exit: ")
                if name == "exit":
                    return -1

            req = Request("Login", name)
            try:

                self.server_sock_.send(cPickle.dumps(req))
                response_data = self.server_sock_.recv(self.BLOCK)
            except:
                print "Error in network connection"
                continue
            try:
                response = cPickle.loads(response_data)
                if not response.getStatus():
                    print "Login failed with the following message:"
                    print response.getData()
                else:
                    status = True
                    print "Login succeeded"
                    return response.getData()
            except:
                print "Error Processing response data"


    # Will create a new user if the username is not already taken
    # and you will be considered logged in on successful creation
    def CreateAccount(self):
        status = False
        while not status:
            name = "!"
            while not re.match(r'\w+$', name):
                name = raw_input("Enter in your new username, or exit: ")
                if name == "exit":
                    return -1

            req = Request("CreateUser", name)
            try:

                self.server_sock_.send(cPickle.dumps(req))
                response_data = self.server_sock_.recv(self.BLOCK)
            except:
                print "Error in network connection"
                continue
            try:
                response = cPickle.loads(response_data)
                if not response.getStatus():
                    print "Creation failed with the following message:"
                    print response.getData()
                else:
                    status = True
                    print "Created User " + name + " successfully"
                    print "You are now logged in as above user"
                    return response.getData()
            except:
                print "Error Processing response data"

    def MainMenu(self):
        running = True
        while running:
            valid_choice = False
            while not valid_choice:
                choice = raw_input(self.LOGIN_CHOICES)
                if choice == "exit":
                    valid_choice = True
                    running = False
                    print "Exiting..."
                    continue
                try:
                    c = int(choice)
                except:
                    print "Please enter in a valid choice (1 or 2)"
                    continue
                if c == 1:
                    self.current_user_ = self.Login()
                    if self.current_user_ != -1:
                        valid_choice = True
                elif c == 2:
                    self.current_user_ = self.CreateAccount()
                    if self.current_user_ != -1:
                        valid_choice = True
                else:
                    print "Invalid choice. Please try again."
            print "Logged in and in main menu"
            running = False

if __name__ == '__main__':
    c = Controller()
    if not c.ConnectToServer():
        sys.exit(-1);
    c.MainMenu()
