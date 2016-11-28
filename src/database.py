import psycopg2

# Assuming that server sanitizes the input strings
class Database:
    def __init__(self, dbname="spaceattack", user="postgres", host="localhost",
                 password="postgres"):
        self.dbname_ = dbname
        self.user_ = user
        self.host_ = host
        self.password_ = password
        self.connection_ = None
        self.cur_ = None
        self.Init()

    # Connect to the database
    def Init(self):
        if (self.connection_ != None):
            self.Close()
        try:
            params = "dbname='%s' user='%s' host='%s' password='%s'" % \
                     (self.dbname_, self.user_, self.host_, self.password_)
            self.connection_ = psycopg2.connect(params)
            self.cur_ = self.connection_.cursor()
        except:
            print "Failed to connect to database"
            return False
        return True

    # Rollback the current transaction so that we can proceed with other
    # transactions
    def Reset(self):
        if self.connection_:
            self.connection_.rollback()

    # Close up the transaction and cursor
    def Close(self):
        if self.cur_:
            self.cur_.close()
        if self.connection_:
            self.connection_.close()

    # Return all user's that match the search. Should only be at most one,
    # since the username is a primary key
    def SearchForUser(self, username):
        try:
            self.cur_.execute("SELECT * FROM Users WHERE username = '%s'" % username)
            return self.cur_.fetchall()
        except:
            self.Reset()
            return "Error"

    # Add a user to the Users table, as long as they don't already exist
    def AddNewUser(self, username):
        try:
            self.cur_.execute("INSERT INTO Users (username, onlineStatus,\
                        inGameStatus) values ('%s', True, False);" % username)
            self.connection_.commit()
            return "Success"
        except psycopg2.IntegrityError as e:
            self.Reset()
            if "already exists" in e.message:
                return "Duplicate"
            else:
                return "Error"
        except:
            self.Reset()
            return "Error"

    # Check to see if the users are already friends. If not, add the request
    # to the friend request list
    def SendFriendRequest(self, sending_user, receiving_user):
        try:
            self.cur_.execute("SELECT * FROM FriendsList WHERE username='%s'\
                     AND friend='%s';" % (sending_user, receiving_user))
            if self.cur_.fetchall():
                return "Already Friends"
            # If the receiving user already sent a friend request to the
            # now sending user, instead of sending the request, just make them
            # friends in each other's friends list
            self.cur_.execute("SELECT * FROM FriendRequests WHERE from_user =\
                    '%s' AND to_user = '%s';" % (receiving_user, sending_user))
            if self.cur_.fetchall():
                self.AcceptFriendRequest(sending_user, receiving_user)
            else:
                self.cur_.execute("INSERT INTO FriendRequests (from_user,\
                        to_user) values ('%s', '%s');" % (sending_user,
                         receiving_user))
                self.connection_.commit()
            return "Success"
        except psycopg2.IntegrityError as e:
            self.Reset()
            if "already exists" in e.message:
                return "Duplicate request"
            elif "is not present" in e.message:
                return "Invalid User"
            else:
                return "Error"
        except:
            self.Reset()
            return "Error"

    # If the requests exists, delete it from the request list, and add the
    # sending_user to the receiving_user's friend list, and visa versa
    def AcceptFriendRequest(self, sending_user, receiving_user):
        try:
            self.cur_.execute("DELETE FROM FriendRequests WHERE from_user='%s'\
                     AND to_user='%s';" % (sending_user, receiving_user))
            self.cur_.execute("DELETE FROM FriendRequests WHERE from_user='%s'\
                     AND to_user='%s';" % (receiving_user, sending_user))
            self.cur_.execute("INSERT INTO FriendsList (username, friend)\
                    values ('%s', '%s');" % (sending_user, receiving_user))
            self.cur_.execute("INSERT INTO FriendsList (username, friend)\
                    values ('%s', '%s');" % (receiving_user, sending_user))
            self.connection_.commit()
            return "Success"
        except:
            self.Reset()
            return "Error"
    
    # Remove the friend request sent by sending_user, and received
    # by the receiving_user
    def RejectFriendRequest(self, sending_user, receiving_user):
        try:
            self.cur_.execute("DELETE FROM FriendRequests WHERE from_user='%s'\
                     AND to_user='%s';" % (sending_user, receiving_user))
            self.connection_.commit()
            return "Success"
        except:
            self.Reset()
            return "Error"

    def ViewFriendRequests(self, username):
        try:
            self.cur_.execute("SELECT from_user FROM FriendRequests WHERE to_user='%s';" %
                    (username,))
            return self.cur_.fetchall()
        except:
            self.Reset()
            return "Error"

    def ViewFriendsList(self, username):
        try:
            self.cur_.execute("SELECT friend FROM FriendsList WHERE username=\
                    '%s';" % username)
            return self.cur_.fetchall()
        except:
            self.Reset()
            return "Error"

    def RemoveFriend(self, username, friend):
        try:
            self.cur_.execute("DELETE FROM FriendsList WHERE username='%s' AND\
                    friend='%s';" % (username, friend))
            # Remove the reverse too
            self.cur_.execute("DELETE FROM FriendsList WHERE username='%s' AND\
                    friend='%s';" % (friend, username))
            self.connection_.commit()
            return "Success"
        except:
            self.Reset()
            return "Error"

    def RemoveUser(self, username):
        try:
            self.cur_.execute("DELETE FROM Users WHERE username='%s';" %
                              username)
            self.connection_.commit()
            return "Success"
        except:
            self.Reset()
            return "Error"

    def SetOnlineStatus(self, username, status):
        try:
            self.cur_.execute("UPDATE Users SET onlineStatus = '%s' WHERE \
                               username = '%s';" % (str(status), username))
            self.connection_.commit()
            return "Success"
        except:
            self.Reset()
            return "Error"
    
    def SetInGameStatus(self, username, status):
        try:
            self.cur_.execute("UPDATE Users SET inGameStatus = '%s' WHERE \
                               username = '%s';" % (str(status), username))
            self.connection_.commit()
            return "Success"
        except:
            self.Reset()
            return "Error"
