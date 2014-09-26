#!/usr/bin/env python

import webapp2

class Versions(webapp2.RequestHandler):
    def options(self):      
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE'
    
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        version_history = {}

        version_history['0.5'] = '*Test 1'
        version_history['0.5'] += '*Test 2'

        version_history['1.0'] = '*Initial release!'

        version_history['1.01'] =  '*Added options file where you can specify various things about how the program runs'
        version_history['1.01'] += '*Examples: Width of wordclouds, '
        version_history['1.01'] += 'whether or not to include emotes in the word cloud, manual timezone setting'
        version_history['1.01'] += '*To change settings, change the chat_stats.ini file'

        version_history['1.02'] =  '*The .exe version now should work on more systems.'
        version_history['1.02'] += '*.exe version also has 2 new executables, make_cloud.exe and make_plot.exe so you can '
        version_history['1.02'] += 'remake the clouds again if you want new colors, a new layout, etc.'
        version_history['1.02'] += '*Note: old logs still work with newer versions.'

        s = str(version_history)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(s)

class Changelog(webapp2.RequestHandler):
    def options(self):      
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE'
    
    def get(self):
        self.response.out.write('TODO: this.')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('http://github.com/popcorncolonel/chat_stats')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/versions', Versions),
    ('/changelog', Changelog)
], debug=True)
