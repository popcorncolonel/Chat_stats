#TODO: further y2_interval. 300k min.

import os
import sys
import datetime
import random
import urllib2
import string
try:
    from dateutil.tz import *
    from matplotlib import rc
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.patheffects as PathEffects
    from matplotlib.ticker import FuncFormatter
except ImportError:
    print "Looks like you're missing some of the matplotlib dependencies - Check the Github page at https://github.com/popcorncolonel/chat_stats to see what you need to install."
    raise

#leaves max(0, padding_mins) zeroes at the end to make it look more natural.
def remove_trailing_zeroes(rates):
    new_rates = []
    while rates[-1].split(',')[1] == '0':
        rates.pop()
    for rate in rates:
        new_rates.append(rate)
    return new_rates

def get_xinterval(dur):
    interval = 1
    if dur > 20:
        interval = 2
    if dur > 30:
        interval = 5
    if dur > 90:
        interval = 10
    if dur > 150:
        interval = 15
    if dur > 240:
        interval = 30
    if dur > 700:
        interval = 60
    if dur > 1400:
        interval = 120
    if dur > 2700:
        interval = 180
    if dur > 5400:
        interval = 360
    if dur > 10800:
        interval = 720
    return interval

def get_yinterval(max_viewercount):
    interval = 1
    if max_viewercount > 10:
        interval = 2
    if max_viewercount > 30:
        interval = 5
    if max_viewercount > 60:
        interval = 10
    if max_viewercount > 90:
        interval = 15
    if max_viewercount > 140:
        interval = 20
    if max_viewercount > 300:
        interval = 50
    if max_viewercount > 600:
        interval = 100
    if max_viewercount > 1400:
        interval = 200
    if max_viewercount > 3000:
        interval = 500
    if max_viewercount > 4500:
        interval = 750
    if max_viewercount > 6000:
        interval = 1000
    if max_viewercount > 12000:
        interval = 2000
    if max_viewercount > 30000:
        interval = 5000
    if max_viewercount > 60000:
        interval = 10000
    return interval

def make_plot(channel, time, drawLabels=True):
    #get the log file
    directory = "logs/" + channel + '/' + time 
    filename = 'rate.csv'
    file_path = os.path.relpath(directory + '/' + filename)

    with open(file_path, 'r') as rate:
        rates = map(lambda x:x.strip(), list(rate))

    start_hour = int(rates[0].split('=')[1].split('_')[0])
    start_min  = int(rates[0].split('=')[1].split('_')[1])

    #Load data
    rates = rates[1:]
    events = []
    to_delete = []
    for rate in rates:
        if len(rate.split('*')) >= 3:
            events.append((int(rate.split('*')[1]), rate.split(',', 1)[1]))
            to_delete.append(rate)
    rates = [x for x in rates if x not in to_delete]
    old_len = len(rates)
    rates = remove_trailing_zeroes(rates)
    num_removed = old_len - len(rates)

    mins = map(lambda x:int(filter(lambda x:x in string.printable, x).split(',')[0]), rates)
##### XXX
    l = len(mins)
    mins = []
    for i in range(l):
        mins.append(i)
##### XXX
    y_data = map(lambda x:float(x.split(',')[1]), rates)
    show_viewers = False
    try:
        y_data2 = map(lambda x:int(x.split(',')[2]), rates)
        show_viewers = True
    except IndexError:
        print rates
        pass

    dur = mins[-1] + 1 #in minutes

    #interval = 15
    interval = get_xinterval(dur)
    padding_mins = start_min%interval
    carry = start_min/interval

    x_data = range(carry*interval, start_min + dur + min(num_removed,padding_mins))
    x = np.array(x_data)
    y = np.random.randint(1, size=padding_mins) #pad it with all 0's
    y = np.append(y, np.array(y_data))
    y = np.append(y, np.random.randint(1, size=min(num_removed, padding_mins))) #potentially add zeroes to the end
    if show_viewers:
        y2 = np.random.randint(1, size=padding_mins) #pad it with all 0's
        y2 = np.append(y2, np.array(y_data2))
        y2 = np.append(y2, np.random.randint(1, size=min(num_removed, padding_mins))) #potentially add zeroes to the end
    #print len(x)
    #print len(y)
    #print len(y2)
    times = time.split('-') #2014-08-23-04AM

    try:
        year = int(times[0])
        mo = int(times[1])
        day = int(times[2])
        hour = start_hour
        minute = start_min
        minute = 0 #?????????????????????????????????????????????????????????????
        start_time = datetime.datetime(year, mo, day, hour, minute, 0)
    except ValueError: #debugging.
        print "THIS SHOULD NEVER HAPPEN! Email me popcorncolonel@gmail.com right away!"
        start_time = datetime.datetime(2014, 8, 11, start_hour, start_min)

    #Removes leading zeroes from all the "words" in s.
    #"00138 hello 01AM" -> "138 hello 1AM"
    def removeLeadingZeroes(s):
        return " ".join(map(lambda x: x.lstrip('0'), s.split(" ")))

    def formatTime(x, pos):
        #timestamp = (start_time - datetime.datetime(1970, 1, 1)).total_seconds() + x*60
        #now_time = datetime.datetime.fromtimestamp(timestamp) #does not convert time zones. Need time zones.
        now_time = datetime.timedelta(hours=float(x)/60) + start_time
        if dur > 2160: #Aug 5, 8AM 
            return removeLeadingZeroes(now_time.strftime("%b %d, %I %p"))
        elif interval >= 60: #8AM
            return removeLeadingZeroes(now_time.strftime("%I %p"))
        else: #7:45 AM
            return removeLeadingZeroes(now_time.strftime("%I:%M %p"))
    print "Drawing rate over time graph..."

    #START GRAPHING
    #plt.figure(num=None, figsize=(36, 16), dpi=80)
    plt.figure(num=None, figsize=(27, 12), dpi=80)

    #fig, ax = plt.subplots()
    ax = plt.axes()
    ax.xaxis.grid(True)
    ax.xaxis.set_major_formatter(FuncFormatter(formatTime))
    ax.yaxis.grid(True)
    ax.grid(True)

    r = 45
    if dur >= 2160:
        r = 270
    plt.xticks(np.arange(min(x), max(x)+1, interval), rotation=r)
    months = ['','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    try:
        i = int(times[1])
        mon = months[i] 
        ye = int(times[2]) 
        da = int(times[0]) 
        plt.title("%s - %s %d, %d\n" %(channel, mon, ye, da))
    except (ValueError, IndexError):
        plt.title(channel+'\n')

    local_timezone = datetime.datetime.now(tzlocal()).tzname() #Eastern Daylight Time
    split = local_timezone.split(" ")
    if len(split) > 1:
        local_timezone = "".join([word[0] for word in split])
    avg_mpm = np.mean(y)
    plt.xlabel('\nTimes in ' + local_timezone)
    plt.ylabel('\nMessages per minute (Avg=%0.2f)\n' %avg_mpm, color='blue')
    for tl in ax.get_yticklabels():
        tl.set_color('blue')
    plt.plot(x,y,linewidth=2,color='#4422AA')
    
    if show_viewers:
        ax2color = 'green'
        ax2 = ax.twinx()
        ax2.plot(x,y2,linewidth=4,color=ax2color)
        ax2.fill_between(x,0,y2,color=ax2color, alpha=0.1)
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        ax2.yaxis.set_ticks_position('right')
        ax2.yaxis.set_label_position('right')
        avg_viewercount = np.mean(y2)
        ax2.set_ylabel('\nViewercount (Avg=%0.1f)\n' %avg_viewercount, color=ax2color, rotation=270)
        m =  1.16*max(y)
        m2 = 1.16*max(y2)
        ax.set_yticks( np.arange(0, m,   get_yinterval(max(y))))
        ax2.set_yticks(np.arange(0, m2, get_yinterval(max(y2))))
        ax.set_ylim(0, m)
        ax2.set_ylim(0, m2)
        for tl in ax2.get_yticklabels():
            tl.set_color(ax2color)

    ax.fill_between(x,0,y,color='#5577DD')
    font = {'size' : 25}
    rc('font', **font)

    ticklist = ax2.get_yticks()
    height_diff = ticklist[1] - ticklist[0]
    height_offset = ticklist[1]
    init_offset = height_offset
    ha = 'center'
    for event in events:
        if drawLabels:
            plt.axvline(x=event[0]+padding_mins+carry*interval, color='red', linewidth=2, label=event[1])
            s = event[1].replace('\\n', '\n')
            down = ax2.yaxis.get_view_interval()[1]-height_offset
            plt.text(event[0]+padding_mins+carry*interval, 
                    down, s, color='red', verticalalignment='top', 
                    horizontalalignment=ha, fontsize=25, rotation=0, #rotation=270,
                    path_effects=[PathEffects.withSimplePatchShadow(linewidth=2)])
                    #path_effects=[PathEffects.withStroke(linewidth=1,foreground="black")])
            height_offset = (height_offset + height_diff) if height_offset == init_offset else init_offset
            #height_offset = height_diff - height_offset
    #S E L L O U T
    plt.text(0.01,0.99, 'github.com/popcorncolonel/chat_stats', color='#666666', verticalalignment='top',
            horizontalalignment='left', fontsize=25, rotation=0, transform=ax.transAxes)
    plt.text(0.99,0.99, 'http://twitch.tv/'+channel, color='#666666', verticalalignment='top', 
            horizontalalignment='right', fontsize=25, rotation=0, transform=ax.transAxes)
    #plt.text(-0.05, -0.170, 'http://github.com/popcorncolonel/chat_stats', color='grey', verticalalignment='top',
    #        horizontalalignment='left', fontsize=25, rotation=0, transform=ax.transAxes)
    #plt.text(1.05, -0.170, 'http://www.twitch.tv/'+channel, color='grey', verticalalignment='top', 
    #        horizontalalignment='right', fontsize=25, rotation=0, transform=ax.transAxes)

    #plt.show() #for running locally rather than saving the figure

    directory = "images/" + channel + '/' + time
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(directory + '/rate.png', bbox_inches='tight')
    print "Rate graph completed!"

chan = None
time = None
#if sys.argv[0] == __file__:
if __name__ == '__main__':
    try:
        chan = sys.argv[1]
        time = sys.argv[2]
        make_plot(chan, time)
    except IndexError:
        pass

