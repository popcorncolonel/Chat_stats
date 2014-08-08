import os
import sys
import datetime
import random
import urllib2
try:
    import word_cloud
except ImportError:
    print "Looks like you're missing some dependencies - Check the Github page at https://github.com/popcorncolonel/chat_stats to see what you need to install."
    sys.exit()

def make_plot(channel, time, drawLabels=True):
    #get the log file
    directory = "logs/" + channel + '/' + time 
    filename = 'rate.csv'
    file_path = os.path.relpath(directory + '/' + filename)
#todo: make the images lol

