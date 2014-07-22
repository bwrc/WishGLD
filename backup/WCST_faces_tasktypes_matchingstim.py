
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
import json
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
             'cue'   : 0xf0,\
             'feedback'   : 0x0f,\
             'stimOn'   : 0x10,\
             'refsOn' : 0x20,\
             'respRight' : 0x40,\
             'respWrong' : 0x80,\
             'start': 0xfe,\
             'stop': 0xff}
             
"""
0x00 clear
0xfe start
0xff stop

0x10 stimulus card on 
0x20 targets on (only if stim presented separately)

responses

0x40 + 0x01..0x04 right + rule
0x80 + 0x01..0x04 wrong + guess

use: 
    writePort( tgtOn | rule1 )
    writePort( respRight | rule1 )
    writePort( respWrong | rule2 ) #where rule2 would be impossible to deduce, since we don't know what the user meant?

"""

#parallel.setPortAddress(0x0378) #<-- add this for parallel triggering

def ShowInstructionSequence( instrFile ):
    print instrFile
    
def RunSequence( seqFile ):
    print seqFile


def SelectCardSubset( subSetCount, deckSize ):

    if( subSetCount > deckSize ):
        print('Trying to select %1d cards out of %1d cards. NOT POSSIBLE!')
        return []

    """Selects a random set of subSetCount cards from a deck of deckSize cards."""
    cards =[]

    for i in range(subSetCount):
        cn = randint( 0, deckSize-1)
        while cn in cards:
            #print 'omg: %01d:%01d' % (i, cn)
            cn = randint( 0, deckSize-1)
            
        cards.append( cn )

    return cards

#selects a random value [0..n-1], where the value != skip
def randomValue( n, skip ):
    c = randint( 0, n-1)
    while( c == skip ):
        c = randint( 0, n-1)
    return c

#selects a reference card that 
#given a target card [A, B, C, D] only matches on one feature
def selectRefCard( tgtCard, matchFeat ):
    if matchFeat == 0:
        rc = ( tgt[0],\
               randomValue( 4, tgtCard[1] ),\
               randomValue( 4, tgtCard[2] ),\
               randomValue( 4, tgtCard[3] ) )
    elif matchFeat == 1:
        rc = ( randomValue( 4, tgtCard[0] ),\
               tgt[1],\
               randomValue( 4, tgtCard[2] ),\
               randomValue( 4, tgtCard[3] ) )
    elif matchFeat == 2:
        rc = ( randomValue( 4, tgtCard[0] ),\
               randomValue( 4, tgtCard[1] ),\
               tgt[2],\
               randomValue( 4, tgtCard[3] ) )
    elif matchFeat == 3:
        rc = ( randomValue( 4, tgtCard[0] ),\
               randomValue( 4, tgtCard[1] ),\
               randomValue( 4, tgtCard[2] ),\
               tgt[3] )
    return rc

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

    cardstr = ''
    for idx in range(4):
        cardstr += '%01d: %01d,%01d,%01d,%01d | ' % ( idx, deck[ feat1[idx]], feat2[idx], feat3[idx], feat4[idx]) 

    logThis( 'Using deck: ' + cardstr );

    return True

def DebugMsg( msg ):
    txt = visual.TextStim( win, text=msg, pos=(150, 480), color=(1.0, 0.0, 0.0), colorSpace='rgb')
    txt.draw()

def SetupTrial( ):

# selects a stimcard matching one of each target card features
    global currentRule
    global ruleRepeats
    global tgtCards
    
    currentRule = rules[ ruleList[ ruleCount ][0] ]
    ruleRepeats = int( ruleList[ruleCount][1] )

    if DEBUG:
        print 'CURRENTRULE = ' + currentRule

    #get a random set for every round, if wanted
    if RANDOMIZE_CATEGORY_CARDS:
        SetupCategoryCards( tgtCards )
        stimCards[0].setImage( tgtCards[0]['fn'] )
        stimCards[1].setImage( tgtCards[1]['fn'] )
        stimCards[2].setImage( tgtCards[2]['fn'] )
        stimCards[3].setImage( tgtCards[3]['fn'] )

def GetStimCard( tgtCards ):
    
    #if DEBUG:
    #    print tgtCards
    
    match = [0, 1, 2, 3]
    match = randomizeOrder( match )
    
#    sc = [ tgtCards[0][rules[match[0]]],\
#           tgtCards[1][rules[match[1]]],\
#           tgtCards[2][rules[match[2]]],\
#           tgtCards[3][rules[match[3]]] ]
    sc = [ tgtCards[match[0]][rules[0]],\
           tgtCards[match[1]][rules[1]],\
           tgtCards[match[2]][rules[2]],\
           tgtCards[match[3]][rules[3]] ]
           
    return sc

def GetResponse():
    global currentRule, currentTgt, ruleCount, rightAnswers, gameScore

    event.clearEvents()
    #answerCorrect = False

    retVal = 0 #if not modified, breaks the task
    answerPressed = -1 # which card was selected?

    keys = event.waitKeys()
    if keys[0]=='escape':
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
           triggerAndLog( portCodes['respRight'] | portCodes['rule1'], 'RESP   1 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'G2':
            triggerAndLog( portCodes['respRight'] | portCodes['rule2'], 'RESP   1 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L1':
            triggerAndLog( portCodes['respRight'] | portCodes['rule3'], 'RESP   1 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L2':
            triggerAndLog( portCodes['respRight'] | portCodes['rule4'], 'RESP   1 ' + currentRule + ' ANSWER ' + str(retVal) )
    elif retVal < 0:
        gameScore -= 1
        if currentRule == 'G1':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule1'], 'RESP   0 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'G2':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule2'], 'RESP   0 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L1':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule3'], 'RESP   0 ' + currentRule + ' ANSWER ' + str(retVal) )
        if currentRule == 'L2':
            triggerAndLog( portCodes['respWrong'] | portCodes['rule4'], 'RESP   0 ' + currentRule + ' ANSWER ' + str(retVal) )

#    #if enough right answers given, update rule
#    if retVal > 0:
#        if rightAnswers % ruleRepeats == 0: # rightAnswers can't be 0 here since retVal wouldn't be > 0
#            #logThis( 'changing rule from ' + currentRule ) 
#            ruleCount += 1
#            rightAnswers = 0
#            currentRule = rules[ruleList[ruleCount][0]]
#            #logThis( '...to ' + currentRule ) 
    
    return retVal

def GiveFeedback( taskType, fbVal ):

    if fbVal > 0:
        triggerAndLog( portCodes['feedback'], 'FEEDB  CORRECT ' + str(rightAnswers) + ' of ' + str(ruleRepeats) );
    else:
        triggerAndLog( portCodes['feedback'], 'FEEDB  FAIL ' + str(rightAnswers) + ' of ' + str(ruleRepeats) );
        
    if taskType == 1:
        if fbVal > 0:
            ShowInstruction('RIGHT', 1)
        else:
            ShowInstruction('WRONG', 1)

    elif taskType == 2:
        if fbVal > 0:
            frameCard( (0,0), 'green', 1 )
        else:
            frameCard( (0,0), 'red', 1 )
            
    elif (taskType == 3) | (taskType == 4) | (taskType==5):

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
    win.flip( clearBuffer = False ) #for some odd reason without this the backbuffer is empty while drawing the frame, and then flashes the cards
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
    triggerAndLog( portCodes['cue'], 'CUE' ) 
    core.wait(duration)
    #win.flip()

def NextTrial( tasktype ):

    # select next random stimcard
    global currentTgt
    global currentRule
    #currentTgt = ( randint(0, 3),\
    #               randint(0, 3),\
    #               randint(0, 3),\
    #               randint(0, 3) )

    currentTgt = GetStimCard( tgtCards )
    #major debug
    for t in tgtCards:
        count = 0
        for i in range(4):
            if currentTgt[i] == t[rules[i]]:
                count += 1
        if count > 1:
            print 'VITTUSAATANA-----------------------------------------------'
            print currentTgt
            print tgtCards
            print '-----------------------------------------------------------'

    if DEBUG:
        print 'stimcard'
        print currentTgt

    fn = stimPath + '%02d_%02d_%02d_%02d.png' % (deck[currentTgt[0]], currentTgt[1], currentTgt[2], currentTgt[3]) 
    tgtCard.setImage( fn )

    if DEBUG:
        print 'stim: ' + fn

    if tasktype == 1: # 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        fixCross( 1 )

#        if SEPARATE_STIM: #first show stimcard for a short period of SEP_STIM_DURATION (in refresh frames, x 16ms), then the target cards
        win.clearBuffer()
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'], 'STIM   ' + str( currentTgt[0] ) + ', ' + str( currentTgt[1] ) + ', ' +str( currentTgt[2] ) + ', ' +str( currentTgt[3] ) + ' RULE ' + currentRule )

        win.flip() #clear

        #else: # show all cards at the same time
        #        tgtCard.draw(win)
            
        for c in stimCards:
            c.draw(win)

        if DEBUG:
            DebugMsg( 'current rule ' + str(currentRule) )

        win.flip()

        triggerAndLog( portCodes['refsOn'], \
                'TGT    ' + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
                       + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
                       + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
                       + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 2: # 2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222

        fixCross( 1 )

#        if SEPARATE_STIM: #first show stimcard for a short period of SEP_STIM_DURATION (in refresh frames, x 16ms), then the target cards
        win.clearBuffer()
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'], 'STIM   ' + str( currentTgt[0] ) + ', ' + str( currentTgt[1] ) + ', ' +str( currentTgt[2] ) + ', ' +str( currentTgt[3] ) + ' RULE ' + currentRule)

        win.flip() #clear

        #else: # show all cards at the same time
        #        tgtCard.draw(win)
            
        for c in stimCards:
            c.draw(win)

        if DEBUG:
            DebugMsg( 'current rule ' + str(currentRule) )

        win.flip()

        triggerAndLog( portCodes['refsOn'], \
                'TGT    ' + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
                       + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
                       + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
                       + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

        #draw stim card to back buffer for feedback -> flip in GiveFeedback, ugly but efficient
        tgtCard.draw(win)

    elif taskType == 3: # 3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

        fixCross(0.5)
        
        for i in range( SEP_STIM_DURATION ): #accurate timing trick
            tgtCard.draw(win)
            win.flip()
            if i == 0:
                triggerAndLog( portCodes['stimOn'], 'STIM   ' + str( currentTgt[0] ) + ', ' + str( currentTgt[1] ) + ', ' +str( currentTgt[2] ) + ', ' +str( currentTgt[3] ) + ' RULE ' + currentRule)

        win.flip() #clear

        for c in stimCards:
            c.draw(win)

        if DEBUG:
            DebugMsg( 'current rule ' + str(currentRule) )

        win.flip( clearBuffer= False ) # keep the cards in the backbuffer for feedback

        triggerAndLog( portCodes['refsOn'], \
                'TGT    ' + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
                       + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
                       + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
                       + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 4: # 4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444

        tgtCard.draw(win)

        for c in stimCards:
            c.draw(win)

        if DEBUG:
            DebugMsg( 'current rule ' + str(currentRule) )

        win.flip( ) # keep the cards in the backbuffer for feedback

    # TODO concurrent presentation not compatible with logging scheme?
        triggerAndLog( portCodes['stimOn'], \
                'TGT    ' + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
                       + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
                       + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
                       + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    elif taskType == 5: # 3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

        #fixCross(0.5)
        
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
                triggerAndLog( portCodes['stimOn'], 'STIM   ' + str( currentTgt[0] ) + ', ' + str( currentTgt[1] ) + ', ' +str( currentTgt[2] ) + ', ' +str( currentTgt[3] ) + ' RULE ' + currentRule )

        win.flip() #clear

        for c in stimCards:
            c.draw(win)

        if DEBUG:
            DebugMsg( 'current rule ' + str(currentRule) )

        win.flip( clearBuffer= False ) # keep the cards in the backbuffer for feedback

        triggerAndLog( portCodes['refsOn'], \
                'TGT    ' + str(tgtCards[0]['G1']) + ',' + str(tgtCards[0]['G2'])+ ',' + str(tgtCards[0]['L1']) + ',' + str(tgtCards[0]['L2']) + '; '\
                       + str(tgtCards[1]['G1']) + ',' + str(tgtCards[1]['G2'])+ ',' + str(tgtCards[1]['L1']) + ',' + str(tgtCards[1]['L2']) + '; '\
                       + str(tgtCards[2]['G1']) + ',' + str(tgtCards[2]['G2'])+ ',' + str(tgtCards[2]['L1']) + ',' + str(tgtCards[2]['L2']) + '; '\
                       + str(tgtCards[3]['G1']) + ',' + str(tgtCards[3]['G2'])+ ',' + str(tgtCards[3]['L1']) + ',' + str(tgtCards[3]['L2']) )

    else: 
        ShowInstruction("Wrong Task Type (NextTrial)", 1)

def logThis( msg ):
    logging.log( msg, level=myLogLevel )

def triggerAndLog( trigCode, msg, trigDuration=10 ):
    #parallel.setData( trigCode ) #<-- add this for parallel triggering
    logThis( msg )
    #core.wait( trigDuration/1000.0, hogCPUperiod = trigDuration/1000.0 ) #<-- add this for parallel triggering
    #parallel.setData( portCodes['clear'] ) #<-- add this for parallel triggering

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

    instr = visual.TextStim( win, text=txt, pos=(0,-50), color=col, colorSpace='rgb', height=50 )

    pic = visual.ImageStim( win );
    pic.setImage( picFile );

    h = pic.size

    picpos = ( 0, h[1]/2 + 20 )
    textpos = ( 0, -1* instr.height/2 - 10)

    pic.setPos( picpos );
    pic.draw( win );

    instr.setPos( textpos )
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

def ShowTestInstructions():
    instr = open('.\instructions.txt')
    txt = instr.read()
    lines = txt.splitlines()
    
    for i in range( len(lines) ):
#        print '<' + lines[i] + '>'
        if( i % 2 == 0 ):
                ShowPicInstruction( lines[i], -1, lines[i+1], 1)
    
    #ShowPicInstruction( 'here be\ntext\nbe text\nbe text', -1, tgtCards[0]['fn'], 1)

# - MAIN PROG -------------------------------------------------------------------------------------

#init random seed
seed()

# Gather info / dialog
myDlg = NewDlg.NewDlg(title="The amazing ReKnow mindfuck")

myDlg.addText('Subject info')
myDlg.addField('SubjID:', width=30)
myDlg.addField('Age:', 18)

myDlg.addText('Experiment Info')
myDlg.addField('Randomize Category Cards:', choices=["No", "Yes"])
myDlg.addField('Select presentation mode', choices=["1 :: Sequential, Feedback:R/W", \
                                                     "2 :: Sequential, Feedback: stimcard",\
                                                     "3 :: Sequential, Feedback: framed target",\
                                                     "4 :: Concurrent",\
                                                     "5 :: Gamify"\
                                                     ])
myDlg.addField('Group:', choices=["Test", "Control"])

myDlg.addField('Show Instructions?', choices=["No", "Yes"])

myDlg.addField('Config File:', '.\\configs\config1.json', width=30);


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

logThis('Subj ID: ' + confInfo[0] )
logThis('Run: ' + str(datetime.utcnow()) )
logThis('Age: ' + str(confInfo[1]) )

if confInfo[4] == 0:
    logThis('Group: Test')
else:
    logThis('Group: Control')

startWithInstructions = False
if confInfo[5] == 'Yes':
    startWithInstructions = True

logThis('--------------------------------------------------------')

logThis('INFO')
logThis('timestamp CUE')
logThis('timestamp STIM  [state for each rule G1 G2 L1 L2 : 0,1,2,3] RULE [current rule]')
logThis('timestamp TGT   [states for each card / Up, Right, Down, Left: 0,1,2,3; 0,1,2,3;...]') 
logThis('timestamp RESP  [correct: 1/0] [current rule: G1, G2, L1, L2] ANSWER [card selected: 1(up), 2(right), 3(down), 4(left)]')
logThis('timestamp FEEDB [correct/fail] [correct answers] of [series length]')
logThis('--------------------------------------------------------')
logThis('\n')

# SETUP TEST PARAMS
if confInfo[2] == 'No':
    RANDOMIZE_CATEGORY_CARDS = False
else:
    
    RANDOMIZE_CATEGORY_CARDS = True

#if confInfo[3] == 'No':
#    SEPARATE_STIM = False
#else:
#    SEPARATE_STIM = True

#rendering window setup
#myMon = monitors.Monitor('yoga', width=29.3, distance=40); myMon.setSizePix((3200, 1800))
myMon=monitors.Monitor('dell', width=37.8, distance=50); myMon.setSizePix((1920, 1080))
#myMon=monitors.Monitor('dell', width=37.8, distance=50); myMon.setSizePix((1920, 1200))

#pygame detects screen size correctly, but draws on a 1280x720 surface??
#pyglet reports the screen size as 1280x720
win = visual.Window( winType='pyglet', size=(1920, 1080),units='pix',fullscr=True, monitor=myMon, rgb=(1,1,1)) # set screen=1 for multiple monitors
#win = visual.Window( winType='pyglet', size=(1920, 1200),units='pix',fullscr=True, monitor=myMon, rgb=(1,1,1))
#win = visual.Window( winType='pyglet', size=(3200, 1800),units='pix',fullscr=True, monitor=myMon, rgb=(1,1,1))

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
#stimCards = ( visual.ImageStim( win, pos=( 0, 266) ), \
#              visual.ImageStim( win, pos=( 522, 0) ), \
#              visual.ImageStim( win, pos=( 0, -266) ), \
#              visual.ImageStim( win, pos=( -522, 0) ))

taskType = int( confInfo[3][0] ) # 1, 2, 3, ...

global cardPos; cardPos = []

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

stimCards = ( visual.ImageStim( win, pos=cardPos[0] ), \
              visual.ImageStim( win, pos=cardPos[1] ), \
              visual.ImageStim( win, pos=cardPos[2] ), \
              visual.ImageStim( win, pos=cardPos[3] ) )

stimCards[0].setImage( tgtCards[0]['fn'] )
stimCards[1].setImage( tgtCards[1]['fn'] )
stimCards[2].setImage( tgtCards[2]['fn'] )
stimCards[3].setImage( tgtCards[3]['fn'] )

tgtCard = visual.ImageStim( win, pos=( 0, 0 ) )

# - BEGIN -------------------------------------------------------------------------

confFile = open('.\\configs\\config1.json')
config = json.loads( confFile.read() )
confFile.close()

for item in config['test']:
    if( item['type'] == 'instruction'):
        ShowInstructionSequence( item['file'] )
    elif item['type'] == 'set':
        RunSequence( item['file'] )
    else:
        print 'unidentified item type in config: ' + item['type']

if( startWithInstructions == True ):
    ShowTestInstructions()
else:
    ShowInstruction( 'start', -1 )
    
#start test

global cardCount; cardCount = 0
global rightAnswers; rightAnswers = 0
global ruleCount; ruleCount=0

global gameScore; gameScore = 0 #for the gamify mode
global lastScore; lastScore = 0

#run test type based on confInfo

while ruleCount < (RULE_COUNT-1): #-1 because ruleCount gets upped before setting currentRule

    SetupTrial()
    NextTrial( taskType )
    answer = GetResponse()

    if answer == 0:
        break
    else:
        GiveFeedback( taskType, answer )

    #if enough right answers given, update rule
    #moved from getresponse
    if answer > 0:
        if rightAnswers % ruleRepeats == 0: # rightAnswers can't be 0 here since retVal wouldn't be > 0
            #logThis( 'changing rule from ' + currentRule ) 
            ruleCount += 1
            rightAnswers = 0
            currentRule = rules[ruleList[ruleCount][0]]
            #logThis( '...to ' + currentRule ) 

    cardCount +=1

# - CLEANUP -------------------------------------------------------------------------------------

win.close()
core.quit()
