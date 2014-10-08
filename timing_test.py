
from psychopy import visual, core, event, logging 
import datetime, sys

#for parallel triggers
if sys.platform.startswith('win'):
    from ctypes import windll

global gInterval; gInterval = 1000
global run; run = True
global gFrameInterval; gFrameInterval = 60
global triggers; triggers = False
global trigDuration; trigDuration = 10 #ms

global gStartTime; gStartTime = datetime.datetime.utcnow()

def msTime():
    delta = datetime.datetime.utcnow() - gStartTime
    return delta.total_seconds()#delta#int(delta.total_seconds() * 1000)

#setup log
myLogLevel = logging.CRITICAL + 1
logging.addLevel( myLogLevel, '' )
myLog = logging.LogFile( '.\\timings.log', filemode='w', level = myLogLevel, encoding='utf8') #= myLogLevel )

coreClock = core.Clock()
logging.setDefaultClock( coreClock )

logging.log('Run: ' + str(datetime.datetime.utcnow()) , myLogLevel)

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

    logging.log( msTime(), myLogLevel )
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