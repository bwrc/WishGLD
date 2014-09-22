 # -*- coding: utf-8 -*-

"""
WCST experiment / ReKnow

"""
from random import randint, random, seed
from psychopy import visual,core,monitors,event,gui, logging#, parallel
from copy import deepcopy
import csv
from datetime import datetime
import json
import NewDlg   # allows setting the length of textfields
import os       # to get path separator for platform independence
import string   # to find test type from pathstrings (noise, patch)
import sys
if sys.platform.startswith('win'):
    from ctypes import windll

# - GLOBALS -------------------------------------------------------------------------------------------
global DEBUG; DEBUG = False
global RANDOMIZE_CATEGORY_CARDS; RANDOMIZE_CATEGORY_CARDS = False
global RULE_COUNT; RULE_COUNT = 20 #if read from file, this will be overridden
global SEP_STIM_DURATION; SEP_STIM_DURATION = 20 #n of frames (16ms)
global N_OF_CARDS; N_OF_CARDS = 4 #this is now fixed for each stim folder!
global rules; rules = ['G1', 'G2', 'L1', 'L2'] # face/letter, color, shape/letter, orientation
global portCodes;
global s; s=os.sep
global currentSet, currentTrial, currentBlock; currentSet = 0; currentTrial = 0; currentBlock = 1;

"""
Additive port code scheme allows unique decoding with sparse set. Avoids any number ending in #F, 
as that will be used to trigger the eye tracker on the four bit parallel.

'clear'     : 0
'rule1'     : 1
'rule2'     : 2
'rule3'     : 3
'rule4'     : 4
'start'     : 10
'stop'      : 20
'cue'       : 30
'feedback'  : 40
'stimOn'    : 50
'refsOn'    : 15
'respRight' : 100
'respWrong' : 110

use: 
    writePort( stimOn | rule1 ) -> 66 
    writePort( respRight | rule1 ) -> 116
    writePort( respWrong | rule2 ) #where rule2 would be impossible to deduce, since we don't know what the user meant?

"""
portCodes = {'clear' : 0x00,\
             'rule1' : 0x10,\
             'rule2' : 0x20,\
             'rule3' : 0x30,\
             'rule4' : 0x40,\
             'cue'   : 0x1e,\
             'feedback'   : 0x28,\
             'stimOn'   : 0x32,\
             'refsOn' : 0x0f,\
             'respRight' : 0x64,\
             'respWrong' : 0x6e,\
             'start': 0x0a,\
             'stop': 0x14}

def ShowInstructionSequence( instrSequence ):
    for item in instrSequence['pages']:
        ShowPicInstruction( unicode(item['text']),int(item['duration']), item['pic'], 1)

def RunSequence( sequence ):
    #setup rules
    global rules
    global currentRule, currentBlock, currentTrial
    # list of tuples containing the sequence of sorting rules (0, 1, 2, 3) and required n of correct repeats per set(5, 6, 7)
    global ruleList; ruleList = []
    for item in sequence['blocks']:
        ruleList.append( (int(item['rule']), int(item['reps'])) )
    print 'RULELIST:', ruleList
    global RULE_COUNT; RULE_COUNT = len( ruleList )
    global ruleCount, cardCount, rightAnswers;
    ruleCount = 0;

    ShowPicInstruction( u'Aloita painamalla jotain näppäintä.\n\nPress any key to start.', -1, "", 1 )

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

        #if enough right answers given, update rule
        if answer > 0:
            if rightAnswers % ruleRepeats == 0: # rightAnswers can't be 0 here since retVal wouldn't be > 0
                ruleCount += 1
                rightAnswers = 0
                currentBlock += 1
                currentTrial = 0

        cardCount +=1

#    logging.flush() # flush log when set has been run - don't want flush to cause display pause!

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
    if DEBUG:
        print str(feat1)
        print str(feat2)
        print str(feat3)
        print str(feat4)

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

            cards[idx]['fn'] = stimPath +'%02d_%02d_%02d_%02d.png' % (feat1[idx], feat2[idx], feat3[idx], feat4[idx])
#            cards[idx]['fn'] = stimPath +'%02d_%02d_%02d_%02d.png' % (deck[feat1[idx]]*active_rules[0], feat2[idx], feat3[idx], feat4[idx])
            if DEBUG:
                print cards[idx]['fn']

    cardstr = ''
    for idx in range(4):
        cardstr += '%01d: %01d,%01d,%01d,%01d | ' % ( idx, feat1[idx], feat2[idx], feat3[idx], feat4[idx])
#        cardstr += '%01d: %01d,%01d,%01d,%01d | ' % ( idx, deck[feat1[idx]]*active_rules[0], feat2[idx], feat3[idx], feat4[idx]) 
#    logThis( 'Using deck: ' + cardstr[0:len(cardstr)-2] );

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

    if DEBUG:
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
    
    sc = [ tgtCards[match[0]][rules[0]],\
           tgtCards[match[1]][rules[1]],\
           tgtCards[match[2]][rules[2]],\
           tgtCards[match[3]][rules[3]] ]
           
    return sc

def GetResponse():
    global currentRule, currentTgt, ruleCount, rightAnswers, gameScore

    event.clearEvents()

    retVal = 0 #if not modified, breaks the task
    answerPressed = -1 # which card was selected?

    keys = event.waitKeys(keyList=['f10', 'escape', 'up', 'right', 'down', 'left'])

    if keys[0] == 'f10':
        logThis('PANIC BUTTON -> OUT')
        win.close()
        core.quit()
    elif keys[0] == 'escape':
        retVal = 0
    elif keys[0] == 'up':
        if CheckCard( 0, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 1
        else:
            retVal = -1
    elif keys[0] == 'right':
        if CheckCard( 1, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 2
        else:
            retVal = -2
    elif keys[0] == 'down':
        if CheckCard( 2, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 3
        else:
            retVal = -3
    elif keys[0] == 'left':
        if CheckCard( 3, currentRule, currentTgt ):
            rightAnswers += 1
            retVal = 4
        else:
            retVal = -4
            
    if retVal > 0:
        gameScore += 1
        if currentRule == 'G1':
           triggerAndLog( portCodes['respRight'] | portCodes['rule1'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
           + '_RSP 1 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'G2':
            triggerAndLog( portCodes['respRight'] | portCodes['rule2'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
            + '_RSP 1 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L1':
            triggerAndLog( portCodes['respRight'] | portCodes['rule3'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
            + '_RSP 1 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L2':
            triggerAndLog( portCodes['respRight'] | portCodes['rule4'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
            + '_RSP 1 ' + currentRule + ' ANSWER ' + str(retVal) )
    elif retVal < 0:
        gameScore -= 1
        if currentRule == 'G1':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule1'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
            + '_RSP 0 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'G2':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule2'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
            + '_RSP 0 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L1':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule3'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
            + '_RSP 0 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L2':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule4'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
            + '_RSP 0 ' + currentRule + ' ANSWER ' + str(retVal) )
    
    return retVal

def GiveFeedback( taskType, fbVal ):

    if fbVal > 0:
        triggerAndLog( portCodes['feedback'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
                                + '_FDB CORRECT ' + str(rightAnswers) + ' of ' + str(ruleRepeats) );
    else:
        triggerAndLog( portCodes['feedback'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
                                + '_FDB FAIL ' + str(rightAnswers) + ' of ' + str(ruleRepeats) );
        
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
        
    frame = visual.ShapeStim( win, lineWidth=2.0, lineColor=col, lineColorSpace='rgb',\
                         fillColor=None, fillColorSpace='rgb',\
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
    fc = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=None, fillColorSpace='rgb',\
                         vertices=((0, 20), (0, -20), (0,0), (-20,0), (20,0)),
                         closeShape=False )
                         
    fc.pos = (0, 0)
    fc.draw( win )
    win.flip()
    triggerAndLog( portCodes['cue'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial) + '_CUE' ) 
    core.wait(duration)

def NextTrial( tasktype ):
    global currentTgt
    global currentRule

    currentTgt = GetStimCard( tgtCards )

    if DEBUG:
        print 'stimcard', currentTgt

    fn = stimPath + '%02d_%02d_%02d_%02d.png' % (currentTgt[0], currentTgt[1], currentTgt[2], currentTgt[3])
#    fn = stimPath + '%02d_%02d_%02d_%02d.png' % (deck[currentTgt[0]]*active_rules[0], currentTgt[1], currentTgt[2], currentTgt[3]) 
    tgtCard.setImage( fn )

    if DEBUG:
        print 'stim: ' + fn

    if tasktype == 1: # 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        fixCross(0.5)
        
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
                    + '_STM ' + str( currentTgt[0] ) + ',' + str( currentTgt[1] ) + ',' +str( currentTgt[2] ) + ','\
                    + str( currentTgt[3] ) + ' RULE ' + currentRule)

        win.flip() #clear

        for c in stimCards:
            c.draw(win)

        win.flip( clearBuffer= False ) # keep the cards in the backbuffer for feedback

        triggerAndLog( portCodes['refsOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial) + '_TGT '\
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 2: # 22222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222

        fixCross( 1 )

        win.clearBuffer()
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
                    + '_STM ' + str( currentTgt[0] ) + ',' + str( currentTgt[1] ) + ',' +str( currentTgt[2] ) + ','\
                    + str( currentTgt[3] ) + ' RULE ' + currentRule)

        win.flip() #clear
            
        for c in stimCards:
            c.draw(win)

        win.flip()

        triggerAndLog( portCodes['refsOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial) + '_TGT '\
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
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
                triggerAndLog( portCodes['stimOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
                    + '_STM ' + str( currentTgt[0] ) + ',' + str( currentTgt[1] ) + ',' +str( currentTgt[2] ) + ','\
                    + str( currentTgt[3] ) + ' RULE ' + currentRule )

        win.flip() #clear
            
        for c in stimCards:
            c.draw(win)

        win.flip()

        triggerAndLog( portCodes['refsOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial) + '_TGT '\
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 4: # 4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444

        tgtCard.draw(win)

        for c in stimCards:
            c.draw(win)

        win.flip( ) # keep the cards in the backbuffer for feedback

    # TODO concurrent presentation not compatible with logging scheme?
        triggerAndLog( portCodes['stimOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial) + '_TGT '\
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
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
                triggerAndLog( portCodes['stimOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial)\
                    + '_STM ' + str( currentTgt[0] ) + ',' + str( currentTgt[1] ) + ',' +str( currentTgt[2] ) + ','\
                    + str( currentTgt[3] ) + ' RULE ' + currentRule )

        win.flip() #clear

        for c in stimCards:
            c.draw(win)

        win.flip( clearBuffer= False ) # keep the cards in the backbuffer for feedback

        triggerAndLog( portCodes['refsOn'], "{:02d}".format(currentBlock) + '.' + "{:02d}".format(currentTrial) + '_TGT '\
            + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
            + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
            + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
            + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    else: 
        ShowInstruction("Wrong Task Type (NextTrial)", 1)

def logThis( msg ):
    logging.log( msg, level=myLogLevel )

# parallel stuff has been replaced with Marco's solution!
def triggerAndLog( trigCode, msg, trigDuration=10 ):
    logThis( msg )
    if triggers:
        windll.inpout32.Out32(0x378,trigCode)
        core.wait( trigDuration/1000.0, hogCPUperiod = trigDuration/1000.0 ) #<-- add this for parallel triggering
        windll.inpout32.Out32(0x378, portCodes['clear'] ) #<-- add this for parallel triggering

def ShowInstruction( txt, duration, col=(0.0, 0.0, 0.0) ):
    instr = visual.TextStim( win, text=txt, pos=(0,0), color=col, colorSpace='rgb', height=50 )
    instr.draw(win)
    win.flip()
    if duration < 0:
        event.waitKeys()
    else:
        core.wait( duration )

    win.flip() #clear screen
    
def ShowPicInstruction( txt, duration, picFile, location, col=(0.0, 0.0, 0.0) ):

    hasPic = False; hasTxt = False; logTxt=False
    h = 0;

    if txt != "":
        hasTxt = True
        if txt[0]=='*':
            logTxt=True
            offset=txt.find('*',1)
            txt_to_log=txt[1:offset]+': '
            txt=string.replace(txt, '*', '')
        instr = visual.TextStim( win, text=txt, pos=(0,-50), color=col, colorSpace='rgb', height=25, wrapWidth=800, alignHoriz='center')

    if picFile != "":
        picFile = string.replace( picFile, '\\', s )
        hasPic = True
        pic = visual.ImageStim( win );
        pic.setImage( picFile );
        h = pic.size

    if hasTxt:
        if hasPic:
            textpos = ( 0, -1* instr.height/2 - 10)
            picpos = ( 0, h[1]/2 + 20 )
        else:
            textpos = ( 0, 0 )
            picpos = ( -2000, -2000 )
    else:
        picpos = (0, 0)
        textpos = ( -2000, -2000 )

#    picpos = ( 0, h[1]/2 + 20 )
#    textpos = ( 0, -1* instr.height/2 - 10)

    if hasPic:
        pic.setPos( picpos );
        pic.draw( win );

    if hasTxt:
        instr.setPos( textpos )
        instr.draw(win)

    win.flip()
    if duration < 0:
        if logTxt:
            keys = event.waitKeys(keyList=['1', '2', '3', '4', '5', '6', '7', '8', '9'])
            logThis("{:02d}".format(currentSet) + '.0_' + txt_to_log + str(keys[0]))
        else:
            event.waitKeys()
    else:
        core.wait( duration )

    win.flip() #clear screen
    
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
seed()

# Gather info / dialog
myDlg = NewDlg.NewDlg(title="The amazing ReKnow card test")

myDlg.addText('Subject info')
# confInfo 0
myDlg.addField('SubjID:', width=30)
# confInfo 1
myDlg.addField('Age:', 18)

myDlg.addText('Experiment Info')
# confInfo 2
myDlg.addField('Randomize Category Cards:', choices=["No", "Yes"])
# confInfo 3
myDlg.addField('Select presentation mode', choices=["1 :: Sequential, Feedback: framed target", \
                                                     "2 :: Sequential, Feedback: stimcard",\
                                                     "3 :: Sequential, Feedback: R/W",\
                                                     "4 :: Concurrent",\
                                                     "5 :: Gamify"\
                                                     ])
# confInfo 4
myDlg.addField('Group:', choices=["Test", "Control"])
# confInfo 5
myDlg.addField('Show Instructions?', choices=["No", "Yes"])
myDlg.addText('IMPORTANT!! DOUBLE CHECK!')
# confInfo 6
myDlg.addField('Config File:', choices=['sep_latin1', 'sep_latin2', 'sep_latin3', 'sep_latin4',\
                                        'sep_latin5', 'sep_latin6', 'sep_latin7', 'sep_latin8',\
                                        'config_base'], width=30);
# confInfo 7
myDlg.addField('Choose monitor', choices=["1", "2"])
if sys.platform.startswith('win'):
    myDlg.addField('Send Triggers?', choices=["True", "False"])
else:
    myDlg.addField('No Windows detected: Trigger status ', choices=["False"])

myDlg.show()  # show dialog and wait for OK or Cancel

if myDlg.OK:  # then the user pressed OK
    confInfo = myDlg.data
    print confInfo
else:
    print 'user cancelled'
    core.quit()

# SETUP LOGGING & CLOCKING
testClock = core.Clock()
logging.setDefaultClock( testClock )

myLogLevel = logging.CRITICAL + 1
logging.addLevel( myLogLevel, '' )
myLog = logging.LogFile( '.'+s+'logs'+s+'' + confInfo[0] + '.log', filemode='w', level = myLogLevel, encoding='utf8') #= myLogLevel )

logThis('Subj ID: ' + confInfo[0] )
logThis('Run: ' + str(datetime.utcnow()) )
logThis('Age: ' + str(confInfo[1]) )

if confInfo[4] == 0:
    logThis('Group: Test')
else:
    logThis('Group: Control')

logThis('--------------------------------------------------------')
logThis('INFO')
logThis('timestamp [block].[trial]_CUE')
logThis('timestamp [block].[trial]_STM [state for each rule G1 G2 L1 L2 : 0,1,2,3] RULE [current rule]')
logThis('timestamp [block].[trial]_TGT [states for each card / Up, Right, Down, Left: 0,1,2,3; 0,1,2,3;...]') 
logThis('timestamp [block].[trial]_RSP [correct: 1/0] [current rule: G1, G2, L1, L2] ANSWER [card selected: 1(up), 2(right), 3(down), 4(left)]')
logThis('timestamp [block].[trial]_FDB [correct/fail] [correct answers] of [series length]')
logThis('--------------------------------------------------------')

# SETUP TEST PARAMS
if confInfo[2] == 'No':
    RANDOMIZE_CATEGORY_CARDS = False
else:
    RANDOMIZE_CATEGORY_CARDS = True

#rendering window setup
mntrs=[]
monW=[]
monH=[]
# OIH experimenter's screen
mntrs.append( monitors.Monitor('OIH1', width=37.8, distance=50) ); monW.append(1680); monH.append(1050)
# OIH eye tracking screen
mntrs.append( monitors.Monitor('OIH2', width=37.8, distance=50) ); monW.append(1680); monH.append(1050)
#HP Elitebook 2560p
mntrs.append( monitors.Monitor('Ben1', width=31.5, distance=40) ); monW.append(1366); monH.append(768)
mntrs.append( monitors.Monitor('Ben2', width=31.5, distance=40) ); monW.append(1080); monH.append(1920)
#Dynamite Mac
mntrs.append( monitors.Monitor('DynMac', width=50, distance=90) ); monW.append(1920); monH.append(1200)
#DELL Latitude
mntrs.append( monitors.Monitor('bTTL', width=31.5, distance=40) ); monW.append(1600); monH.append(900)
# kride laptop
mntrs.append( monitors.Monitor('yoga', width=29.3, distance=40) ); monW.append(3200); monH.append(1800)
# kride desktop 1
mntrs.append( monitors.Monitor('dell', width=37.8, distance=50) ); monW.append(1920); monH.append(1200)
# kride desktop 2
mntrs.append( monitors.Monitor('dell', width=37.8, distance=50) ); monW.append(1920); monH.append(1080)
midx=4
myMon=mntrs[midx]
myMon.setSizePix((monW[midx], monH[midx]))
win=visual.Window(winType='pyglet', size=(monW[midx], monH[midx]), units='pix', fullscr=True, monitor=myMon,\
                screen=int(confInfo[7]), rgb=(1,1,1))
taskType = int( confInfo[3][0] ) # 1, 2, 3, ...
global cardPos; cardPos = []

# TARGET CARD POSITIONS
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
global triggers; triggers=(confInfo[8]=='True') # flag as True when actually recording 

#SETUP CARDS 
cardPrototype = {'G1':0, 'G2':0, 'L1':0, 'L2':0, 'fn':''}

#setup deck of four cards from the whole deck
#deck = SelectCardSubset( 4, N_OF_CARDS )

global currentTgt; currentTgt = (-1, -1, -1, -1)

#TODO: ADD ERROR CHECKING! Here we trust the json files to be correctly formed and valid
confFile = open( '.'+s+'configs'+s+confInfo[6]+'.json' )
config = json.loads( confFile.read() )
confFile.close()

gameScore = 0
lastScore = 0

for item in config['sets']:
    if( item['type'] == 'instruction'):
        temp=string.replace( item['file'], '\\', s )
        instrFile = open( temp )
        instrSequence = json.loads( instrFile.read() )
        instrFile.close()
        ShowInstructionSequence( instrSequence )
        
    elif item['type'] == 'set':
        temp=string.replace( item['file'], '\\', s )
        seqFile = open( temp )
        setSequence = json.loads( seqFile.read() )
        seqFile.close()
        currentSet += 1
        logThis("{:02d}".format(currentSet) + '.00_' + 'Running set %s' % (item['file']) )

        #run test type based on confInfo
        global stimPath; stimPath = setSequence['set']['stimpath']
        stimPath=string.replace( stimPath, '\\', s )

        # RESTRICT CARD SETS FOR REDUCED FEATURE SETS ---------------------------------
        active_rules = [1,1,1,1]
        if string.find(stimPath, 'noise') != -1:
            active_rules = [0,0,1,1]
        elif string.find(stimPath, 'patch') != -1:
            active_rules = [1,1,0,0]

        tgtCards = (deepcopy(cardPrototype), \
                    deepcopy(cardPrototype), \
                    deepcopy(cardPrototype), \
                    deepcopy(cardPrototype) )

        SetupCategoryCards( tgtCards )
           
        stimCards = ( visual.ImageStim( win, pos=cardPos[0] ), \
                      visual.ImageStim( win, pos=cardPos[1] ), \
                      visual.ImageStim( win, pos=cardPos[2] ), \
                      visual.ImageStim( win, pos=cardPos[3] ) )

        stimCards[0].setImage( tgtCards[0]['fn'] )
        stimCards[1].setImage( tgtCards[1]['fn'] )
        stimCards[2].setImage( tgtCards[2]['fn'] )
        stimCards[3].setImage( tgtCards[3]['fn'] )

        tgtCard = visual.ImageStim( win, pos=( 0, 0 ) )

        cardCount = 0
        rightAnswers = 0
        ruleCount=0

        RunSequence( setSequence['set'] )
        
    else:
        print 'unidentified item type in config: ' + item['type']
    

# - CLEANUP -------------------------------------------------------------------------------------

win.close()
core.quit()