
from psychopy import visual, core, event, logging 
import datetime, time, sys

#for parallel triggers
if sys.platform.startswith('win'):
    from ctypes import windll

global gInterval; gInterval = 1000
global run; run = True
global gFrameInterval; gFrameInterval = 60
global triggers; triggers = False
global trigDuration; trigDuration = 10 #ms

global gStartDt; gStartDt = datetime.datetime.utcnow()
global gStartTt; gStartTt = time.time();
global gStartTc; gStartTc = time.clock();

def msTime():
    deltadt = datetime.datetime.utcnow() - gStartDt
    deltatt = time.time() - gStartTt
    deltatc = time.clock()
    return deltadt.total_seconds(), deltatt, deltatc 
    #delta#int(delta.total_seconds() * 1000)

#setup log
myLogLevel = logging.CRITICAL + 1
logging.addLevel( myLogLevel, '' )
myLog = logging.LogFile( '.\\timings.log', filemode='w', level = myLogLevel, encoding='utf8') #= myLogLevel )

coreClock = core.Clock()
logging.setDefaultClock( coreClock )

logging.log('Run: ' + str(datetime.datetime.utcnow()) , myLogLevel)
logging.log('PP timestamp, datetime, timetime, timeclock', myLogLevel)
#setup window
win = visual.Window([400,400])
msg = visual.TextStim(win, text='<esc> to quit')
msg.draw()
win.flip()

while run:
    
    for i in range( gFrameInterval ): #accurate timing trick
        msg.setText('<esc> to quit\n' + str(i))
        msg.draw(win)
        win.flip()

    times = msTime()
    logging.log( str(times[0]) + ', ' + str(times[1]) + ', ' + str(times[2]), myLogLevel )
    logging.flush()

    if triggers:
        windll.inpout32.Out32(paraport, 0x10 )
        core.wait( trigDuration/1000.0, hogCPUperiod = trigDuration/1000.0 ) #<-- add this for parallel triggering
        windll.inpout32.Out32(paraport, 0x00 ) #<-- add this for parallel triggering

    if 'escape' in event.getKeys():
        run = False
   
#cleanup  
logging.flush()
win.close()
core.quit()