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

    def Init(self):
        if (self.connection_ == None):
            try:
                params = "dbname='%s' user='%s' host='%s' password='%s'" % \
                         (self.dbname_, self.user_, self.host_, self.password_)
                self.connection_ = psycopg2.connect(params)
                self.cur_ = self.connection_.cursor()
            except:
                print "Failed to connect to database"
                return False
        else:
            print "Connection already present"
        return True

    def Reset(self):
        if self.connection_:
            self.connection_.rollback()

    def Close(self):
        if self.cur_:
            self.cur_.close()
        if self.connection_:
            self.connection_.close()

    def SearchForUser(self, username):
        self.cur_.execute("SELECT * FROM Users WHERE username = '%s'" % username)
        return self.cur_.fetchall()

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

    def SendFriendRequest(self, sending_user, receiving_user):
        try:
            self.cur_.execute("INSERT INTO FriendRequests (from_user, to_user)\
                    values ('%s', '%s');" % (sending_user, receiving_user))
            self.connection_.commit()
            return "Success"
        except psycopg2.IntegrityError as e:
            self.Reset()
            if "already exists" in e.message:
                return "Duplicate"
            elif "is not present" in e.message:
                return "Invalid User"
            else:
                return "Error"
        except:
            self.Reset()
            return "Error"
