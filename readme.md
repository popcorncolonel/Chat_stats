###USAGE###
"python chat_stats.py [channel]"

###GETTING THE DATA###
* Check the logs directory that is created after running chat_stats.py 
* Get the name of the directory you want to read from.  
* Use the command "python log_reader.py [channel] [dir name] [name of log file]"  

###DEPENDENCIES###
[Matplotlib](http://matplotlib.org/downloads.html) - Graph creation (if you keep create_images as True).  
[word_cloud](https://github.com/amueller/word_cloud) - Word cloud creation. This can be a pain to install on Windows though. An alternative to this is just to copy+paste the contents of words.log to http://www.wordle.net.  
* [Python Imaging Library](http://www.pythonware.com/products/pil/) - Word cloud creation.  
* [Cython](http://cython.org/#download) - Word cloud creation.  

###TODO###
* examples folder. listed inline in this file.
* Words per message?  
* Create images (graphs) of the most used emotes

###"I found a bug!"###
[Email me](mailto:popcorncolonel@gmail.com) or [Tweet me](http://twitter.com/popcorncolonel)

