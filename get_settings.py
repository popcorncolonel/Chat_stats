#turns the ini file into a dictionary of {string:string}
def getSettings():
    with open('chat_stats.ini', 'r') as settings:
        settings = list(settings)
        settingsDict = {}
        for setting in settings:
            setting = setting.split('=')
            try:
                settingsDict[setting[0]] = setting[1]
            except IndexError:
                continue
    return settingsDict

