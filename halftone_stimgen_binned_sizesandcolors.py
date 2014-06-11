
from psychopy import visual,core,monitors,event,gui
import itertools
import random

from PIL import Image

PIC_LOAD_PATH = 'C:\\Kride\\Projects\\ReKnow\\WCST\\26x26\\'
PIC_SAVE_PATH='C:\\Kride\\Projects\\ReKnow\\WCST\\shinned\\faces\\'

IMG_W = 512
IMG_H= 512
DIMX = 26
DIMY = 26

#lenovo
myMon=monitors.Monitor('yoga', width=29.3, distance=40); myMon.setSizePix((3200, 1800))
#desktop
#myMon=monitors.Monitor('asus', width=37.8, distance=40); myMon.setSizePix((1920, 1080))
win = visual.Window( size=(IMG_W, IMG_H),units='pix',fullscr=False,monitor=myMon, color=(1.0, 1.0, 1.0), colorSpace='rgb')

faces = []

#faces
for i in range(16):
    faces.append( Image.open( PIC_LOAD_PATH + 'f' + '%02d' % (i+1,) + '.png') )
#    faces.append( Image.open('.\\26x26\\sf%02d' % (i+1,) + '.png') )
#   faces.append( Image.open('.\\26x26\\smlltr%01d' % (i+1,) + '.png') )

#letters
#for i in range(17):
#    faces.append( Image.open('C:\\Kride\\Projects\\ReKnow\\WCST\\shinedef1by1\\ltr' + '%01d' % (i+1,) + ' (Custom).png') )

#equiluminant colors
col1 = (35/255.0, 197/255.0, 79/255.0)
col2 = (196/255.0, 171/255.0, 3/255.0) # NOT APPENDED
col3 = (255/255.0, 114/255.0, 75/255.0)
col4 = (222/255.0, 134/255.0, 255/255.0)
col5 = (0/255.0, 191/255.0, 187/255.0) 

colors = []
colors.append( col1 )
colors.append( col3 )
colors.append( col4 )
colors.append( col5 )

#SHAPES
featTriangle = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                         vertices=((0, 10), (8, -10), (-8, -10), (0, 10)), 
                         closeShape=True )
                         
featDiamond = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                         vertices=((0, 10), (8, -6), (0,-10), (-8, -6), (0, 10)), 
                         closeShape=True )

featHouse = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                         vertices=((0, 10), (5.7, 0), (5.7,-9), (-5.7, -9), (-5.7,0), (0, 10)), 
                         closeShape=True )

featArrow = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                         vertices=((0, 10), (8, 0), (4,0), (4, -10), (-4,-10), (-4, 0), (-8, 0), (0,10)), 
                         closeShape=True )

#not used
#featDrop = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
#                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
#                         vertices=((0, 10), (7, 1), (6.9, -4), (5.65, -5.65), (4, -6.9), (0,-8), (-4, -6.9), (-5.65, -5.65), (-6.9, -4), (-7, 1), (0, 10)), 
#                         closeShape=True )

#featStarTrek = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
#                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
#                         vertices=((0, 10), (8, -10), (0,0), (-8, -10), (0, 10)), 
#                         closeShape=True )

#featA = visual.ShapeStim( win, lineWidth=2.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
#                         fillColor=None, fillColorSpace='rgb',\
#                         vertices=((-6, -8), (0,10), (6,-8), (3,-4), (-3,-4) ),
#                         closeShape=True )


feats=[]

feats.append( featTriangle )
feats.append( featDiamond )
feats.append( featHouse )
feats.append( featArrow )

step = IMG_W/DIMX
half = -1*IMG_W/2 #image coords are centered

PREVAIL_COL_RATIO = 0.5
N_OF_FACES = 18
N_OF_FEATS = 4
SAVE_FRAMES = True
N_OF_BINS = 26

#card generation    
for faceN in range( N_OF_FACES ):

    pixels = []

    for x in range(DIMX):
        for y in range(DIMY):
            pixels.append( (faces[faceN].getpixel( (x,DIMY-1-y) ), x, y) )

    pixels.sort( key=lambda tup: tup[0] )

    mp = pixels[ len(pixels)-1 ][0]

    nOfBins=N_OF_BINS
    valPerBin = len(pixels)/ nOfBins

    for cardColor in range(4):
        colIdx = [0, 1, 2, 3]
        colIdx.remove( cardColor )

        #assign each bin random colors with prevailing color ratios
        colPerBin = []
        for a in range( N_OF_BINS ):
            colInBin = []
            for i in range( valPerBin ):
                if( random.random() <= PREVAIL_COL_RATIO ):
                    colInBin.append( 1 )
                else:
                    colInBin.append( 0 )
                     
            #make sure the list has at least PREVAIL_COL_RATIO items of prevailing color
            while(sum( colInBin ) / float( len( colInBin )) < PREVAIL_COL_RATIO ):
                colInBin[ random.randint( 0, len(colInBin)-1 ) ] = 1
                #print sum( colInBin ) / float( len( colInBin ) )

            # replace 1's and 0's with colors
            for i in range( len(colInBin) ):# in colInBin:
                if colInBin[i] == 1:
                    colInBin[i] = cardColor
                else:
                    colInBin[i] = colIdx[ random.randint(0,2) ]

            colPerBin.append( colInBin )

        for featN in range( 4):# N_OF_FEATS ):

            for featOrientation in range( 4 ): 

                currentPixel = 0

                binPixCounter = [0] * N_OF_BINS

                for p in pixels:
                    x = p[1]
                    y = p[2]
                    v = p[0]

                    n = currentPixel / valPerBin +1 #integer!
                    sz = 1.0 - float(n) / float(nOfBins)
                    #v = int( currentPixel / nOfBins ) +1
                    #sz = 1-v/221.0#676#(mp / nOfBins )
                    
                    feats[featN].pos = ( half+(x+1)*step, half+(y+1)*step)

#                    if (random.random() <= PREVAIL_COL_RATIO):
#                        c = cardColor
#                    else:
#                        c = colIdx[random.randint(0,2)]
                    
                    #print binPixCounter[n]
                    c = colPerBin[n-1][binPixCounter[n-1]]
                    binPixCounter[n-1] += 1

                    feats[featN].fillColor = colors[c]
                    feats[featN].lineColor = colors[c]
                    feats[featN].ori = 45+ 90*featOrientation
                    feats[featN].size = (sz, sz)
                    feats[featN].draw( win )

                    currentPixel += 1
 
                win.flip()
                if( SAVE_FRAMES ):
                    win.getMovieFrame()
                    win.saveMovieFrames( PIC_SAVE_PATH + '%02d_%02d_%02d_%02d.png' % (faceN, cardColor, featN, featOrientation ))
                    #win.saveMovieFrames( 'C:\\Kride\\Projects\\ReKnow\\WCST\\shinned\\letters\\%02d_%02d_%02d_%02d.png' % (faceN, cardColor, featN, featOrientation ))
#                    win.saveMovieFrames( 'C:\\Kride\\Projects\\ReKnow\\WCST\\lettercards\\%02d_%02d_%02d_%02d.png' % (faceN, cardColor, featN, featOrientation ))

#                keys = event.getKeys()
#                if keys:
#                   if keys[0] == 'escape':
#                       break
#                   else:
#                        keys.clear()

#cleanup
win.close()
core.quit()

