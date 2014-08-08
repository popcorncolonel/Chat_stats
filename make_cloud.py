import os
import sys
import datetime
import random
import urllib2
try:
    import wordcloud
except ImportError:
    print "Looks like you're missing one of the wordcloud dependencies - Check the Github page at https://github.com/popcorncolonel/chat_stats to see what you need to install."
    sys.exit()

def make_cloud(channel, time, myType=None, drawLabels=True):
    #get the log file
    directory = "logs/" + channel + '/' + time 

    if myType == None:
        file_path = os.path.relpath(directory + '/words.log')
        with open(file_path, 'r') as f:
            words = f.read()

        file_path = os.path.relpath(directory + '/emotes.log')
        with open(file_path, 'r') as f:
            emotes = f.read()

        directory = "images/" + channel + '/' + time
        if not os.path.exists(directory):
            os.makedirs(directory)

        w_words = 1600
        h_words = 900
        print "Generating word cloud... Hold on! (This takes a while if there are a lot of words)"
        w = wordcloud.process_text(words, max_features=1000)
        elements = wordcloud.fit_words(w, width=w_words, height=h_words)
        wordcloud.draw(elements, os.path.relpath(directory + '/wordcloud.png'), width=w_words, height=h_words, scale=1)
        print "Word cloud created!"

        w_emotes = 1600
        h_emotes = 900
        print "Generating emote cloud..."
        w = wordcloud.process_text(emotes, max_features=1000)
        elements = wordcloud.fit_words(w, width=w_emotes, height=h_emotes)
        wordcloud.draw(elements, os.path.relpath(directory + '/emotecloud.png'), width=w_emotes, height=h_emotes)
        print "Emote cloud created!"
    else: #if running the program manually
        w_custom = 1600
        h_custom = 900
        file_path = os.path.relpath(directory + '/'+myType+'.log')
        with open(file_path, 'r') as f:
            data = f.read()
        print "Generating " +myType+ " cloud... Hold on!"
        w = wordcloud.process_text(data, max_features=1000)
        elements = wordcloud.fit_words(w, width=w_custom, height=h_custom)
        wordcloud.draw(elements, os.path.relpath(directory + '/'+myType+'.png'), width=w_custom, height=h_custom)
        print myType + " cloud created!"


chan = None
time = None
try:
    chan = sys.argv[1]
    time = sys.argv[2]
    myType = None
    if len(sys.argv) > 3:
        myType = sys.argv[3]
    #raise IndexError
    make_cloud(chan, time, myType)
except IndexError:
    pass


