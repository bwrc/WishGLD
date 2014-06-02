
from psychopy import visual,core,monitors,event,gui
import itertools
import random

from PIL import Image

IMG_W = 512
IMG_H= 512
DIMX = 26
DIMY = 26

#lenovo
myMon=monitors.Monitor('yoga', width=29.3, distance=40); myMon.setSizePix((3200, 1800))
#desktop
#myMon=monitors.Monitor('asus', width=37.8, distance=40); myMon.setSizePix((1920, 1080))
win = visual.Window( size=(IMG_W, IMG_H),units='pix',fullscr=False,monitor=myMon, color=(1.0, 1.0, 1.0), colorSpace='rgb')
#win = visual.Window( size=(IMG_W, IMG_H),units='pix',fullscr=False,monitor=myMon, color=(0.0, 0.0, 0.0), colorSpace='rgb')

faces = []
#faces.append( Image.open('C:\\Kride\\Projects\\ReKnow\\WCST\\letters\\noiseA.png' ) );

#faces
#for i in range(17):
#    faces.append( Image.open('C:\\Kride\\Projects\\ReKnow\\WCST\\26x26\\f' + '%02d' % (i+1,) + '.png') )

#letters
for i in range(17):
    faces.append( Image.open('C:\\Kride\\Projects\\ReKnow\\WCST\\shinedef1by1\\ltr' + '%01d' % (i+1,) + ' (Custom).png') )

#face1 = Image.open('pics\\natalie26.png')
#face2 = Image.open('pics\\girl1.png')
#face3 = Image.open('pics\\girl2.png')
#face4 = Image.open('pics\\ben.png')
#face5 = Image.open('pics\\letter_S.png')
#face6 = Image.open('pics\\letter_S_noise.png')
#face7 = Image.open('pics\\letter_S_noise2.png')

#facetest = Image.open( 'C:\\Kride\\Projects\\ReKnow\\pics\\faces_ATTK\\26x26\\f01.png' )
#faces.append( facetest )

#faces.append( face1 )
#faces.append( face2 )
#faces.append( face3 )
#faces.append( face4 )
#faces.append( face5 )
#faces.append( face6 )
#faces.append( face7 )

col1 = (35/255.0, 197/255.0, 79/255.0)
col2 = (196/255.0, 171/255.0, 3/255.0) # NOT APPENDED
col3 = (255/255.0, 114/255.0, 75/255.0)
col4 = (222/255.0, 134/255.0, 255/255.0)
col5 = (0/255.0, 191/255.0, 187/255.0) 
#col1 = (/255.0, /255.0, /255.0, 1.0)

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
                         #,\
                         #pos=(0, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0)#,\
                         #interpolate=True, lineRGB=None, fillRGB=None, name='', autoLog=True)
                         
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

#feats.append( featStarTrek )
#feats.append( featA )

step = IMG_W/DIMX
half = -1*IMG_W/2 #image coords are centered


#featN = 0
#faceN = 0

PREVAIL_COL_RATIO = 0.5
N_OF_FACES = 18
N_OF_FEATS = 4
SAVE_FRAMES = True

#card generation    
for faceN in range( N_OF_FACES ):

    for cardColor in range(4):
        colIdx = [0, 1, 2, 3]
        colIdx.remove( cardColor )

        for featN in range( 4):# N_OF_FEATS ):

            for featOrientation in range( 4 ): 

                for x in range(DIMX):
                    for y in range(DIMY):

                        feats[featN].pos = ( half+(x+1)*step, half+(y+1)*step)
                        #sz = random.random()
                   
                        val = faces[faceN].getpixel( (x,DIMY-1-y) )
                        #flip y-axis
                        sz = (255-val)/255.0
                        
                        if (random.random() <= PREVAIL_COL_RATIO):
                            c = cardColor
                        else:
                            c = colIdx[random.randint(0,2)]
                            
                        feats[featN].fillColor = colors[c]
                        feats[featN].lineColor = colors[c]

                        #feats[featN].opacity = 1.0 - x*1.0/DIMX
                        feats[featN].ori = 45+ 90*featOrientation
                        
                        feats[featN].size = (sz, sz)
                        
                        feats[featN].draw( win )

                win.flip()
                if( SAVE_FRAMES ):
                    win.getMovieFrame()
#faces                    win.saveMovieFrames( 'C:\\Kride\\Projects\\ReKnow\\WCST\\facecards\\%02d_%02d_%02d_%02d.png' % (faceN, cardColor, featN, featOrientation ))
                    win.saveMovieFrames( 'C:\\Kride\\Projects\\ReKnow\\WCST\\lettercards\\%02d_%02d_%02d_%02d.png' % (faceN, cardColor, featN, featOrientation ))

#                keys = event.getKeys()
#                if keys:
#                   if keys[0] == 'escape':
#                       break
#                   else:
#                        keys.clear()


#cleanup
win.close()
core.quit()


"""the old code
while( True ):
    
#    gabor.draw( win )
    #select random color and remaing colors
    cardColor = random.randint(0,3)
    #print cardColor
    colIdx = [0, 1, 2, 3]
    #print colIdx
    colIdx.remove( cardColor )
    #print colIdx

    for x in range(DIMX):
        for y in range(DIMY):
            feats[featN].pos = ( half+(x+1)*step, half+(y+1)*step)
            #sz = random.random()
       
            val = faces[faceN].getpixel( (x,DIMY-1-y) )
            #flip y-axis
            sz = (255-val)/255.0
            
            if (random.random() <= 0.5):
                c = cardColor
            else:
                c = colIdx[random.randint(0,2)]
                
            feats[featN].fillColor = colors[c]
            feats[featN].lineColor = colors[c]

            #feats[featN].opacity = 1.0 - x*1.0/DIMX
            feats[featN].ori = 45+ 90*featN
            
            feats[featN].size = (sz, sz)
            
            feats[featN].draw( win )

    win.flip()
    
    win.getMovieFrame( )
    win.saveMovieFrames( '.\\frames\\%02d_%02d_%02d.png' % (faceN, featN, cardColor ))#+ str(G1) + '_' + str(G2) + '_' + str(L1) + '_' + str(L2) + '.png' )
    
    #keys = event.getKeys()
    keys = event.waitKeys()
    if keys:
       if keys[0] == 'escape':
           break
       if keys[0] == 'space':
           featN = (featN+1) % 6
           faceN = (faceN+1) % 3

"""