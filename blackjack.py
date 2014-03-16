import Deck
import random
d=None
num_players=0
players=[]
moves=[]
hasbeenset=[]
playerdict={}
 
#creates a dictionary of player names and indexes in the list of player hands
def playtoname(player_names, players):
    name = []
    for i in range(1, len(players)):
        name.append((player_names[i-1], i))
    return dict(name)
 
def whowins(players):
    max = 0
    checkover(players)
    sums = map(sum, players)
    x = len(players) - 1
    while (x >= 0):
        if (players[x][0] != -1 and sums[x] > max):
            max = sums[x]
    winners = []
    num = sums.count(max)
    while (num > 0 ):
        num = num - 1
        i = sums.index(max)
        winners.append(i)
        sums[i] = 0
    return winners
 
def setmove(i, move):
    global moves
    global hasbeenset
    if i<len(moves):
        print("setting move")
        moves[i]=move
        hasbeenset[i]=1
 
def allset():
    global hasbeenset
    print("WTF")
    for i in range(1, len(hasbeenset)):
        if (hasbeenset[i]==0):
            print("i="+str(i))
            return False
    print("len hasbeenset="+str(len (hasbeenset)))
    return True
def sendRequests(sockets):
    global hasbeenset
    for i in range(1, len(hasbeenset)):
        if (hasbeenset[i]==0):
            sockets[i-1].getsocket().send(bytes("Please submit a blackjack move.", 'UTF-8'))
def resetmoves():
    print("reset moves")
    global moves
    global hasbeenset
    for i in range(1, len(moves)):
        moves[i]=0
        hasbeenset[i]=0
 
def initGame(clientsockets):
    global d
    global num_players
    global players
    global moves
    global hasbeenset
    global playerdict
    d = Deck.Deck()
    num_players = len(clientsockets)
    players = []
    moves=[]
    hasbeenset=[]
    names=[]
    i = 0
    #set up
    while (i <= num_players):
        print("init"+str(i))
        players.append(initial_deal(d))
        moves.append(0)
        hasbeenset.append(0)
        names.append(clientsockets[i-1].getname())
        i = 1 + i
    playerdict=playtoname(names, players)
 
    print("len hasbeenset="+str(len(hasbeenset)))
    hasbeenset[0]=1
 
def gethand(i):
    global players
    return str(players[i+1])
def dealcard(deck):
    x = random.choice(deck.contents)
    deck.remove(x)
    return x
 
def initial_deal(deck):
    try:
        x = random.choice(deck.contents)
        deck.remove(x)
        y = random.choice(deck.contents)
        deck.remove(y)
        return [x,y]
    except:
        pass
def dealerturn(players, deck):
    aces = players[0].count(11)
    t = sum(players[0])
    while(t > 21 and aces > 0):
        players[0].remove(11)
        players[0].append(1)
        aces = players[0].count(11)
        t = sum(players[0])
    if( t < 17):
        players[0].append(dealcard(deck))
        dealerout = "hit"
    else:
        dealerout = "stand"
    return dealerout
 
 
def checkover(players):
    playersin = []
    x = len(players)
    while(x > 0 and (players[x-1][0] > 0)):
        x = x - 1
        player = players[x]
        aces = player.count(11)
        t = sum(player)
        while(t > 21 and aces > 0):
            player.remove(11)
            player.append(1)
            aces = player.count(11)
            t = sum(player)
        if( t > 21):
            player[0] = -1
    x = len(players)
    while(x > 0):
        x = x - 1
        if players[x][0] > 0:
            playersin.append(x)
    if players[0][0] > 0:
        playersin.append(-1)
    print("playersin len"+str(len(playersin)))
    #return playersin.reverse()
    return list(reversed(playersin))
 
 
def getmove(index, players):
    #get the move from the player with this index and hand
    return players[index]
 
 
 
 
def rungame(sockets,sendtoall):
    global d
    print (players)
    #loop for game
    #game = 1
    #while(game):
    #assume that a 0 is pass and 1 is hit me
    x = checkover(players)
    y = len(x) - 1
    #print (players[0][0])
    #we need to get the input from players one by one, we have the list of indicies of players who are still in
    #if(x[0] != "dealer"):
     #   print ("The dealer went over!  Game over")
 
    #else:
    i = 1
    while (i < y):
        move = getmove(i, players)
        #while move == 1:
        if (move==1):
            playerout = "hit for player: "+str(i)
            players[i].append(dealcard(d))
         #   move = getmove(i, players)
        else:
            playerout = "stand for player: "+str(i)
         
        sockets[i-1].getsocket().send(bytes(playerout,'UTF-8'))
        i=i+1
        #sendtoall(playerout)
    dealerout = dealerturn(players, d)
    sendtoall(dealerout)
    #resetmoves()
