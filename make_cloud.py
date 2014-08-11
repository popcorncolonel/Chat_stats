#TODO? Make emote cloud the actual pictures of the emotes? How bad of an idea is that. I don't know.

import os
import sys
import datetime
import random
import urllib2
from global_consts import w_emotes, h_emotes, w_words, h_words
try:
    import wordcloud
except ImportError:
    print "Looks like you're missing one of the wordcloud dependencies - Check the Github page at https://github.com/popcorncolonel/chat_stats to see what you need to install."
    sys.exit()

def make_cloud(channel, time, myType=None, drawLabels=True, font_path=None):
    #get the log file
    directory = "logs/" + channel + '/' + time 

    if myType == None:
        file_path = os.path.relpath(directory + '/words.log')
        with open(file_path, 'r') as f:
            words = f.read().upper()

        file_path = os.path.relpath(directory + '/emotes.log')
        with open(file_path, 'r') as f:
            emotes = " ".join(filter(lambda x:len(x)>3, f.read().split('\n')))

        directory = "images/" + channel + '/' + time
        if not os.path.exists(directory):
            os.makedirs(directory)

        print "Generating word cloud... Hold on! (This takes a while if there are a lot of messages)"
        scale = 2
        w = wordcloud.process_text(words, max_features=1000)
        elements = wordcloud.fit_words(w, width=w_words/scale, height=h_words/scale)
        wordcloud.draw(elements, os.path.relpath(directory + '/wordcloud.png'), 
                       width=w_words/scale, height=h_words/scale, scale=scale)
        print "Word cloud created!"

        print "Generating emote cloud..."
        w = wordcloud.process_text(emotes, max_features=1000)
        elements = wordcloud.fit_words(w, width=w_emotes, height=h_emotes)
        wordcloud.draw(elements, os.path.relpath(directory + '/emotecloud.png'), 
                       width=w_emotes, height=h_emotes)
        print "Emote cloud created!"
    else: #if running the program manually. this is mainly for my debugging purposes.
        w_custom = 1100
        h_custom = 700
        file_path = os.path.relpath(directory + '/'+myType+'.log')

        directory = "images/" + channel + '/' + time
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'r') as f:
            data = f.read()
        if myType.lower() == 'authors':
            data = data.upper()
        print "Generating " +myType+ " cloud... Hold on!"
        scale = 2
        w = wordcloud.process_text(data, max_features=1000)
        elements = wordcloud.fit_words(w, width=w_custom/scale, 
                                       height=h_custom/scale, font_path=font_path)
        wordcloud.draw(elements, os.path.relpath(directory + '/'+myType+'cloud.png'), 
              width=w_custom/scale, height=h_custom/scale, scale=scale, font_path=font_path)
        print myType + " cloud created!"


chan = None
time = None
argv = sys.argv
if argv[0] == __file__:
    try:
        chan = argv[1]
        time = argv[2]
        myType = None
        font_path = None
        if len(argv) >= 4:
            myType = argv[3]
        if len(argv) >= 5:
            font_path = "C:\\Windows\\Fonts\\"+argv[4]+".ttf"
        make_cloud(chan, time, myType=myType, font_path=font_path)
    except IndexError:
        pass


