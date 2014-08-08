#TODO: words per message?, --> AUTO WORD CLOUD <--, create images (graphs) of the most used emotes
#TODO: Delete logs on SystemExit? maybe?
#TODO: listen() might crash silently on internet interruption. need to do more testing.

#USAGE: "python chat_stats.py" or "python chat_stats.py <channel>"

#NOTE: Some special characters don't interact well with sockets and python, so those won't be logged (like some of them here: http://www.umingo.de/doku.php?id=misc:chat_smileys)
#NOTE: This is meant to be done a few times per stream approximately (not like 100 times per stream). So if you start recording the chat, then restart 5 mins later, the old version will be overwritten, but if you start recording the chat then restart the program 2 hours later, it will start recording new logs. The filename represents when the chat recordings were started.
#NOTE: 'rate' is in messages per minute

include_emotes = False #include emotes in the words wordcloud?
create_graph = True #create graph of the rates over time? Need matplotlib for this. 
                        #Which you should have anyway because it's awesome.
create_wordcloud = True #create wordclouds of the chat? Need word_cloud for this.
verbose = True #default=False
debug = False #It won't log any information.

from thread import start_new_thread, exit
import os
import sys
import time
import string
import datetime
import threading
import urllib2
import json
import re
from twitch_chat_listen import listen

if '--nocloud' in sys.argv[2:]:
    create_wordcloud = False
if '--nograph' in sys.argv[2:]:
    create_graph = True
if '--debug' in sys.argv[2:]:
    debug = True

if create_graph:
    from make_plot import make_plot
if create_wordcloud:
    from make_cloud import make_cloud
try:
    from pass_info import get_password, get_username
except ImportError:
    print "Error loading Twitch password info"
    print "You need to defined pass_info.py with your username and oauth password"

if len(sys.argv) == 1:
    channel = raw_input("Chat to join: ")
else:
    channel = sys.argv[1]
try:
    count = int(sys.argv[2])
except IndexError, ValueError:
    count = 0

#thanks to http://twitchemotes.com/ :-)
def getEmotes():
    emotelist = [':)',':(',':o',':z','B)',':/',';)',';p',':p',';P',':P','R)','o_O','O_O','o_o','O_o',':D','>(','<3']
    print "loading emotes..."
    normal = json.load(urllib2.urlopen('http://twitchemotes.com/global.json'))
    emotelist.extend(normal.keys())
    print "loading sub emotes..."
    subs = json.load(urllib2.urlopen('http://twitchemotes.com/subscriber.json'))
    for channel in subs.keys():
        emotelist.extend(subs[channel]['emotes'].keys())
    return emotelist

print

emotelist = getEmotes()
emotelist.remove('GG')
emotelist.remove('Gg')

dt = datetime.datetime.now()
d = dt.strftime('%b-%d-%Y')
t = dt.strftime('%H_%M')
dt = dt.strftime('%b-%m-%d-%I%p') #2014-08-23-02PM
directory = "logs/" + channel + '/' + dt
if not os.path.exists(directory) and not debug:
    os.makedirs(directory)
print 
if debug:
    print "Debug mode - not writing to any directories"
else:
    print "Writing to " + directory

def open_file(kind, extension='log'):
    filename = ""
    filename += kind+'.'+extension
    file_path = os.path.relpath(directory + '/' + filename)
    return open(file_path, 'w')

files = []
if not debug:
    authors = open_file('authors') #to get the most active users
    messages = open_file('messages') #literal log of the messages - for average message length, etc.
    words = open_file('words') #to get word cloud
    emotes = open_file('emotes') #for emote stats
    rate = open_file('rate', 'csv') #how fast chat is going
    files = [authors, messages, words, emotes, rate]

prog = re.compile('^.*[a-z0-9_.-]+\.tmi\.twitch\.tv PRIVMSG #')
def isMessage(data):
    return prog.match(data) != None
    #return len(data.split('tmi.twitch.tv PRIVMSG #')) > 1

def formatMessage(message):
    #TODO: remove the "action" stuff for "/me"s
    return message.strip().split('\n')[0].split('\r')[0]

num_messages = 0

def log(author, message):
    global num_messages
    num_messages += 1
    if debug:
        return
    message = formatMessage(message)

    try:
        #AUTHORS
        authors.write(author + '\n')
        #MESSAGES
        messages.write(message + '\n')
        #WORDS
        for word in message.split(' '):
            if word.isalnum() and (include_emotes or word not in emotelist):
                words.write(word.upper())
                words.write(' ')
        #EMOTES
        for word in message.split(' '):
            if word in emotelist:
                emotes.write(word.split('/')[0].split('7')[0] + '\n')
    except ValueError: #happens if the program closes in the middle of writing to the files
        print "Closing program..."
        pass

#http://stackoverflow.com/questions/5179467
def setInterval(interval, times=-1):
    # This will be the actual decorator
    def outer_wrap(function):
        # This will be the function to be called
        def wrap(*args, **kwargs):
            stop = threading.Event()

            # This is another function to be executed
            # in a different thread to simulate setInterval
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1
            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


#init
if not debug:
    rate.write('TIME_START='+t+'\n')

#Writes a notable event to be marked by red vertical line and text
def writeEvent(time, msg):
    try:
        rate.write('*'+str(time)+'*,'+msg+'\n')
    except ValueError: #happens if the program closes in the middle of writing to the files
        pass

def get(URL):
    val = None
    while True:
        try:
            val = urllib2.urlopen(URL)
            break
        except urllib2.URLError:
            print "Connection timed out. Retrying."
            pass
    return val
            
cur_game = json.load(get('https://api.twitch.tv/kraken/channels/'+channel))['game']

#RATE
@setInterval(60)
def checkTime():
    if debug:
        return
    global count
    global num_messages
    global cur_game
    game = cur_game
    stream = json.load(get('https://api.twitch.tv/kraken/streams/'+channel))['stream']
    if stream == None:
        viewers = int(json.load(get('http://tmi.twitch.tv/group/user/'+channel))['chatter_count'])
        game = json.load(get('https://api.twitch.tv/kraken/channels/'+channel))['game']
    else:
        viewers = int(stream['viewers'])
    if game != cur_game:
        print "Now playing " + game
        #writeEvent(count, 'Now playing ' + game)
        cur_game = game
    try:
        rate.write(str(count)+','+str(num_messages)+','+str(viewers)+'\n')
    except ValueError: #happens if the program closes in the middle of writing to the files
        pass
    count += 1
    for f in files:
        f.flush()
    num_messages = 0

done = False

def endProgram():
    global done
    global dt
    done = True
    for f in files:
        f.close()
    img_directory = "images/" + channel + '/' + dt
    if create_wordcloud:
        make_cloud(channel, dt)
        print "Rate chart created under /" + img_directory + "!"
    if create_graph:
        make_plot(channel, dt)
        print "Rate chart created under /" + img_directory + "!"
    else:
        print create_graph
    exit()
#TODO: output images and stuff. stats. (aka the main point of this program.)
    #sys.exit()

def logEvent(x):
    global count
    global done
    try:
        s = raw_input(x)
        if s == '!exit' or s == '!quit' or s == '!q':
            print "==================================ENDING PROGRAM================================"
            endProgram()
        writeEvent(count, s)
        try:
            rate.flush()
        except ValueError: #happens if the program closes in the middle of writing to the files
            pass
        print 'Event "' + s + '" logged at ' + datetime.datetime.now().strftime('%I:%M %p') + '.'
        print
    except (EOFError, KeyboardInterrupt):
        print
        print
        print "==================================ENDING PROGRAM!+=============================="
        endProgram()
        pass
    if not done:
        start_new_thread(logEvent, (x,))

def interpret(data):
    if isMessage(data):
        try:
            try:
                author = data.split('@')[1].split('.tmi.twitch.tv',1)[0]
            except IndexError:
                author = data.split('.tmi.twitch.tv',1)[0]
            s = channel + ' :'
            message = s.join(data.split(s)[1:])
            message = filter(lambda x: x in string.printable, message)
            log(author, message)
            if verbose:
                print (author + ' - ' + message).strip()
        except IndexError:
            print
            print 'MALFORMED DATA - ' + data
            print 'MALFORMED DATA - ' + data
            print 'MALFORMED DATA - ' + data
            print
            return

nick = get_username()
PASS = get_password()

print
print "===============================STARTING CHAT INPUT=============================="
print "Type '!exit', '!quit', or '!q' to stop recording."
start_new_thread(logEvent, ('Log an event: ',))
checkTime()
listen(channel, nick, PASS, interpret)
print "==================================ENDING_PROGRAM================================"
endProgram()

