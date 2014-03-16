import sys
import socket
import edit
import os
import time
import shutil
import blackjack
 
chatlog=open("chatlog.txt", "a")
edlog=open("edlog.txt","a")
 
def checkbackupdir(filename):
    dirname=filename[0:filename.find(".")]
    if not os.path.exists(os.path.join(os.getcwd(), "backup/"+dirname)):
        os.makedirs(os.path.join(os.getcwd(), "backup/"+dirname))
 
checkbackupdir("")
serversocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    serversocket.bind(('127.0.0.1',3219))
except OSError:
    try:
        serversocket.bind(('127.0.0.1',3119))
    except OSError:
        serversocket.bind(('127.0.0.1',3019))
 
serversocket.setblocking(0)
serversocket.listen(5)
 
clientsockets=[]
class user:
    def __init__(self, socket):
        self.socket=socket
        self.file=None
        self.filename=""
        self.name=""
        self.backupname=""
    def getsocket(self):
        return self.socket
    def getfile(self):
        return self.file
    def getfilename(self):
        return self.filename
    def getbackupfoldername(self):
        return self.backupname
    def setfile(self, path):
        toreturn=""
        self.backupname=os.path.join(os.getcwd(),"backup/"+path[0:path.find(".")])
        backuppath=os.path.join(os.getcwd(), "backup/"+path[0:path.find(".")]+"/"+time.strftime("%Y-%m-%d-%H-%M-%S-")+path)
        curpath=os.path.join(os.getcwd(), path)
        checkbackupdir(path[0:path.find(".")]+"/")
        open(backuppath, 'w').close()
        try:
            shutil.copy(curpath, backuppath)
        except FileNotFoundError:
            toreturn="Making a new file."
        self.file=edit.openFile(curpath)
        self.filename=curpath
        return toreturn
    def nullFile(self):
        self.file=None;
        self.filename=""
    def setname(self,name):
        self.name=name
    def getname(self):
        return self.name
def sendtoallnoremove(line):
    for client in clientsockets:
        try:
            client.getsocket().send(bytes(line, 'UTF-8'))
        except BrokenPipeError:
            pass
def sendtoall(line):
    dec=0;
    for client in clientsockets:
        try:
            client.getsocket().send(bytes(line, 'UTF-8'))
        except BrokenPipeError:
            clientsockets.remove(client)
            dec=dec-1
    return dec
 
try:
    #global chatlog
    #global edlog
    blackjackrunning=False
    while 1:
        clientsocket=None
        try:
            (clientsocket, address)=serversocket.accept()
        except BlockingIOError:
            pass
        if (clientsocket is not None):
            clientsockets.append(user(clientsocket))
            clientsocket.setblocking(0)
        adjust=0
        for i in range(0, len (clientsockets)):
            socket=clientsockets[i-adjust]
            try:
                test=str(socket.getsocket().recv(1000))[2:-1]
                if (test != ''):
                    #print("test="+test)
                    if (test[0:3]=="%"+"ed"):
                        string=socket.setfile(test[4:])
                        string="%"+"Opening file "+test[4:]+"\n"+string
                        socket.getsocket().send(bytes(string,'UTF-8'))
                        #print (test[4:])"+"
                    elif (test[0:3]=="%"+"vc"):
                        if (socket.getfilename()==""):
                            socket.getsocket().send(bytes("%"+"No file open",'UTF-8'))
                        else:
                            path=socket.getbackupfoldername()#socket.getfilename()[0:socket.getfilename().find(".")]
                            onlyfiles = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
                            if (len(test)<4):
                                 
                                msg="%"
                                for i in range(0, len(onlyfiles)):
                                    f=onlyfiles[i]
                                    print (f)
                                    msg=msg+str(i)+": "+f+'\n'
                                socket.getsocket().send(bytes(msg,'UTF-8'))
                            else:
                                if (test[4:10]=="revert"):
                                    print("reverting")
                                    try:
                                        target=int(test[11:])
                                        print (target)
                                        if (target<len(onlyfiles) and target>=0):
                                            shutil.copy(os.path.join(socket.getbackupfoldername(),onlyfiles[target]), socket.getfilename())
                                    except ValueError:
                                        pass
                                 
                    elif (test[0:6]=="*name*"):
                        socket.setname(test[6:])
                        #print ("name="+socket.getname())
                        socket.getsocket().send(bytes("Welcome, "+socket.getname()+".", 'UTF-8'))
                        chatlog.write(time.strftime("%Y-%m-%d--%H-%M-%S")+" "+socket.getname()+" entered the server.\n")
                        chatlog.flush()
                    elif (test[0]=="$"):
                        print(test[1:12])
                        if (test[1:11]=="!blackjack"):
                            if (blackjackrunning):
                                print(test[12:])
                                if (test[12:]=="print"):
                                    socket.getsocket().send(bytes("Current hand:"+blackjack.gethand(i),'UTF-8'))
                                if (test[12:]=="hit"):
                                    blackjack.setmove(i+1,1)
                                if (test[12:]=="pass"):
                                    blackjack.setmove(i+1,0)
                                if (test[12:]=="nextmove"):
                                    if (blackjack.allset()):
                                        blackjack.rungame(clientsockets, sendtoallnoremove)
                                    else:
                                        blackjack.sendRequests(clientsockets)
                            elif(test[12:]=="start"):
                                blackjack.initGame(clientsockets);
                                sendtoallnoremove("Starting Blackjack Game")
                                blackjackrunning=True
                            else:
                                socket.getsocket().send(bytes("No game running.",'UTF-8'))
                        else:
                            adjust=adjust+sendtoall("*"+socket.getname()+"*"+test[1:])
                            chatlog.write(time.strftime("%Y-%m-%d--%H-%M-%S")+" "+"*"+socket.getname()+"*"+test[1:]+"\n")
                            chatlog.flush()
                    else:
                        try:
                            out=edit.betterprocess(socket.getfilename(), test[1:], socket.getfile())
                            if (test[1:]=='q'):
                                socket.nullFile()
                            if (out != ""):
                                socket.getsocket().send(bytes(("%"+str(out)),'UTF-8'))
                        except TypeError:
                            socket.getsocket().send(bytes("%"+"No file open",'UTF-8'))
                        except AttributeError:
                            socket.getsocket().send(bytes("%"+"No file open",'UTF-8'))
                    #else:
                    #   socket.getsocket().send(bytes("%"+"No file open",'UTF-8'))
            except BlockingIOError:
                pass
finally:
    serversocket.close()
