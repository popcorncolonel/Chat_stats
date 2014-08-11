#Logs in to a chat and listens to the messages, calling a function each distinct line of message

#NOTE: interactive mode is off. i.e. you can call listen() then call end_program on the next line and it'll go until an exception is caught.

import socket
import time

def connect(channel, nick, PASS):
    join = "#" + channel
    while True:
        sock = socket.socket()
        sock.connect(("irc.twitch.tv",80))
        sock.send("USER " + nick + " 0 * :" + nick + "\r\n")
        sock.send("PASS " + PASS + "\r\n")
        sock.send("NICK " + nick + "\r\n")
        sock.send("MODE " + nick + " +B\r\n")
        sock.send("JOIN " + join + "\r\n")
        break
    except socket.error:
        print "Connection timeout D: retrying"
        pass
    return sock

#f is the function to be called on each line of data
def listen(channel, nick, PASS, interpret):
    try:
        sock = connect(channel, nick, PASS)
        while True:
           data = ''
           try:
               data = sock.recv(512)
           #except ValueError:
           #    pass
           except socket.error: #if the user's connection blips
               print "connection error, attempting to listen"
               time.sleep(5)
               sock = connect(channel, nick, PASS)
               pass
           if data[0:4] == "PING":
              sock.send(data.replace("PING", "PONG"))
           #I split the data like this because the sockets sometimes concats the data in a weird way. This ameliorates that problem.
           for line in data.split('\n'):
               if line != '':
                   interpret(line)
    except KeyboardInterrupt, SystemExit:
        return

