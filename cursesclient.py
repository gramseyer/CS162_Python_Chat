import sys
import socket
import _thread as thread
import curses
import _curses
import math
 
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
prevChatLines=[]
prevEdLines=[]
currentmessage=""
ed=False
LINES=0
COLS=0
for i in range (0, 100):
    prevChatLines.append("")
    prevEdLines.append("")
 
def main(stdscr):
    global LINES
    global COLS
    pad = curses.newpad(curses.LINES, curses.COLS)
    curses.use_default_colors()
    thread.start_new_thread(readInput,(stdscr,pad))
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    COLS=curses.COLS
    LINES=curses.LINES
    while 1:
        resize = curses.is_term_resized(LINES, COLS)
        if resize is True:
            LINES, COLS = stdscr.getmaxyx()
            stdscr.clear()
            curses.resizeterm(LINES, COLS)
            pad.resize(LINES,COLS)
            stdscr.refresh()
        try:
            for i in range(0,LINES-1):
                pad.move(i,0)
                pad.clrtoeol()
                pad.addstr(i,0,prevChatLines[i], curses.color_pair(1))
                pad.addstr(i,math.floor(COLS/2), prevEdLines[i], curses.color_pair(3))
            pad.move(LINES-1,0)
            pad.clrtoeol()
            global ed
            if (ed):
                pad.addstr(LINES-1,0,currentmessage, curses.color_pair(3))
            else:
                pad.addstr(LINES-1,0,currentmessage, curses.color_pair(1))
            pad.refresh(0,0,0,0,LINES,COLS)
        except _curses.error:
            pass
def startRender():
    curses.wrapper(main)
 
def freeChatLine():
    for i in range(1, LINES):
        prevChatLines[LINES-i]=prevChatLines[LINES-i-1]
 
def putChatLine(string):
    numlines=math.ceil(len(string)/math.floor(COLS/2))
    for i in range(0, numlines):
        freeChatLine()
    for i in range(0, numlines):
        prevChatLines[i]=string[i*math.floor(COLS/2):(i+1)*math.floor(COLS/2)]
 
def freeEdLine():
    for i in range(1, LINES):
        prevEdLines[LINES-i]=prevEdLines[LINES-i-1]
 
def putEdLine(string):
    lines=[]
    lastline=0
    for i in range(0, len (string)):
        if (i-lastline>=math.floor(curses.COLS/2)):
            lines.append(string[lastline:i])
            lastline=i
        if (string[i:i+2]=='\\'+'n'):
            lines.append(string[lastline:i])
            lastline=i+2
    lines.append(string[lastline:])
    for i in range(0, len (lines)):
        freeEdLine()
        prevEdLines[0]=lines[len(lines)-i-1]
 
def readInput(stdscr,pad):
    c=""
    while 1:
        global currentmessage
        c=stdscr.getch()
        #putLine("got key")
        # Check if screen was re-sized (True or False)
        global ed
        if (c==curses.KEY_RESIZE):
            pass
            #currentmessage=str(curses.LINES)+" "+str(curses.COLS)
            #curses.endwin()
            #y,x=stdscr.getmaxyx()
            #stdscr.refresh()
            #stdscr.clear()
            #stdscr.refresh()
            #curses.resizeterm(y,x)
            #pad.resizeterm(y,x)
            #stdscr.refresh()
         
        elif (c==curses.KEY_BACKSPACE):
            currentmessage=currentmessage[:-1]
        elif (chr(c)=='\t'):
            ed=not(ed)
        elif (chr(c)=='\n'):
            if (ed):
                s.send(bytes("%"+currentmessage, 'UTF-8'))
                currentmessage=""
            else:
                msg=currentmessage;
                s.send(bytes("$"+msg,'UTF-8'))
                currentmessage=""
        else:
            currentmessage=currentmessage+chr(c)
try:
    s.connect(('127.0.0.1',3219))
except ConnectionRefusedError:
    try:
        s.connect(('127.0.0.1',3119))
    except:
        s.connect(('127.0.0.1',3019))
s.setblocking(0)
#print ("Welcome to Da Awesomest Chat Server In Da Wild West\nType yer name!")
#name=input()
name=""
try:
    name=sys.argv[1]
except IndexError:
    name="add a name fool"
s.send(bytes("*name*"+name,'UTF-8'))
def receivemessages():
    while 1:
        try:
            test=str(s.recv(1000))[2:-1]
            if (test != ''):
                if (test[0]=="%"):
                    putEdLine(test[1:])
                else:
                    putChatLine(test)
        except BlockingIOError:
            i=1
def sendmessages():
    while 1:
        pass
        #msg="*"+name+"*"+input()
        #s.send(bytes(msg,'UTF-8'))
 
thread.start_new_thread(receivemessages,())
thread.start_new_thread(sendmessages,())
startRender()
