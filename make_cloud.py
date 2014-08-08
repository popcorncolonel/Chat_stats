import os
import sys
import datetime
import random
import urllib2
import wordcloud
try:
    #TODO: put import word_cloud here
    print
except ImportError:
    print "Looks like you're missing some dependencies - Check the Github page at https://github.com/popcorncolonel/chat_stats to see what you need to install."
    sys.exit()

def make_cloud(channel, time, drawLabels=True):
    #get the log file
    directory = "logs/" + channel + '/' + time 
    file_path = os.path.relpath(directory + '/emotes.log')
    with open(file_path, 'r') as f:
        emotes = f.read()

    file_path = os.path.relpath(directory + '/words.log')
    with open(file_path, 'r') as f:
        words = f.read()

    directory = "images/" + channel + '/' + time
    if not os.path.exists(directory):
        os.makedirs(directory)

    w = wordcloud.process_text(words, max_features=2000)
    elements = wordcloud.fit_words(w, width=500, height=500)
    wordcloud.draw(elements, os.path.relpath(directory + '/wordcloud.png'), width=500, height=500, scale=2)

    w = wordcloud.process_text(emotes, max_features=2000)
    elements = wordcloud.fit_words(w, width=500, height=500)
    wordcloud.draw(elements, os.path.relpath(directory + '/emotecloud.png'), width=500, height=500, scale=2)

chan = None
time = None
try:
    chan = sys.argv[1]
    time = sys.argv[2]
    #raise IndexError
    make_cloud(chan, time)
except IndexError:
    pass


