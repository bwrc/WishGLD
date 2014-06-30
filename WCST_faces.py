
"""
WCST experiment / ReKnow

TODO:
    - check the parallel port triggering, the logic is there (commented, search for 'add this for parallel triggering') but untested since lacking a parallel port + drivers
      for driver installation, check http://psychopy.wmwikis.net/Triggering+the+Parallel+Port+(EEG)
    - check the paths to the image files, also create a .\logs\ folder for logs
    - if working from a csv file for rule sequences: check path, and delimiter
    - check globals for configuring the test



"""

from random import randint, random, seed
from psychopy import visual,core,monitors,event,gui, logging#, parallel
from copy import deepcopy
import csv
from datetime import datetime #for date

import NewDlg #allows setting the length of textfields

# - GLOBALS -------------------------------------------------------------------------------------------
global DEBUG; DEBUG = True
global RANDOMIZE_CATEGORY_CARDS; RANDOMIZE_CATEGORY_CARDS = False
global USE_RANDOM_RULES; USE_RANDOM_RULES = False # True
global RULE_COUNT; RULE_COUNT = 20 #if read from file, this will be overridden
global SEPARATE_STIM; SEPARATE_STIM = True
global SEP_STIM_DURATION; SEP_STIM_DURATION = 20 #n of frames (16ms)
global N_OF_CARDS; N_OF_CARDS = 16

global PRESENTATION_MODE; PRESENTATION_MODE = 0

global portCodes;
portCodes = {'clear' : 0x00,\
             'rule1' : 0x01,\
             'rule2' : 0x02,\
             'rule3' : 0x04,\
             'rule4' : 0x08,\
             'cue'   : 0x10,\
             'tgtOn' : 0x20,\
             'respRight' : 0x40,\
             'respWrong' : 0x80,\
             'start': 0xfe,\
             'stop': 0xff}
             
"""
0x00 clear
0xfe start
0xff stop

0x10 cue
0x01 .. 0x08 stim on/off? + stim category

0x20 targets on (only if stim presented separately)

responses

0x40 + 0x01..0x08 right + rule
0x80 + 0x01..0x08 wrong + guess

use: writePort( respRight | rule1 )

"""
#parallel.setPortAddress(0x0378) #<-- add this for parallel triggering

def SelectCardSubset( subSetCount, deckSize ):
    """Selects a random set of subSetCount cards from a deck of deckSize cards."""
    cards =[]
    for i in range( subSetCount ):
        cards.append( randint(0, deckSize-1) )
    return cards

#setup paths
#global stimPath; stimPath = 'c:\\Kride\\Projects\\ReKnow\\WCST\\facecards\\'
#global stimPath; stimPath = 'c:\\Kride\\Projects\\ReKnow\\WCST\\shinned\\letters\\'
global stimPath; stimPath = 'c:\\Kride\\Projects\\ReKnow\\WCST\\shinned\\faces\\'
global ruleFile; ruleFile = '.\\sets.csv'

#setup rules
global rules; rules = ['G1', 'G2', 'L1', 'L2'] # face, color, shape, orientation
global currentRule; #currentRule = rules[randint(0,3)]
global ruleList; ruleList = [] #a list of tuples containing the sequence of sorting rules (0, 1, 2, 3) and required n of correct repeats per set(5, 6, 7)

#setup deck of four cards from the whole deck
deck = SelectCardSubset( 4, N_OF_CARDS )

#ruleList is a list of sorting rules and their durations
if USE_RANDOM_RULES == False: #load from ruleFile
    rf = open( ruleFile, 'rb' )
    reader = csv.reader( rf, delimiter=';' )

    for row in reader:
        ruleList.append( ( int(row[0])-1, int(row[1]) ) )
    rf.close()
    RULE_COUNT = len( ruleList )
    
    
else: #generate random set of RULE_COUNT tuples
    for i in range( RULE_COUNT ):
        ruleList.append( (randint(0, 3), randint(5, 7)) )

global currentTgt; currentTgt = (-1, -1, -1, -1)

# - FUNCTION DEFS -------------------------------------------------------------------------------------

def randomizeOrder( lst ):
    return sorted(lst, key=lambda k: random())

def SetupCategoryCards( cards, randomOrder = True ):
    order = [0, 1, 2, 3]

    # should the order of features be randomized?
    print order
    if randomOrder:
        feat1 = randomizeOrder( order )
        feat2 = randomizeOrder( order )
        feat3 = randomizeOrder( order )
        feat4 = randomizeOrder( order )
    else:
        feat1 = order
        feat2 = order
        feat3 = order
        feat4 = order
        
    #fill card parameters
    if len(cards) <> 4:
        print 'setup card count: ' + str(len(cards))
        DebugMsg( 'You have to supply 4 cards for setup' )
        return False
        
    else:

        for idx in range(4):
            cards[idx]['G1'] = feat1[idx]
            cards[idx]['G2'] = feat2[idx]
            cards[idx]['L1'] = feat3[idx]
            cards[idx]['L2'] = feat4[idx]

            cards[idx]['fn'] = stimPath +'%02d_%02d_%02d_%02d.png' % (deck[ feat1[idx]], feat2[idx], feat3[idx], feat4[idx]) 
            if DEBUG:
                print cards[idx]['fn']

    return True

def DebugMsg( msg ):
    txt = visual.TextStim( win, text=msg, pos=(150, 480), color=(1.0, 0.0, 0.0), colorSpace='rgb')
    txt.draw()

def NextTrial():

    # select next random stimcard
    global currentTgt
    currentTgt = ( randint(0, 3),\
                   randint(0, 3),\
                   randint(0, 3),\
                   randint(0, 3) )
                   
    fn = stimPath + '%02d_%02d_%02d_%02d.png' % (deck[currentTgt[0]], currentTgt[1], currentTgt[2], currentTgt[3]) 
    tgtCard.setImage( fn )

    if DEBUG:
        print 'stim: ' + fn

    if SEPARATE_STIM: #first show stimcard for a short period of SEP_STIM_DURATION (in refresh frames, x 16ms), then the target cards
        win.clearBuffer()
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['cue'], 'STIM ' + str( currentTgt[0] ) + ', ' + str( currentTgt[1] ) + ', ' +str( currentTgt[2] ) + ', ' +str( currentTgt[3] ) )
                #logThis('STIM ' + currentTgt )#trig & log

        win.flip() #clear

    else: # show all cards at the same time
        tgtCard.draw(win)

#logThis('STIM ' + str(currentTgt[0]) + ',' + str(currentTgt[1]) + ',' + str(currentTgt[2]) + ',' + str(currentTgt[3]) )#trig & log
    
    for c in stimCards:
        c.draw(win)

    if DEBUG:
        logThis( 'cr: ' + str(currentRule) )
        DebugMsg( 'current rule ' + str(currentRule) )

    win.flip()
    
    triggerAndLog( portCodes['tgtOn'], \
            'TGT ' + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
                   + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
                   + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
                   + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )
    
#    + tgtCards[1] + tgtCards[2] + tgtCards[3] )  
    
    #trig & log

def ShowInstruction( txt, duration ):
    instr = visual.TextStim( win, text=txt, pos=(0,0), color=(0.0, 0.0, 0.0), colorSpace='rgb', height=50 )
    instr.draw(win)
    win.flip()
    if duration < 0:
        event.waitKeys()
    else:
        core.wait( duration )

    win.flip() #clear screen
    

def CheckCard( stimNum, currentRule, currentTgt ):
    cardOK = False

    if currentRule == 'G1':
        if tgtCards[stimNum]['G1'] == currentTgt[0]:
            cardOK = True
    
    if currentRule == 'G2':
        if tgtCards[stimNum]['G2'] == currentTgt[1]:
            cardOK = True

    if currentRule == 'L1':
        if tgtCards[stimNum]['L1'] == currentTgt[2]:
            cardOK = True
    
    if currentRule == 'L2':
        if tgtCards[stimNum]['L2'] == currentTgt[3]:
            cardOK = True
        
    if cardOK:
        return True
    else:
        return False

# - MAIN PROG -------------------------------------------------------------------------------------

# Gather info / dialog

#init random seed
seed()

myDlg = NewDlg.NewDlg(title="The amazing ReKnow mindfuck")

myDlg.addText('Subject info')
myDlg.addField('SubjID:', width=30)
myDlg.addField('Age:', 18)

myDlg.addText('Experiment Info')
myDlg.addField('Randomize Category Cards:', choices=["No", "Yes"])
myDlg.addField('Select presentation mode', choices=["Sequential, Feedback:R/W", \
                                                     "Sequential, Feedback: stimcard",\
                                                     "Sequential, Feedback: framed target",\
                                                     "Concurrent",\
                                                     ])
myDlg.addField('Group:', choices=["Test", "Control"])

myDlg.show()  # show dialog and wait for OK or Cancel

if myDlg.OK:  # then the user pressed OK
    confInfo = myDlg.data
    print confInfo
else:
    print 'user cancelled'
    win.close()
    core.quit()

# SETUP LOGGING & CLOCKING
testClock = core.Clock()
logging.setDefaultClock( testClock )

myLogLevel = logging.CRITICAL + 1
logging.addLevel( myLogLevel, '' )
myLog = logging.LogFile( '.\\logs\\' + confInfo[0] + '.log', filemode='w', level = myLogLevel, encoding='utf8') #= myLogLevel )

def logThis( msg ):
    logging.log( msg, level=myLogLevel )

logThis('Subj ID: ' + confInfo[0] )
logThis('Run: ' + str(datetime.utcnow()) )
logThis('Age: ' + str(confInfo[1]) )

def triggerAndLog( trigCode, msg, trigDuration=10 ):
    #parallel.setData( trigCode ) #<-- add this for parallel triggering
    logThis( msg )
    #core.wait( trigDuration/1000.0, hogCPUperiod = trigDuration/1000.0 ) #<-- add this for parallel triggering
    #parallel.setData( portCodes['clear'] ) #<-- add this for parallel triggering

if confInfo[4] == 'Test':
    logThis('Group: Test')
else:
    logThis('Group: Control')

logThis('--------------------------------------------------------')

logThis('INFO')
logThis('timestamp STIM state for each rule G1 G2 L1 L2 : 0,1,2,3')
logThis('timestamp TGT states for each card / Up, Right, Down, Left: 0,1,2,3; 0,1,2,3;...') 
logThis('timestamp RESP correct: 1, 0; rule used: G1, G2, L1, L2 ')
logThis('--------------------------------------------------------')
logThis('\n')

# SETUP TEST PARAMS
if confInfo[2] == 'No':
    RANDOMIZE_CATEGORY_CARDS = False
else:
    RANDOMIZE_CATEGORY_CARDS = True

if confInfo[3] == 'No':
    SEPARATE_STIM = False
else:
    SEPARATE_STIM = True

#rendering window setup
#myMon = monitors.Monitor('yoga', width=29.3, distance=40); myMon.setSizePix((3200, 1800))
myMon=monitors.Monitor('dell', width=37.8, distance=50); myMon.setSizePix((1920, 1080))

#pygame detects screen size correctly, but draws on a 1280x720 surface??
#pyglet reports the screen size as 1280x720
win = visual.Window( winType='pyglet', size=(1920, 1080),units='pix',fullscr=True, monitor=myMon, rgb=(1,1,1))

#init

#SetupParams()

#SETUP CARDS
cardPrototype = {'G1':0, 'G2':0, 'L1':0, 'L2':0, 'fn':''}

tgtCards = (deepcopy(cardPrototype), \
            deepcopy(cardPrototype), \
            deepcopy(cardPrototype), \
            deepcopy(cardPrototype) )

SetupCategoryCards( tgtCards )

#552 = 2*256 + 40
# cards in clockwise order: up, right, down, left

# TARGET CARD POSITIONS
"""
#cross formation
stimCards = ( visual.ImageStim( win, pos=( 0, 552) ), \
              visual.ImageStim( win, pos=( 552, 0) ), \
              visual.ImageStim( win, pos=( 0, -552) ), \
              visual.ImageStim( win, pos=( -552, 0) ))
"""
#tight form
stimCards = ( visual.ImageStim( win, pos=( 0, 266) ), \
              visual.ImageStim( win, pos=( 522, 0) ), \
              visual.ImageStim( win, pos=( 0, -266) ), \
              visual.ImageStim( win, pos=( -522, 0) ))


stimCards[0].setImage( tgtCards[0]['fn'] )
stimCards[1].setImage( tgtCards[1]['fn'] )
stimCards[2].setImage( tgtCards[2]['fn'] )
stimCards[3].setImage( tgtCards[3]['fn'] )

tgtCard = visual.ImageStim( win, pos=( 0, 0 ) )

# - BEGIN -------------------------------------------------------------------------

ShowInstruction( 'start', -1 )

#start test

cardCount = 0
rightAnswers = 0

ruleCount=0

while ruleCount < RULE_COUNT: #True: #not CheckForEndCondition() :

    currentRule = rules[ ruleList[ ruleCount ][0] ]
    ruleRepeats = int( ruleList[ruleCount][1] )

    #get a random set for every round, if wanted
    if RANDOMIZE_CATEGORY_CARDS:
        SetupCategoryCards( tgtCards )
        stimCards[0].setImage( tgtCards[0]['fn'] )
        stimCards[1].setImage( tgtCards[1]['fn'] )
        stimCards[2].setImage( tgtCards[2]['fn'] )
        stimCards[3].setImage( tgtCards[3]['fn'] )
        
    NextTrial()

    cardCount +=1
    
    if DEBUG:
        DebugMsg( 'CurRule: ' + str(currentRule) )
    
#    ClockTimes()
#    WaitKeyEvents()
#    ClockResponse()
#    HandleResponse()
#    GiveFeedback()
#    WriteResult()

#    if DEBUG:
#        for n in range (20):
#            txt = visual.TextStim( win, text='%01d'%(n*100), pos=(-500, -540+n*100), color=(0.0, 0.0, 0.0), colorSpace='rgb')
#            txt.draw()
            

    event.clearEvents()

#    win.flip() -> moved to nextTrial

    answerCorrect = False

    keys = event.waitKeys()
    if keys[0]=='escape':
        break
    elif keys[0] == 'up':
        if CheckCard( 0, currentRule, currentTgt ):
            answerCorrect = True
            ShowInstruction('RIGHT', 1)
            #frameCard( up )
            rightAnswers += 1
        else:
            ShowInstruction('WROOONG', 1)
    elif keys[0] == 'right':
        if CheckCard( 1, currentRule, currentTgt ):
            answerCorrect = True
            ShowInstruction('RIGHT', 1)
            rightAnswers += 1
        else:
            ShowInstruction('WROOONG', 1)
    elif keys[0] == 'down':
        if CheckCard( 2, currentRule, currentTgt ):
            answerCorrect = True
            ShowInstruction('RIGHT', 1)
            rightAnswers += 1
        else:
            ShowInstruction('WROOONG', 1)
    elif keys[0] == 'left':
        if CheckCard( 3, currentRule, currentTgt ):
            answerCorrect = True
            ShowInstruction('RIGHT', 1)
            rightAnswers += 1
        else:
            ShowInstruction('WROOONG', 1)

    if answerCorrect:
        if currentRule == 'G1':
            triggerAndLog( portCodes['respRight'] | portCodes['rule1'], 'RESP 1 ' + currentRule )
        if currentRule == 'G2':
            triggerAndLog( portCodes['respRight'] | portCodes['rule2'], 'RESP 1 ' + currentRule )
        if currentRule == 'L1':
            triggerAndLog( portCodes['respRight'] | portCodes['rule3'], 'RESP 1 ' + currentRule )
        if currentRule == 'L2':
            triggerAndLog( portCodes['respRight'] | portCodes['rule4'], 'RESP 1 ' + currentRule )
    else:
        if currentRule == 'G1':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule1'], 'RESP 0 ' + currentRule )
        if currentRule == 'G2':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule2'], 'RESP 0 ' + currentRule )
        if currentRule == 'L1':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule3'], 'RESP 0 ' + currentRule )
        if currentRule == 'L2':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule4'], 'RESP 0 ' + currentRule )


    #if enough right answers given, update rule
    logThis( 'repeats: ' + str( rightAnswers ) + '/' + str( ruleRepeats ) )
#    if rightAnswers % ruleList[ruleCount][1] == 0:
    if answerCorrect:
        if rightAnswers % ruleRepeats == 0:
            logThis( 'changing rule from ' + currentRule ) 
            ruleCount += 1
            rightAnswers = 0
            currentRule = rules[ruleList[ruleCount][0]]
            logThis( '...to ' + currentRule ) 

# - CLEANUP -------------------------------------------------------------------------------------

win.close()
core.quit()