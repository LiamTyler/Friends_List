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
            return self._SearchUser(username)
        except:
            self.Reset()
            return "Error"

    # Add a user to the Users table, as long as they don't already exist
    def AddNewUser(self, username):
        try:
            self._InsertUser(username, True)
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

    def RemoveUser(self, username):
        try:
            self._DeleteUser(username, True)
            return "Success"
        except:
            self.Reset()
            return "Error"

    # Check to see if the users are already friends. If not, add the request
    # to the friend request list
    def SendFriendRequest(self, sending_user, receiving_user):
        try:
            if self._SearchFriendsList(sending_user, receiving_user):
                return "Already Friends"

            # If the sending user already got a request from the recipient,
            # just add them to each others friend list and remove request
            if self._SearchRequest(sending_user, receiving_user):
                return self.AcceptFriendRequest(sending_user, receiving_user)
            else:
                self._InsertRequest(sending_user, receiving_user, True)
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
            self._DeleteRequest(sending_user, receiving_user)
            self._InsertFriend(sending_user, receiving_user)
            self._InsertFriend(receiving_user, sending_user, True)
            return "Success"
        except:
            self.Reset()
            return "Error"
    
    # Remove the friend request sent by sending_user, and received
    # by the receiving_user
    def RejectFriendRequest(self, sending_user, receiving_user):
        try:
            self._DeleteRequest(sending_user, receiving_user, True)
            return "Success"
        except:
            self.Reset()
            return "Error"

    def ViewFriendRequests(self, username):
        try:
            return self._SearchRequests(username)
        except:
            self.Reset()
            return "Error"

    def ViewFriendsList(self, username):
        try:
            return self._SearchFriendsList(username)
        except:
            self.Reset()
            return "Error"

    def RemoveFriend(self, username, friend):
        try:
            self._DeleteFriend(username, friend)
            self._DeleteFriend(friend, username, True)
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

    ########################### HELPER FUNCTIONS ##############################
    #
    # Summary: All these functions below merely execute the SQL on each of the
    #          3 tables. These are just so that the above code where the logic
    #          actually resides is uncluttered and easier to understand
    #
    ###########################################################################

    def _SearchUser(self, username):
        SQL = "SELECT * FROM Users WHERE username = (%s);"
        data = (username,)
        self.cur_.execute(SQL, data)
        return self.cur_.fetchall()

    def _InsertUser(self, username, onlineStatus=True,
                    inGameStatus=False, save=False):
        SQL = "INSERT INTO Users (username, onlineStatus, inGameStatus) \
               values ((%s), (%s), (%s));"
        data = (username, onlineStatus, inGameStatus)
        self.cur_.execute(SQL, data)
        if save:
            self.connection_.commit()

    def _DeleteUser(self, username, save=False):
        SQL = "DELETE FROM Users WHERE username = (%s);"
        data = (username,)
        self.cur_.execute(SQL, data)
        if save:
            self.connection_.commit()
    
    def _SearchRequest(self, receiving_user=None, sending_user=None):
        if not sending_user and not receiving_user:
            return []
        elif not sending_user:
            SQL = "SELECT from_user FROM FriendRequests WHERE to_user = (%s);"
            data = (receiving_user,)
        elif not receiving_user:
            SQL = "SELECT to_user FROM FriendRequests WHERE from_user = (%s);"
            data = (sending_user,)
        else:
            SQL = "SELECT * FROM FriendRequests WHERE from_user = (%s) AND \
                    to_user = (%s);"
            data = (sending_user, receiving_user)

        self.cur_.execute(SQL, data)
        return self.cur_.fetchall()

    def _InsertRequest(self, sending_user, receiving_user, save=False):
        SQL = "INSERT INTO FriendRequests (from_user, to_user) \
               values ((%s), (%s));"
        data = (sending_user, receiving_user)
        self.cur_.execute(SQL, data)
        if save:
            self.connection_.commit()

    def _DeleteRequest(self, sending_user, receiving_user, save=False):
        SQL = "DELETE FROM FriendRequests WHERE from_user = (%s) \
                AND to_user = (%s);"
        data = (sending_user, receiving_user)
        self.cur_.execute(SQL, data)
        if save:
            self.connection_.commit()

    def _SearchFriendsList(self, username, friend=None):
        if not friend:
            SQL = "SELECT friend FROM FriendsList WHERE username = (%s);"
            data = (username,)
        else:
            SQL = "SELECT * FROM FriendsList WHERE username = (%s) AND \
                    friend = (%s);"
            data = (username, friend)
        self.cur_.execute(SQL, data)
        return self.cur_.fetchall()

    def _InsertFriend(self, username, friend, save=False):
        SQL = "INSERT INTO FriendsList (username, friend) values ((%s), (%s));"
        data = (username, friend)
        self.cur_.execute(SQL, data)
        if save:
            self.connection_.commit()

    def _DeleteFriend(self, username, friend, save=False):
        SQL = "DELETE FROM FriendsList WHERE username = (%s) \
                AND friend = (%s);"
        data = (username, friend)
        self.cur_.execute(SQL, data)
        if save:
            self.connection_.commit()

