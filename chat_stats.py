#TODO: words per message, --> AUTO WORD CLOUD <--, create images (graphs) of the most used emotes
#TODO: Delete logs? maybe?

#USAGE: "python chat_stats.py" or "python chat_stats.py <channel>"

#NOTE: Twitch's IRC doesn't send certain special characters to sockets, so those won't be logged (like some of them here: http://www.umingo.de/doku.php?id=misc:chat_smileys)
#NOTE: This is meant to be done a few times per stream approximately (not like 100 times per stream). So if you start recording the chat, then restart 5 mins later, the old version will be overwritten, but if you start recording the chat then restart the program 2 hours later, it will start recording new logs. The filename represents when the chat recordings were started.
#NOTE: 'rate' is in messages per minute

verbose = True
include_emotes = False

import sys
import os
import time
import string
import datetime
import urllib2
import json
from twitch_chat_listen import listen
try:
    from pass_info import get_password, get_username
except ImportError:
    print "Error loading Twitch password info"
    print "You need to defined pass_info.py with your username and oauth password"

if (len(sys.argv) == 1):
    channel = raw_input("Chat to join: ")
else:
    channel = sys.argv[1]

#thanks to http://twitchemotes.com/ :-)
def getEmotes():
    emotelist = [':)',':(',':o',':z','B)',':/',';)',';p',':p',';P',':P','R)','o_O','O_O','o_o','O_o',':D','>(','<3']
    print "loading emotes..."
    normal = json.load(urllib2.urlopen('http://twitchemotes.com/global.json'))
    emotelist.extend(normal.keys())
    print "loaded global emotes. loading sub emotes..."
    subs = json.load(urllib2.urlopen('http://twitchemotes.com/subscriber.json'))
    for channel in subs.keys():
        emotelist.extend(subs[channel]['emotes'].keys())
    print "loaded sub emotes."
    return emotelist

emotelist = getEmotes()
emotelist.remove('GG')
emotelist.remove('Gg')

directory = "logs/" + channel + '_' + datetime.datetime.now().strftime('%B-%d-%Y_%H-00-00') 
if not os.path.exists(directory):
    os.makedirs(directory)
print 
print "Writing to " + directory
print

def open_file(kind, extension='log'):
    filename = ""
    filename += kind+'.'+extension
    file_path = os.path.relpath(directory + '/' + filename)
    return open(file_path, 'w')

authors = open_file('authors') #to get the most active users
messages = open_file('messages') #literal log of the messages - for average message length, etc.
words = open_file('words') #to get word cloud
emotes = open_file('emotes') #for emote stats
rate = open_file('rate', 'csv') #how fast chat is going
files = [authors, messages, words, emotes, rate]

def isMessage(data):
    return len(data.split('tmi.twitch.tv PRIVMSG #')) > 1

def formatMessage(message):
    #TODO: remove the "action" stuff for "/me"s
    return message.strip().split('\n')[0].split('\r')[0]

num_messages = 0
minute = 0

def log(author, message):
    global minute
    global num_messages
    global last_min
    num_messages += 1
    message = formatMessage(message)

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
    #RATE
    t = time.time()
    if t - last_min > 60:
        r = float(num_messages) / (t-last_min) * 60.0
        rate.write(str(minute)+','+str(r)+'\n')
        num_messages = 0
        minute += 1
        last_min = t

    for f in files:
        f.flush()

def endProgram():
    for f in files:
        f.close()
#TODO: output stats. (aka the main point of this program.)
    sys.exit()

def interpret(data):
    if isMessage(data):
        try:
            author = data.split('@')[1].split('.tmi.twitch.tv')[0]
            s = channel + ' :'
            message = s.join(data.split(s)[1:])
            message = filter(lambda x: x in string.printable, message)
            log(author, message)
            if verbose:
                print (author + ' - ' + message).strip()
        except IndexError:
            return

nick = get_username()
PASS = get_password()

print
print "===============================STARTING CHAT INPUT=============================="
last_min = time.time()
listen(channel, nick, PASS, interpret)
print "==================================ENDING PROGRAM================================"
endProgram()

