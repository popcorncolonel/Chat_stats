include_emotes = False #include emotes in the words wordcloud?
create_graph = True #create graph of the chat+viewership over time? Need matplotlib for this. 
                    #Which you should have anyway because it's awesome.
create_wordcloud = True #create wordclouds of the chat? Need word_cloud for this.

verbose = False #default=False
debug = False #It won't log any information.
timezone = None #Change this if you want to manually input the timezone.
                #My program will try to automatically guess it for you, though.

#dimensions of the emote cloud
w_emotes = 1600
h_emotes = 900

#dimensions of the word cloud
w_words = 1600
h_words = 900
#w_words = 3000
#h_words = 1800
