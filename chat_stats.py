#TODO: .ini file for the exe in which people can set variables (aka those in global_consts)
#TODO: Delete logs on SystemExit? maybe?

#USAGE: "python chat_stats.py" or "python chat_stats.py <channel>"

#NOTE: Some special characters don't interact well with sockets and python, so those won't be logged (like some of them here: http://www.umingo.de/doku.php?id=misc:chat_smileys)
#NOTE: This is meant to be done a few times per stream approximately (not like 100 times per stream). So if you start recording the chat, then restart 5 mins later, the old version will be overwritten, but if you start recording the chat then restart the program 2 hours later, it will start recording new logs. The filename represents when the chat recordings were started.


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

from global_consts import include_emotes, create_graph, create_wordcloud, verbose, debug

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
    print "Error importing Twitch password info"
    print "You need to define pass_info.py with your username and oauth password"
    raise

VERSION = "1.0"
def checkVersion():
    try:
        s = urllib2.urlopen('http://chat-stats.appspot.com/versions').read()
    except urllib2.URLError:
        return #silently exit if server is down
    json_acceptable_string = s.replace("'", "\"")
    flag = False
    d = json.loads(json_acceptable_string)
    float_keys = map(float, d.keys())
    for key in list(reversed(sorted(float_keys))):
        key = str(key)
        if float(key) > float(VERSION):
            if not flag:
                print 'Program out of date!'
                flag = True
            else:
                print
            print 'New in version ' + key + ':'
            for s in d[key].split('*'):
                if s != '':
                    print '-'+s
        else:
            return

checkVersion()

if len(sys.argv) == 1:
    channel = raw_input("Chat to join: ")
else:
    channel = sys.argv[1]
try:
    count = int(sys.argv[2])
except IndexError, ValueError:
    count = 0

def isTwitchChannel(channel):
    response = json.load(urllib2.urlopen('https://api.twitch.tv/kraken/streams/'+channel))
    return 'error' not in response.keys()

while True:
    try:
        if not isTwitchChannel(channel):
            print 'Error: "' + channel + '" does not appear to be a valid Twitch channel.'
            channel = raw_input("Chat to join: ")
        break
    except urllib2.HTTPError:
        print 'Error: "' + channel + '" does not appear to be a valid Twitch channel.'
        channel = raw_input("Chat to join: ")

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

#words in the twitchemotes API that should not actually be counted as emotes 
    #AKA, not used as emotes >90% of the time
not_emotes = ['GG', 'Gg', 'double', 'triple']
emotelist = getEmotes()
for emote in not_emotes:
    emotelist.remove(emote)

dt = datetime.datetime.now()
d = dt.strftime('%b-%d-%Y')
t = dt.strftime('%H_%M')
dt = dt.strftime('%Y-%m-%d-%I%p') #2014-08-23-02PM
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
    global done
    num_messages += 1
    if debug:
        return
    message = formatMessage(message)

    if done:
        return
    else:
        try:
            #AUTHORS
            authors.write(author + '\n')
            #MESSAGES
            messages.write(message + '\n')
            #WORDS
            for word in message.split(' '):
                if word.isalnum() and (include_emotes or word not in emotelist):
                    if word != 'ACTION':
                        words.write(word)
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
            time.sleep(5)
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
    global done
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
        if not done:
            rate.write(str(count)+','+str(num_messages)+','+str(viewers)+'\n')
        else:
            exit()
            return
        count += 1
        for f in files:
            f.flush()
    except ValueError: #happens if the program closes in the middle of writing to the files
        pass
    num_messages = 0


done = False

def endProgram():
    global done
    global dt
    global stopper
    for f in files:
        f.close()
    img_directory = os.path.abspath("images/" + channel + '\\' + dt)
    if create_wordcloud:
        make_cloud(channel, dt)
        print "Word clouds created under " + img_directory + "!"
    if create_graph:
        make_plot(channel, dt)
        print "Rate chart created under " + img_directory + "!"
    else:
        print create_graph
    sys.exit()

def logEvent(x):
    global count
    global done
    try:
        s = raw_input(x)
        if s == '!exit' or s == '!quit' or s == '!q':
            print "Starting program end cycle..."
            done = True
            stopper.set() #end the setInterval
            return
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
    else:
        return

def interpret(data):
    global done
    if isMessage(data):
        if done:
            return
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

def endFunc():
    global done
    return done

print
print "===============================STARTING CHAT INPUT=============================="
print "Type '!exit', '!quit', or '!q' to stop recording."
start_new_thread(logEvent, ('Log an event (optional): ',))
try:
    stopper = checkTime()
    listen(channel, nick, PASS, interpret, endFunc)
except SystemExit:
    print "o"
    raise
print "==================================ENDING_PROGRAM================================"
endProgram()

