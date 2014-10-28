 # -*- coding: utf-8 -*-

"""
WCST experiment / ReKnow

"""
import sys

# -------------------------------------------------------------------------------
# Define if we are in debugging mode
# This affects, e.g., the length of the baseline video
# -------------------------------------------------------------------------------
global DEBUGGING_MODE
DEBUGGING_MODE = False
#DEBUGGING_MODE = True

# -------------------------------------------------------------------------------
# Create LSL outlets
# -------------------------------------------------------------------------------
# Define whether LSL should be used
global USE_LSL;
USE_LSL = True

if USE_LSL:
    sys.path.append('C:\Program Files (x86)\PsychoPy2\Lib\pylsl')
    from pylsl import StreamInfo, StreamOutlet, resolve_streams, StreamInlet, IRREGULAR_RATE, cf_int32
    global lsl_outlet_marker, lsl_outlet_log

    info_lsl_marker = StreamInfo('psychopymarkers', 'Markers', 1, 0, 'float32', 'ppsid001')
    info_lsl_log    = StreamInfo('psychopylog', 'Markers', 1, 0, 'string', 'ppsid002')
    # info = StreamInfo('MyMarkerStream','Markers',1,0,'string','myuidw43536');

    lsl_outlet_marker = StreamOutlet(info_lsl_marker)
    lsl_outlet_log    = StreamOutlet(info_lsl_log)
    # outlet = StreamOutlet(info)
# -------------------------------------------------------------------------------

from random import randint, random, seed
from psychopy import visual, core, monitors, event, gui, logging, sound
from copy import deepcopy
import csv
from datetime import datetime
import json
import NewDlg   # allows setting the length of textfields
import os       # to get path separator for platform independence
import string   # to find test type from pathstrings (noise, patch)

if sys.platform.startswith('win'):
    from ctypes import windll

# - GLOBALS -------------------------------------------------------------------------------------------
global RANDOMIZE_CATEGORY_CARDS
RANDOMIZE_CATEGORY_CARDS = False

global RULE_COUNT
RULE_COUNT = 20 # if read from file, this will be overridden

global SEP_STIM_DURATION
SEP_STIM_DURATION = 20 # number of frames (16ms)

global N_OF_CARDS
N_OF_CARDS = 4 # this is now fixed for each stim folder!

global rules
rules = ['G1', 'G2', 'L1', 'L2'] # face/letter, color, shape/letter, orientation
global portCodes;

global s
s = os.sep

global currentSet, currentBase, currentIns, currentTrial, currentBlock
currentSet   = 0
currentBase  = 1
currentIns   = 1
currentTrial = 0
currentBlock = 1

global paraport
paraport = 0xEC00    # or 0xEC00, 0xE880

global startTime
startTime = datetime.utcnow()

"""
Additive port code scheme allows unique decoding with sparse set. 

'clear'     : 0     triggers the parallel port

'rule1'     : 1    = global 1 rule, FACES or LETTERS
'rule2'     : 2    = global 2 rule, colour
'rule3'     : 3    = local 1 rule, shape or letter
'rule4'     : 4    = local 2 rule, orientation

'segStart' : 8    = marks the start of a segment when combined with [baseline, instr, tlx, set]
'segStop'  : 9    = marks the end of a segment when combined with -"-

'cue'       : 10   = fixation cross before target stimulus
'stimOn'    : 20   = target stimulus is shown
'refsOn'    : 30   = four reference stimuli are shown
'respRight' : 40   = correct response is received
'respWrong' : 50   = wrong response is received
'feedback'  : 60   = red/wrong or green/correct visual feedback to a response
'baseline'  : 70   = baseline start
'instr'     : 80   = marks the display of an instruction
'tlx'       : 90   = marks the display of a questionnaire

'set'       : 100   marks the beginning of a test/practice set
'start'     : 254   marks the start of the experiment
'stop'      : 255   marks the end of the experiment

use: 
    writePort( stimOn + rule1 )      -> 21
    writePort( respRight + rul4 )    -> 44
    writePort( baseline + segStart ) -> 78

"""

portCodes = {'clear'     : 0,
             'rule1'     : 1,
             'rule2'     : 2,
             'rule3'     : 3,
             'rule4'     : 4,
             'segStart'  : 8,
             'segStop'   : 9,
             'cue'       : 10,
             'stimOn'    : 20,
             'refsOn'    : 30,
             'respRight' : 40,
             'respWrong' : 50,
             'feedback'  : 60,
             'base'      : 70,
             'instr'     : 80,
             'tlx'       : 90,
             'set'       : 100,
             'start'     : 254,
             'stop'      : 255}

def ShowInstructionSequence( instrSequence ):
    for item in instrSequence['pages']:
        ShowPicInstruction( unicode(item['text']),int(item['duration']), item['pic'], 1)

def RunSequence( sequence ):
    # setup rules
    global rules
    global currentRule, currentBlock, currentTrial

    # list of tuples containing the sequence of sorting rules (0, 1, 2, 3) and required n of correct repeats per set(5, 6, 7)
    global ruleList; ruleList = []
    for item in sequence['blocks']:
        ruleList.append( (int(item['rule']), int(item['reps'])) )
    # print 'RULELIST:', ruleList
    global RULE_COUNT; RULE_COUNT = len( ruleList )
    global ruleCount, cardCount, rightAnswers;
    ruleCount = 0;

    while ruleCount < RULE_COUNT: 
        currentRule = rules[ruleList[ruleCount][0]]
        SetupTrial()
        NextTrial( taskType )
        answer = GetResponse()

        if answer == 0: #ESC
            rightAnswers = 0
            currentBlock += 1
            currentTrial = 0
            break
        else:
            GiveFeedback( taskType, answer )

        # if enough right answers given, update rule
        if answer > 0:
            if rightAnswers % ruleRepeats == 0: # rightAnswers can't be 0 here since retVal wouldn't be > 0
                ruleCount += 1
                rightAnswers = 0
                currentBlock += 1
                currentTrial = 0

        cardCount +=1


# -------------------------------------------------------------------------------
# Checks the numlock state and automatically set it to ON,
# to make sure that the numpad works correctly in the experiment
#
# Reference: http://win32com.goermezer.de/content/view/136/284/
# -------------------------------------------------------------------------------
def NumLockOn():
    ''' NumLock state: 1 = ON, 0 = OFF '''
    return win32api.GetKeyState(win32con.VK_NUMLOCK)

if sys.platform.startswith('win'):
    import win32api, win32con, win32com.client
    if not NumLockOn():
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("{NUMLOCK}")
# -------------------------------------------------------------------------------
    
def randomizeOrder( lst ):
    return sorted(lst, key=lambda k: random())

def SetupCategoryCards( cards, randomOrder = True ):
    order = [0, 1, 2, 3]

    # should the order of features be randomized?
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
    
    # adjust the feature values for controlled cases
    feat1 = [x*active_rules[0] for x in feat1]
    feat2 = [x*active_rules[1] for x in feat2]
    feat3 = [x*active_rules[2] for x in feat3]
    feat4 = [x*active_rules[3] for x in feat4]
    if DEBUGGING_MODE:
        print str(feat1)
        print str(feat2)
        print str(feat3)
        print str(feat4)

    #fill card parameters
    if len(cards) <> 4:
        if DEBUGGING_MODE:
            print 'setup card count: ' + str(len(cards))
            DebugMsg( 'You have to supply 4 cards for setup' )
        return False
    else:
        for idx in range(4):
            cards[idx]['G1'] = feat1[idx]
            cards[idx]['G2'] = feat2[idx]
            cards[idx]['L1'] = feat3[idx]
            cards[idx]['L2'] = feat4[idx]

            cards[idx]['fn'] = stimPath +'%02d_%02d_%02d_%02d.png' % (feat1[idx], feat2[idx], feat3[idx], feat4[idx])
            if DEBUGGING_MODE:
                print cards[idx]['fn']

    cardstr = ''
    for idx in range(4):
        cardstr += '%01d: %01d,%01d,%01d,%01d | ' % ( idx, feat1[idx], feat2[idx], feat3[idx], feat4[idx])

    return True

def DebugMsg( msg ):
    txt = visual.TextStim( win, text=msg, pos=(150, 480), color=(1.0, 0.0, 0.0), colorSpace='rgb')
    txt.draw()

def SetupTrial():
    global currentRule, currentTrial
    global ruleRepeats
    global tgtCards

    currentRule = rules[ ruleList[ ruleCount ][0] ]
    ruleRepeats = int( ruleList[ruleCount][1] )
    currentTrial += 1

    if DEBUGGING_MODE:
        print 'CURRENTRULE = ' + currentRule

    #get a random set for every round, if wanted
    if RANDOMIZE_CATEGORY_CARDS:
        SetupCategoryCards( tgtCards )
        stimCards[0].setImage( tgtCards[0]['fn'] )
        stimCards[1].setImage( tgtCards[1]['fn'] )
        stimCards[2].setImage( tgtCards[2]['fn'] )
        stimCards[3].setImage( tgtCards[3]['fn'] )

# selects a stim card that matches one of each feature of tgtCards
def GetStimCard( tgtCards ):
        
    match = [0, 1, 2, 3]
    match = randomizeOrder( match )
    
    sc = [ tgtCards[match[0]][rules[0]],
           tgtCards[match[1]][rules[1]],
           tgtCards[match[2]][rules[2]],
           tgtCards[match[3]][rules[3]] ]
           
    return sc

def dict_to_list(d):
    ''' Transform a dictionary into a list. '''
    return [item for sublist in d.values() for item in sublist]

def GetResponse():
    global currentRule, currentTgt, ruleCount, rightAnswers, gameScore

    event.clearEvents()

    retVal = 0 #if not modified, breaks the task
    answerPressed = -1 # which card was selected?

    keylist_response_keys = { 'down': ['down', '2', 'num_2'], 'left': ['left', '4', 'num_4'], 'up': ['up', '8', 'num_8'], 'right': ['right', '6', 'num_6']}
    keylist_special_keys  = ['f10', 'escape']

    keys = event.waitKeys(keyList = (dict_to_list(keylist_response_keys) + keylist_special_keys))

    if keys[0] == 'f10':
        triggerAndLog(portCodes['stop'], "STP", 0, 0, "STOP: aborted by F10")
        win.close()
        core.quit()

    if keys[0] == 'escape':
        retVal = 0

    elif keys[0] in keylist_response_keys['up']:
        if CheckCard( 0, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 1
        else:
            retVal = -1
    elif keys[0] in keylist_response_keys['right']:
        if CheckCard( 1, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 2
        else:
            retVal = -2
    elif keys[0] in keylist_response_keys['down']:
        if CheckCard( 2, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 3
        else:
            retVal = -3
    elif keys[0] in keylist_response_keys['left']:
        if CheckCard( 3, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 4
        else:
            retVal = -4

    idx = str(rules.index(currentRule) + 1)

    if retVal > 0:
        gameScore += 1
        triggerAndLog( portCodes['respRight'] + portCodes['rule'+idx],
        "RSP", currentBlock, currentTrial, 'RESPONSE 1 ' + currentRule + ' ANSWER ' + str(retVal) )
    elif retVal < 0:
        gameScore -= 1
        triggerAndLog( portCodes['respWrong'] + portCodes['rule'+idx],
        "RSP", currentBlock, currentTrial, 'RESPONSE 0 ' + currentRule + ' ANSWER ' + str(retVal) )
    
    return retVal

def GiveFeedback( taskType, fbVal ):

    if fbVal > 0:
        triggerAndLog( portCodes['feedback'],
        "FDB", currentBlock, currentTrial, 'FEEDBACK CORRECT ' + str(rightAnswers) + ' / ' + str(ruleRepeats) );
    else:
        triggerAndLog( portCodes['feedback'],
        "FDB", currentBlock, currentTrial, 'FEEDBACK FAIL ' + str(rightAnswers) + ' / ' + str(ruleRepeats) );
        
    if taskType == 3:
        if fbVal > 0:
            ShowInstruction('RIGHT', 1)
        else:
            ShowInstruction('WRONG', 1)

    elif taskType == 2:
        if fbVal > 0:
            frameCard( (0,0), 'green', 1 )
        else:
            frameCard( (0,0), 'red', 1 )
            
    elif (taskType == 1) | (taskType == 4) | (taskType==5):

        #up
        if fbVal == 1: #up
            frameCard( cardPos[0], 'green', 1)
        elif fbVal == -1:
            frameCard( cardPos[0], 'red', 1 )
        #right
        elif fbVal == 2:
            frameCard( cardPos[1], 'green', 1 )
        elif fbVal == -2:
            frameCard( cardPos[1], 'red', 1 )
        #down
        elif fbVal == 3: 
            frameCard( cardPos[2], 'green', 1 )
        elif fbVal == -3:
            frameCard( cardPos[2], 'red', 1 )
        #left   
        elif fbVal == 4: 
            frameCard( cardPos[3], 'green', 1 )
        elif fbVal == -4:
            frameCard( cardPos[3], 'red', 1 )
            
    
    else:
        ShowInstruction( "Wrong tasktype", 1)

def frameCard( pos, color, duration ):
    if color == 'green':
        col = (0.0, 1.0, 0.0)
    else:
        col = (1.0, 0.2, 0.2)
        
    frame = visual.ShapeStim( win, lineWidth=2.0, lineColor=col, lineColorSpace='rgb',
                         fillColor=None, fillColorSpace='rgb',
                         vertices=((-256, -256), (-256,256), (256,256), (256,-256), (-256,-256)),
                         closeShape=True )

    frame.pos = pos
    #for some odd reason without this the backbuffer is empty while drawing the frame, and then flashes the cards
    win.flip( clearBuffer = False )
    frame.draw(win)
    win.flip( clearBuffer = False )
    core.wait(duration)
    win.flip()

def fixCross(duration):
    fc = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',
                         fillColor=None, fillColorSpace='rgb',
                         vertices=((0, 20), (0, -20), (0,0), (-20,0), (20,0)),
                         closeShape=False )
                         
    fc.pos = (0, 0)
    fc.draw( win )
    win.flip()
    triggerAndLog( portCodes['cue'], "CUE", currentBlock, currentTrial, 'CUE' ) 
    core.wait(duration)

def NextTrial( tasktype ):
    global currentTgt

    currentTgt = GetStimCard( tgtCards )

    if DEBUGGING_MODE:
        print 'stimcard', currentTgt

    fn = stimPath + '%02d_%02d_%02d_%02d.png' % (currentTgt[0], currentTgt[1], currentTgt[2], currentTgt[3])
    # fn = stimPath + '%02d_%02d_%02d_%02d.png' % (deck[currentTgt[0]]*active_rules[0], currentTgt[1], currentTgt[2], currentTgt[3]) 
    tgtCard.setImage( fn )
    idx=str(rules.index(currentRule)+1)

    if DEBUGGING_MODE:
        print 'stim: ' + fn

    if tasktype == 1: # 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        fixCross(0.5)
        
        for i in range( SEP_STIM_DURATION ): # accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'] + portCodes['rule'+idx],
                    "STM", currentBlock, currentTrial, 'STIMULUS ' +
                    str( currentTgt[0] ) +','+ str( currentTgt[1] ) +','+ str( currentTgt[2] ) +','+ str( currentTgt[3] )\
                    + ' RULE ' + currentRule)

        win.flip() #clear

        for c in stimCards:
            c.draw(win)

        win.flip( clearBuffer= False ) # keep the cards in the backbuffer for feedback

        triggerAndLog( portCodes['refsOn'], "TGT", currentBlock, currentTrial, 'TARGET '
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 2: # 22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222

        fixCross( 1 )

        win.clearBuffer()
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'] + portCodes['rule'+idx],
                    "STM", currentBlock, currentTrial, 'STIMULUS' +
                    str( currentTgt[0] ) +','+ str( currentTgt[1] ) +','+ str( currentTgt[2] ) +','+ str( currentTgt[3] )
                    + ' RULE ' + currentRule)

        win.flip() #clear
            
        for c in stimCards:
            c.draw(win)

        win.flip()

        triggerAndLog( portCodes['refsOn'], "TGT", currentBlock, currentTrial, 'TARGET '
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

        #draw stim card to back buffer for feedback -> flip in GiveFeedback, ugly but efficient
        tgtCard.draw(win)

    elif taskType == 3: # 3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

        fixCross( 1 )

        win.clearBuffer()
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'] + portCodes['rule'+idx],
                    "STM", currentBlock, currentTrial, 'STIMULUS' +
                    str( currentTgt[0] ) +','+ str( currentTgt[1] ) +','+ str( currentTgt[2] ) +','+ str( currentTgt[3] )
                    + ' RULE ' + currentRule )

        win.flip() #clear
            
        for c in stimCards:
            c.draw(win)

        win.flip()

        triggerAndLog( portCodes['refsOn'], "TGT", currentBlock, currentTrial, 'TARGET '
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 4: # 4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444

        tgtCard.draw(win)

        for c in stimCards:
            c.draw(win)

        win.flip( ) # keep the cards in the backbuffer for feedback

    # TODO concurrent presentation not compatible with logging scheme?
        triggerAndLog( portCodes['stimOn'] + portCodes['rule'+idx], "STM", currentBlock, currentTrial, 'STIMULUS AS TARGET' )

        triggerAndLog( portCodes['refsOn'], "TGT", currentBlock, currentTrial, 'TARGET '
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 5: # 5555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555
        
        global lastScore
        
        if gameScore-lastScore > 0:
            ShowInstruction( gameScore, 1, (0.0, 1.0, 0.0) )
        else:
            ShowInstruction( gameScore, 1, (1.0, 0.0, 0.0) )
            
        lastScore = gameScore
        
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'] + portCodes['rule'+idx],
                    "STM", currentBlock, currentTrial, 'STIMULUS' +
                    str( currentTgt[0] ) +','+ str( currentTgt[1] ) +','+ str( currentTgt[2] ) +','+ str( currentTgt[3] )
                    + ' RULE ' + currentRule )

        win.flip() #clear

        for c in stimCards:
            c.draw(win)

        win.flip( clearBuffer= False ) # keep the cards in the backbuffer for feedback

        triggerAndLog( portCodes['refsOn'], "TGT", currentBlock, currentTrial, 'TARGET '
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    else: 
        ShowInstruction("Wrong Task Type (NextTrial)", 1)

def logThis( msg ):
    ''' Write to log file and to LSL outlet. '''
    global lsl_outlet_log
    global USE_LSL

    logging.log(msg, level = myLogLevel)

    if USE_LSL:
        lsl_outlet_log.push_sample([msg])

def triggerAndLog( trigCode, id_str, major_inc, minor_inc, payload, trigDuration=10 ):
    ''' Parallel port code, LSL and test logging. '''

    global paraport
    global lsl_outlet_marker
    global USE_LSL
    global startTime

    id_str    = str(id_str)
    major_inc = "{:02d}".format(major_inc)
    minor_inc = "{:02d}".format(minor_inc)
    payload   = string.replace( payload, '\t', '_' )
    outstr    = u'\t'.join([str((datetime.utcnow() - startTime).total_seconds()), str(trigCode), id_str, major_inc, minor_inc, payload]) 
    # outstr  = str( (datetime.utcnow() - startTime).total_seconds() ) + '\t' + str(trigCode) + '\t' + id_str + '\t' + major_inc + '\t' + minor_inc + '\t' + payload

    # Write string to log and also send to LSL outlet
    logThis(outstr)

    if triggers:
        windll.inpout32.Out32(paraport, trigCode)
        core.wait( trigDuration/1000.0, hogCPUperiod = trigDuration/1000.0 ) # <-- add this for parallel triggering
        windll.inpout32.Out32(paraport, portCodes['clear'] ) # <-- add this for parallel triggering

    if USE_LSL:
        lsl_outlet_marker.push_sample([trigCode])


def ShowInstruction( txt, duration, col=(0.0, 0.0, 0.0) ):
    instr = visual.TextStim( win, text=txt, pos=(0,0), color=col, colorSpace='rgb', height=50 )
    instr.draw(win)
    win.flip()
    if duration < 0:
        event.waitKeys()
    else:
        core.wait( duration )

    win.flip() # clear screen
    
def ShowPicInstruction( txt, duration, picFile, location, col=(0.0, 0.0, 0.0) ):
    global currentBase

    hasPic = False; hasTxt = False; logTxt=False
    h = 0;

    if txt != "":
        hasTxt=True
        logTxt=True
        if txt[0]=='*': # 'text' field in a NasaTLX instruction should start with asterix
            symbol='*'
        elif txt[0]=='+': # 'text' field in a baseline instruction should start with plus
            symbol='+'
            hasTxt=False
        else:
            logTxt=False
        if logTxt:
            offset=txt.find(symbol,1)
            txt_to_log=txt[1:offset]
            txt=string.replace(txt, symbol, '')
        instr = visual.TextStim( win, text=txt, pos=(0,-50), color=col, colorSpace='rgb', height=25, wrapWidth=800, alignHoriz='center')

    if picFile != "":
        picFile = string.replace( picFile, '\\', s )
        hasPic = True
        pic = visual.ImageStim( win );
        pic.setImage( picFile );
        h = pic.size

    if hasTxt:
        if hasPic:
            textpos = ( 0, -1* instr.height/2 - 80)
            picpos = ( 0, h[1]/2 + 20 )
        else:
            textpos = ( 0, 0 )
            picpos = ( -2000, -2000 )
    else:
        picpos = (0, 0)
        textpos = ( -2000, -2000 )

    if hasPic:
        pic.setPos( picpos );
        pic.draw( win );

    if hasTxt:
        instr.setPos( textpos )
        instr.draw(win)

    win.flip()

    if not(logTxt):
        if hasTxt:
            triggerAndLog(portCodes['instr'], "ITX", currentIns, 0, 'INSTRUCTION: ' + txt[0:12] )
        elif hasPic:
            triggerAndLog(portCodes['instr'], "IPC", currentIns, 0, 'INSTRUCTION: ' + picFile )

    if duration < 0:
        if logTxt and symbol=='*':
            keys_tmp =  [str(i) for i in range(1, 10)] + ['num_' + str(i) for i in range(1,10)]
            keys = event.waitKeys(keyList = keys_tmp)
            resp = str(keys[0]).replace('num_', '')
            triggerAndLog(portCodes['tlx'], "TLX", currentSet, 0, txt_to_log + ': ' + resp)
        else:
            keys_tmp = ['5', 'num_5']
            keys = event.waitKeys( keyList = keys_tmp )
            #event.waitKeys()
    else:
        if logTxt and symbol=='+':
            triggerAndLog(portCodes['base'], "BAS", currentBase, 0, txt_to_log )
            currentBase += 1
        core.wait( duration )

    win.flip() # clear screen
    
def CheckCard( stimNum, currentRule, currentTgt ):
    cardOK = False

    if currentRule == 'G1':
        if tgtCards[stimNum]['G1'] == currentTgt[0]:
            cardOK = True
    elif currentRule == 'G2':
        if tgtCards[stimNum]['G2'] == currentTgt[1]:
            cardOK = True
    elif currentRule == 'L1':
        if tgtCards[stimNum]['L1'] == currentTgt[2]:
            cardOK = True
    elif currentRule == 'L2':
        if tgtCards[stimNum]['L2'] == currentTgt[3]:
            cardOK = True
        
    if cardOK:
        return True
    else:
        return False

# -------------------------------------------------------------------------------------------------#
# - MAIN PROG -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------#

#init random seed
seed(42)

# Gather info / dialog
myDlg = NewDlg.NewDlg(title="The amazing ReKnow card test")

myDlg.addText('Subject info')
# confInfo 0
myDlg.addField('SubjID:', width=30)
# confInfo 1
myDlg.addField('Age:', 18)
# confInfo 2
myDlg.addField('Group:', choices=["Test", "Control"])

myDlg.addText('TEST info')
# confInfo 3
myDlg.addField('IMPORTANT!! Match to SUBJECT NUMBER:',
    choices=['wcst_conf1', 'wcst_conf2', 'wcst_conf3', 'wcst_conf4',
             'wcst_conf5', 'wcst_conf6', 'wcst_conf7', 'wcst_conf8',
             'wcst_conf9', 'wcst_conf10','wcst_conf11','wcst_conf12',
             'wcst_conf13','wcst_conf14','wcst_conf15','wcst_conf16',
             'wcst_conf17','wcst_conf18','wcst_conf19','wcst_conf20',
             'wcst_conf21','wcst_conf22','wcst_conf23','wcst_conf24',
             'wcst_conf25','wcst_conf26','wcst_conf27','wcst_conf28',
             'wcst_conf29','wcst_conf30','wcst_conf31','wcst_conf32',
             'config_base', 'test_set_no_practice_no_baseline', 'onlyinstructionstest'], width = 30);
# confInfo 4
if sys.platform.startswith('win'):
    myDlg.addField('Send Triggers?', choices=["True", "False"])
else:
    myDlg.addField('No Windows detected: Trigger status ', choices=["False"])
# confInfo 5
myDlg.addField('Start video:', "D:/Experiments/video/habit_video_01_wcst.avi", width=50)

# Remaining options
#myDlg.addField('Randomize Category Cards:', choices=["No", "Yes"])
#myDlg.addField('Select presentation mode', choices=["1 :: Sequential, Feedback: framed target", \
#                                                     "2 :: Sequential, Feedback: stimcard",\
#                                                     "3 :: Sequential, Feedback: R/W",\
#                                                     "4 :: Concurrent",\
#                                                     "5 :: Gamify"\
#                                                     ])
#myDlg.addField('Show Instructions?', choices=["No", "Yes"])
#myDlg.addField('Choose monitor', choices=["1", "2"])

myDlg.show()  # show dialog and wait for OK or Cancel

if myDlg.OK:  # then the user pressed OK
    confInfo = myDlg.data
    if DEBUGGING_MODE:
        print confInfo
else:
    if DEBUGGING_MODE:
        print 'user cancelled'
    core.quit()

# SETUP LOGGING & CLOCKING
testClock = core.Clock()
logging.setDefaultClock( testClock )

myLogLevel = logging.CRITICAL + 1
logging.addLevel( myLogLevel, '' )
myLog = logging.LogFile( '.'+s+'logs'+s+''+confInfo[0] +'.log', filemode='w', level=myLogLevel, encoding='utf8')

logThis('Subj ID: ' + confInfo[0] )
logThis('Run: ' + str(datetime.utcnow()) )
logThis('Age: ' + str(confInfo[1]) )
logThis('Group: ' + confInfo[2])
logThis('Config: ' + confInfo[3])

logThis('--------------------------------------------------------')
logThis('INFO')
logThis('timestamp1 CUE [block] [trial] CUE')
logThis('timestamp1 STM [block] [trial] STIMULUS[state for each rule G1 G2 L1 L2 : 0,1,2,3]RULE[current rule]')
logThis('timestamp1 TGT [block] [trial] TARGET[states for each card / Up, Right, Down, Left: 0,1,2,3; 0,1,2,3;...]') 
logThis('timestamp1 RSP [block] [trial] RESPONSE[correct: 1/0][current rule: G1, G2, L1, L2]ANSWER[card selected: 1(up), 2(right), 3(down), 4(left)]')
logThis('timestamp1 FDB [block] [trial] FEEDBACK[correct/fail][correct answers]/[series length]')
logThis('--------------------------------------------------------')

# SETUP TEST PARAMS
#if confInfo[5] == 'No':
#    RANDOMIZE_CATEGORY_CARDS = False
#else:
#    RANDOMIZE_CATEGORY_CARDS = True

#rendering window setup
mntrs=[]
monW=[]
monH=[]
# Lab monitor
mntrs.append( monitors.Monitor('labTTL', width=37.8, distance=80) ); monW.append(1920); monH.append(1080)
# OIH experimenter's screen
#mntrs.append( monitors.Monitor('OIH1', width=37.8, distance=50) ); monW.append(1680); monH.append(1050)
# OIH eye tracking screen
#mntrs.append( monitors.Monitor('OIH2', width=37.8, distance=50) ); monW.append(1680); monH.append(1050)
#HP Elitebook 2560p
#mntrs.append( monitors.Monitor('Ben1', width=31.5, distance=40) ); monW.append(1366); monH.append(768)
#mntrs.append( monitors.Monitor('Ben2', width=31.5, distance=40) ); monW.append(1080); monH.append(1920)
#Dynamite Mac
#mntrs.append( monitors.Monitor('DynMac', width=50, distance=90) ); monW.append(1920); monH.append(1200)
# kride laptop
#mntrs.append( monitors.Monitor('yoga', width=29.3, distance=40) ); monW.append(3200); monH.append(1800)
# kride desktop 1
#mntrs.append( monitors.Monitor('dell', width=37.8, distance=50) ); monW.append(1920); monH.append(1200)
# kride desktop 2
#mntrs.append( monitors.Monitor('dell', width=37.8, distance=50) ); monW.append(1920); monH.append(1080)
midx=0
myMon = mntrs[midx]
myMon.setSizePix((monW[midx], monH[midx]))
win = visual.Window(winType ='pyglet', size = (monW[midx], monH[midx]), units = 'pix', fullscr = True, monitor = myMon, screen = 1, rgb = (1,1,1), allowGUI=False)
global cardPos; cardPos = []

# TARGET CARD POSITIONS
taskType = 1
#552 = 2*256 + 40
# cards in clockwise order: up, right, down, left
if taskType == 4: #concurrent presentation -> different format
    cardPos.append( (0, 522) )
    cardPos.append( (522, 0) )
    cardPos.append( (0, -522) )
    cardPos.append( (-522, 0) )

else: # sequential -> tight format
    cardPos.append( (0, 266) )
    cardPos.append( (522, 0) )
    cardPos.append( (0, -266) )
    cardPos.append( (-522, 0) )

# -------------------------------------------------------------------------------------------------#
# - BEGIN PROG ------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------#
global cardCount 
global rightAnswers
global ruleCount 

global gameScore  #for the gamify mode
global lastScore
global triggers; triggers=(confInfo[4]=='True') # flag as True when actually recording 

#SETUP CARDS 
cardPrototype = {'G1':0, 'G2':0, 'L1':0, 'L2':0, 'fn':''}

#setup deck of four cards from the whole deck
#deck = SelectCardSubset( 4, N_OF_CARDS )

global currentTgt; currentTgt = (-1, -1, -1, -1)

#TODO: ADD ERROR CHECKING! Here we trust the json files to be correctly formed and valid
confFile = open( '.'+s+'configs'+s+confInfo[3]+'.json' )
config = json.loads( confFile.read() )
confFile.close()
logging.flush()

gameScore = 0
lastScore = 0

triggerAndLog(portCodes['start'], "STR", 0, 0, "START: " + str( startTime ) )

win.setMouseVisible( False )

# - BASELINE VIDEO ------------------------------------------------------------------------------#
movie_filename = confInfo[5]
movie_baseline = visual.MovieStim(win = win, filename = movie_filename, pos = [0,0], size = (1350,1080))
if DEBUGGING_MODE:
    for i in range(25 * 3):
        movie_baseline.draw()
        win.flip()
else:
    while movie_baseline.status != visual.FINISHED:
        movie_baseline.draw()
        win.flip()

triggerAndLog(portCodes['stop'], "STP", 0, 0, "STOP: baseline video")
triggerAndLog(portCodes['start'], "STR", 1, 0, "START: testing" )

# - BEGIN RUNNING CONFIG ------------------------------------------------------------------------#
import codecs

for item in config['sets']:
    if( item['type'] == 'instruction'):
        temp=string.replace( item['file'], '\\', s )
        instrFile = codecs.open( temp, 'r', 'utf-8' )
        instrSequence = json.loads( instrFile.read() )
        instrFile.close()
        triggerAndLog(portCodes['instr'] + portCodes['segStart'], "INS", currentIns, 0, "START Instruction")
        ShowInstructionSequence( instrSequence )
        triggerAndLog(portCodes['instr'] + portCodes['segStop'], "INS", currentIns, 0, "STOP Instruction")
        currentIns += 1
        
    elif item['type'] == 'set':
        temp=string.replace( item['file'], '\\', s )
        seqFile = open( temp )
        setSequence = json.loads( seqFile.read() )
        seqFile.close()
        currentSet += 1

        #run test type based on confInfo
        global stimPath; stimPath = setSequence['set']['stimpath']
        stimPath=string.replace( stimPath, '\\', s )

        # RESTRICT CARD SETS FOR REDUCED FEATURE SETS ---------------------------------
        active_rules = [1,1,1,1]
        if string.find(stimPath, 'noise') != -1:
            active_rules = [0,0,1,1]
        elif string.find(stimPath, 'patch') != -1:
            active_rules = [1,1,0,0]

        tgtCards = (deepcopy(cardPrototype), 
                    deepcopy(cardPrototype), 
                    deepcopy(cardPrototype), 
                    deepcopy(cardPrototype) )

        SetupCategoryCards( tgtCards )
           
        stimCards = ( visual.ImageStim( win, pos=cardPos[0] ), 
                      visual.ImageStim( win, pos=cardPos[1] ), 
                      visual.ImageStim( win, pos=cardPos[2] ), 
                      visual.ImageStim( win, pos=cardPos[3] ) )

        stimCards[0].setImage( tgtCards[0]['fn'] )
        stimCards[1].setImage( tgtCards[1]['fn'] )
        stimCards[2].setImage( tgtCards[2]['fn'] )
        stimCards[3].setImage( tgtCards[3]['fn'] )

        tgtCard = visual.ImageStim( win, pos=( 0, 0 ) )

        cardCount = 0
        rightAnswers = 0
        ruleCount=0

        triggerAndLog(portCodes['instr'] + portCodes['segStart'], "INS", currentIns, 0, "START Instruction")
        ShowPicInstruction( u'Aloita painamalla keskimmäistä 5-näppäintä', -1, "", 1 )
        triggerAndLog(portCodes['instr'] + portCodes['segStop'], "INS", currentIns, 0, "STOP Instruction")
        triggerAndLog( portCodes['set']+portCodes['segStart'], "SET", currentSet, 0, 'START set %s' % (item['file']) )
        RunSequence( setSequence['set'] )
        triggerAndLog( portCodes['set']+portCodes['segStop'], "SET", currentSet, 0, 'STOP set %s' % (item['file']) )

    else:
        if DEBUGGING_MODE:
            print 'unidentified item type in config: ' + item['type']

    logging.flush() # flush log when set has been run

triggerAndLog(portCodes['stop'], "STP", 1, 0, "STOP: tests completed")
endtone=sound.Sound(u'A', secs=1.0)
endtone.play()
# - CLEANUP -------------------------------------------------------------------------------------
win.close()
core.quit()