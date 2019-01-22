"""
V3: Added date support and sound on error. Added default gateway finder instead of typing it in.
V3.1: Added a last disconnect. 
v3.2: Added a one time line that shows the date. Optimized code. Fixed bugs. Added a small debug screen.
"""


import win32api, win32con
import os, re
import time
import subprocess

prevNums = []
managerNumber = 0
recentDisconnectTime = ''
dateString = ''
# TODO random crashes. Add an except statment for debug. Or keywait()

# FIXME Records an error once before sleep.
# https://stackoverflow.com/questions/16145516/detecting-computer-program-shutdown-in-python
# https://stackoverflow.com/questions/1411186/python-windows-shutdown-events

# TODO maybe a calculator to show how long the internet was out for?
# TODO change gatewayFinder() so that it only runs once.
def pingFinder():
    global managerNumber
    global amORpm
    global gatewayActual
    commandOutput = subprocess.check_output('ping -n 1 ' + gatewayActual)
    commandString = str(commandOutput)
    timeLocator = commandString.find('time=')  # ususally 102 or so
    currentPing = int((commandString[(timeLocator + 5):(timeLocator + 6)]))
    if len(prevNums) <= 10:  # Adds the pings to the list for averaging and printing
        prevNums.append(currentPing)
    elif len(prevNums) > 10:  # Removes first entry and replaces it with the new one
        del prevNums[0]
        prevNums.append(currentPing)
    avgNum = int(sum(prevNums) / len(prevNums))
    # TODO Find a replacement for lambda
    clear = lambda: os.system('cls')
    clear()
    print('PingTester to ' + gatewayActual)
    print('Avg ping: %sms' % avgNum)
    for pings in prevNums:  # Prints previous pings stored in prevNums
        print(pings, 'ms', sep='')
    print('\n\n\nLast disconnect: ', end ='')
    disconnectIteration = 0
    for i in recentDisconnectTime:
        if disconnectIteration < 2:
            print(i, end=':')
            disconnectIteration += 1
        else:
            print(i, amORpm, '\n', sep='')
    managerNumber = 0  # Resets the soundManager since ping was successful

# TODO Needs optimazation
def timesorter():
    global recentDisconnectTime
    global amORpm, dateString, hour, minutes, seconds
    timeLocal = win32api.GetLocalTime()
    dateString, amORpm ='', 'am'
    hour, minutes, seconds = timeLocal[4], timeLocal[5], timeLocal[6]
    if hour == 0: hour = 12
    elif hour == 12: amORpm = 'pm'
    elif hour > 12:
        hour -= 12
        amORpm = 'pm'
    # Time is done. Now to handle the dates. Written days after.
    dateStamp = timeLocal[1], timeLocal[3], timeLocal[0]
    dateIteration = 0
    for dates in dateStamp:
        if dateIteration < 2:
            dateString += str(dates) + '-'
            dateIteration += 1  # Without this, format would be '6-26-2017-'
        else:
            dateString += str(dates)
    recentDisconnectTime = hour, minutes, seconds
    return hour, minutes, seconds, amORpm, dateString, recentDisconnectTime  # Returns the time of the error

def activeTester():
    try:
        pingFinder()
    except subprocess.CalledProcessError:
        print('Connection Failed!')
        soundManager(), timesorter(), toDateOrNotToDate()
        # TODO change this write command to be better. Call globals for time too.
        fd = open('ConnectionLog.txt', mode='a')
        fd.write('Error occured @ %s:%s:%s%s\n' % (hour, minutes, seconds, amORpm))
        fd.close()

def soundManager():
    global managerNumber
    if managerNumber == 0:
        win32api.MessageBeep(win32con.MB_ICONHAND)
        managerNumber += 1
    else:
        pass
    return 1  # Returns value so that it doesn't run again during same outage.

# All lines in ConnectionLog gets added to dateEntryDecider
# The list is then parsed with the parser varible
# Then, it's converted to boolean and writes the date to file if it's not there and passes if it does.
def toDateOrNotToDate():
    dateEntryDecider = []
    global dateString
    with open('ConnectionLog.txt') as f:
        for lines in f: dateEntryDecider.append(lines)
    parser = re.compile(dateString).search(str(dateEntryDecider))
    if not bool(parser):
        fd = open('ConnectionLog.txt', 'a')
        fd.write('-------------%s-------------\n' % dateString)
        fd.close()
    else: pass
## -------------------------------------------------------------------##

def gatewayFinder():
    global  gatewayActual
    commandOutput = str(subprocess.check_output('ipconfig'))
    gatewayPlace = commandOutput.find('Default ')
    gatewayActual = commandOutput[gatewayPlace + 36:gatewayPlace + 47]
    return gatewayActual

# Run once:
gatewayFinder()

try:
    while True:
        activeTester()
        time.sleep(2)
except:
    input('''This should not be seen by anyone. Tell me if you can see this.
         \nDo not close this window. 
         \nPress enter to continue.
         ''')

