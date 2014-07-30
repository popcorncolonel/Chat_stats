import os
import sys

#USAGE: python log_reader.py channel July-27-2014_20-00-00 kind
#EXAMPLE: 
#EXAMPLE (with filter words): python log_reader.py monotonetim July-27-2014_20-00-00 words Kappa Keepo
#NOTE: This file reads each line. So, it's probably not a good thing to look at words.log...
#NOTE: filter words only look at words 

filter_words = []

if len(sys.argv) == 1:
    channel = raw_input("Channel log to get data from: ")
    date = raw_input("Datetime ('July-27-2014_15-00-00'): ")
    kind = raw_input("Log file to read ('authors', 'emotes'): ")
elif len(sys.argv) == 2:
    channel = sys.argv[1]
    date = raw_input("Datetime ('July-27-2014_15-00-00'): ")
    kind = raw_input("Log file to read ('messages', 'authors', 'emotes'): ")
elif len(sys.argv) == 3:
    channel = sys.argv[1]
    date = sys.argv[2]
    kind = raw_input("Log file to read ('messages', 'authors', 'emotes'): ")
else:
    channel = sys.argv[1]
    date = sys.argv[2]
    kind = sys.argv[3]
    filter_words = sys.argv[4:]

#dictionary with all the counts of the words
d = {}

directory = "logs/" + channel + '_' + date
file_path = os.path.relpath(directory + '/' + kind + '.log')

log = open(file_path, 'r')
lines = list(log) #this works! wow! cool!
if kind == 'words':
    lines = lines[0].split(' ')

if filter_words != []:
    lines = filter(lambda x:x.lower() in filter(lambda x:x.lower(), filter_words), lines)

for word in lines:
    word = word.strip()
    try:
        d[word] += 1
    except KeyError:
        d[word] = 1

# sort it - most first
import operator
sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1))
for key in sorted_d:
    print key[0] + ': ' + str(key[1])

