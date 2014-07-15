
from psychopy import visual,core,monitors,event,gui
import itertools
import random
import os
import colorsys
import copy
import time

from PIL import Image


IMG_W = 512
IMG_H= 512
DIMX = 26
DIMY = 26

# CREATING MONITORS
#lenovo
#    myMon=monitors.Monitor('yoga', width=29.3, distance=40); myMon.setSizePix((3200, 1800))
#HP Elitebook 2560p
myMon=monitors.Monitor('Bens', width=31.5, distance=40); myMon.setSizePix((1366, 768))
#DELL Latitude
#myMon=monitors.Monitor('BensTTL', width=31.5, distance=40); myMon.setSizePix((1600, 900))
#desktop
#myMon=monitors.Monitor('asus', width=37.8, distance=40); myMon.setSizePix((1920, 1080))
win = visual.Window( size=(IMG_W, IMG_H),units='pix',fullscr=False,monitor=myMon,color=(1.0, 1.0, 1.0),colorSpace='rgb')


# CONVEX SHAPES
featTriangle = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(150, 200),\
                         vertices=((0, 11), (7, -11), (-7, -11), (0, 11)), closeShape=True )

featDiamond = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(150, 150),\
                         vertices=((0, 10), (8, -6), (0,-11), (-8, -6), (0, 10)), closeShape=True )

featHouse = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(100, 150),\
                         vertices=((0, 9.5), (6, 0), (6,-9), (-6, -9), (-6,0), (0, 9.5)), closeShape=True )

featDrop = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(100, 200),\
                         vertices=((0, 10), (7, 0), (7, -4), (6, -6), (4, -7), (0,-9), (-4, -7), (-6, -6), (-7, -4), (-7, 0), (0, 10)), 
                         closeShape=True )

# CONCAVE SHAPES
#caveTriangle = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
#                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(25, 25),\
#                         vertices=((0, 10), (6,0), (8, -10), (-8, -10), (0, -8), (0, 10)) )
caveTriangle = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(25, 25),\
                         vertices=((0, 11), (9, -11), (0,-6), (-9, -11), (0, 11)), closeShape=True )

caveDiamond = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(25, -25),\
                         vertices=((0, 10), (6, 2), (0, 0), (8, -6), (0,-10), (-8, -6), (0, 0), (-6, 2), (0, 10)), closeShape=True )

caveHouse = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(-25, -25),\
                         vertices=((0, 10), (7, 0), (7,-10), (4,-10), (4,-1), (-4,-1), (-4,-10), (-7, -10), (-7,0), (0, 10)), closeShape=True )

caveArrow = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(-25, 25),\
                         vertices=((0, 10), (8, 0), (4,0), (4, -10), (-4,-10), (-4, 0), (-8, 0), (0,10)), closeShape=True )

# SKEW SHAPES - FAIL!
skewTriangle = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(-100, -150),\
                         vertices=((0, 10), (5,0), (8, -10), (-8, -10), (-3,0), (0, 10)), closeShape=True )

skewDiamond = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(-100, -200),\
                         vertices=((2, 10), (8, -6), (2,-10), (-8, -6), (2, 10)), closeShape=True )

skewHouse = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(-150, -200),\
                         vertices=((-5, 10), (6, 0), (6, -10), (-5, -10), (-5, 10)), closeShape=True )

skewDrop = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb', pos=(-150, -150),\
                         vertices=((6, 12), (2,-8), (-4, -6.9), (-5.65, -5.65), (-6.9, -4), (-7, 1), (6, 12)), 
                         closeShape=True )
#patch=visual.GratingStim(win, tex='sin', mask='circle', pos=(0, 0), size=(50, 50), color=(1.0,0.0,0.0))
#patch.draw(win)

featTriangle.draw(win)
featDiamond.draw(win)
featHouse.draw(win)
featDrop.draw(win)

caveTriangle.draw(win)
caveDiamond.draw(win)
caveHouse.draw(win)
caveArrow.draw(win)

skewTriangle.draw(win)
skewDiamond.draw(win)
skewHouse.draw(win)
skewDrop.draw(win)

win.flip()

time.sleep(200)