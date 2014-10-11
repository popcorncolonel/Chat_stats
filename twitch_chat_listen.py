#Logs in to a chat and listens to the messages, calling a function each distinct line of message

#NOTE: interactive mode is off. i.e. you can call listen() then call end_program on the next line and it'll go until an exception is caught.

import socket
import time

def connect(channel, nick, PASS, server, port):
    if channel[0] != '#':
        join = '#' + channel
    else:
        join = channel
    while True:
        try:
            sock = socket.socket()
            sock.connect((server, port))
            sock.send("USER " + nick + " 0 * :" + nick + "\r\n")
            if PASS != '':
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
#endFunc is a function that, when called, if it returns true then the loop
#        will stop. By default (without this function being passed in), 
#        this program will loop forever when called
def listen(channel, nick, PASS, interpret, endFunc=None, server='irc.twitch.tv', port=80):
    try:
        sock = connect(channel, nick, PASS, server, port)
        sock.settimeout(6) #so we can frequently check for endFunc
        while True:
           data = ''
           while True:
               try:
                   data = sock.recv(512)
                   break
               except socket.timeout:
                   if endFunc and endFunc():
                       return
                   continue
               except socket.error: #if the user's connection blips
                   print "connection error, attempting to listen"
                   time.sleep(5)
                   sock = connect(channel, nick, PASS)
                   sock.settimeout(6) #so we can frequently check for endFunc
                   break
           if data[0:4] == "PING":
              sock.send(data.replace("PING", "PONG"))
           #I split the data like this because the sockets sometimes concats the data in a weird way. This ameliorates that problem.
           for line in data.split('\n'):
               if line != '':
                   interpret(line)
    except KeyboardInterrupt, SystemExit:
        print "finishing this"
        raise
        return

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
# channel, nick, password, [server], [port]
    print args
    try:
        channel = args[0]
    except IndexError:
        channel = raw_input('Channel to join: ')

    try:
        nick = args[1]
    except IndexError:
        nick = raw_input('Nick to use: ')

    try:
        PASS = args[2]
    except IndexError:
        PASS = raw_input('Password (might be OAUTH): ')

    try:
        server = args[3]
    except IndexError:
        server = raw_input('Server (if twitch channel, just press enter): ')
        if server == '': #if it's a twitch channel
            server = 'irc.twitch.tv'
            port = 6667
            if channel != '' and channel[0] != '#':
                print channel
                print channel[0]
                channel = '#' + channel

    if server != 'irc.twitch.tv':
        try:
            port = int(args[4])
        except IndexError:
            port = int(raw_input('Port: '))
    print channel, nick, PASS, server, port
    def interpret(data):
        print data
    listen(channel, nick, PASS, interpret, server=server, port=port)

