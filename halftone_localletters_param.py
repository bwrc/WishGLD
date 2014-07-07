
from psychopy import visual,core,monitors,event,gui
import itertools
import random
import os
import colorsys
import copy
import sys

from PIL import Image

#def generator(globaltype, globalcluster, filtertype, params):
#    global1, global2, local1=params.split('_')

# CONSTANTS
SAVE_FRAMES = True
IMG_W = 512
IMG_H= 512
DIMX = 26
DIMY = 26
s = os.sep

# CREATING MONITORS ---------------------------------------------------------------------------------------------------
#lenovo
#    myMon=monitors.Monitor('yoga', width=29.3, distance=40); myMon.setSizePix((3200, 1800))
#HP Elitebook 2560p
#    myMon=monitors.Monitor('Bens', width=31.5, distance=40); myMon.setSizePix((1366, 768))
#DELL Latitude
myMon=monitors.Monitor('BensTTL', width=31.5, distance=40); myMon.setSizePix((1600, 900))
#desktop
#    myMon=monitors.Monitor('asus', width=37.8, distance=40); myMon.setSizePix((1920, 1080))
win = visual.Window( size=(IMG_W, IMG_H),units='pix',fullscr=False,monitor=myMon,color=(1.0, 1.0, 1.0),colorSpace='rgb')

# PARAMETER PARSING --------------------------------------------------------------------------------------------------
globaltype = sys.argv[1]
globalcluster = sys.argv[2]
filtertype = sys.argv[3]
global1 = sys.argv[4]
global2 = sys.argv[5]
local1 = sys.argv[6]

# Global type, set FACES=0 or LETTERS=1 or TEST=2
gtype = int(globaltype)
# cluster can be 1 to 3 for global faces, 1 to 4 for global letters
cluster=int(globalcluster)
# version of stim prep to use, 0=cleaner, 1=more noise
ftype=int(filtertype)
# paramterisation for slow local letter production
g1 = int(global1)
g2 = int(global2)
l1 = int(local1)

print 'Global ' + str(globaltype)
print 'Cluster ' + str(globalcluster)
print 'Filter ' + str(filtertype)
print 'g1 ' + str(global1)
print 'g2 ' + str(global2)
print 'l1 ' + str(local1)
#print 'params ' + params

# PARAMETERISATION OF PATHS -------------------------------------------------------------------------------------------
tystr = ['face', 'letter', 'blank']
filter=[]
filter.append(['shelimdf', 'shsmimdf'])
filter.append(['bow', 'bowsl'])
#    filter.append(['wob', 'wobsl'])
gstims=['faces_final', 'letters_final']
# cluster sets
clsets=['AVXY', 'DJLU', 'CGOQ', 'HMNW']
letter = clsets[cluster][l1]

# VISUAL FEATURES -----------------------------------------------------------------------------------------------------

# GET A SET OF COLORS 
col1 = "#DB9D85"
col2 = "#86B875"
col3 = "#4CB9CC"
col4 = "#CD99D8"

colors = []
colors.append( col1 )
colors.append( col2 )
colors.append( col3 )
colors.append( col4 )
cardColor = g2

# SPECIFY PATHS
pth = '..'+s+ 'stimuli' +s
outdir = '..' +s+ 'stimuli' +s+ 'output' +s+ tystr[gtype] + '_letter_'
if gtype < 2:
    outdir = outdir + filter[gtype][ftype] + '_' + clsets[cluster] + '_cards' + s
    pth = pth + gstims[gtype] +s+ 'cluster_size_4' +s+ str(cluster+1) +s+ filter[gtype][ftype] +s
else:
    outdir = outdir + clsets[cluster] + '_cards' + s
if not os.path.exists(outdir):
    os.makedirs(outdir)

# GLOBALS
imgs = []

if gtype == 0:
    idx=g1+1
    imgs = Image.open(pth + 'f' + '%02d' %idx + '.png')   #faces
elif gtype == 1:
    imgs = Image.open(pth + filter[gtype][ftype] + clsets[cluster][g1] + '.png')    #letters
else:
    imgs = Image.open(pth + 'bowlank.png')   #TEST!

#LETTERS
ltrH = (IMG_H/DIMY)+3
feats = visual.TextStim( win, text=letter, font='Sloan', bold=True, height=ltrH )

# BUILDING CARDS AS STIM/COLOR/FEATURE/ORIENTATION COMBINATIONS -------------------------------------------------------

PREVAIL_COL_RATIO = 0.5
step = IMG_W/DIMX
half = -1*IMG_W/2 #image coords are centered
coef = (DIMX * DIMY) / 3

# CARD GENERATION -----------------------------------------------------------------------------------------------------
# Build color probabilities by observation
gt = 0  # greytotal
for xi in range(DIMX):
    for yi in range(DIMY):
        vali = imgs.getpixel( (xi,DIMY-1-yi) )
        gt = gt + (255-vali)/255.0
#        print 'image gt=' + str(round(gt)) # DEBUG PRINT
#    maxsz = max(max(imgsz))

colIdx = range(len(colors))
colIdx.remove( cardColor )

for featOrientation in range( 4 ):

#        ct = 0  # color total - to collect how much of the total coloured area is dominant
#        nt = 0  # other colors

    for x in range(DIMX):
        for y in range(DIMY):
            # SET LOCAL VALUES
            val = imgs.getpixel( (x,DIMY-1-y) )
            sz = (255-val)/255.0    #flip y-axis
            PREVAIL_COL_RATIO = (sz/gt)*coef
            
            feats.pos = (half+(x+1)*step, half+(y+1)*step)

#                print 'size=' + str(round(sz,3)) + '; PCR=' + str(round(PREVAIL_COL_RATIO,2)) # DEBUG PRINT
#                print 'idxi=' + str(idxi)

            if (random.random() < PREVAIL_COL_RATIO):
                c = cardColor
#                            ct = ct + sz
            else:
                c = colIdx[random.randint(0,2)]
#                            nt = nt + sz

            feats.setOri( 45+90*featOrientation )
            feats.setColor( colors[c] )
            feats.setHeight( sz*ltrH )
            feats.text = feats.text
            feats.draw( win )

    win.flip()
    if( SAVE_FRAMES ):
        win.getMovieFrame()
        win.saveMovieFrames( outdir + '%02d_%02d_%02d_%02d.png' % (g1, g2, l1, featOrientation ))

#cleanup
win.close()
core.quit()

# EXPLANATION AND HARD CODED 4-COLOR SET
def createColors():
    # CREATING COLORS -------------------------------------------------------------------------------------------

    # Color selection for equally perceivable colours is covered in Zeileis, Hornik and Murrell (2007), available here:
    #   http://epub.wu.ac.at/1692/1/document.pdf
    # The simple answer seems to be: use the CIE Luv color space. Code is here:
    #   http://cran.r-project.org/web/packages/colorspace/vignettes/hcl-colors.pdf
    # A palette derived from that R code (procedure unknown) is given as:

    col1 = "#DB9D85"
    col2 = "#86B875"
    col3 = "#4CB9CC"
    col4 = "#CD99D8"

    # A tool is available (below), which uses the CMC color differencing algorithm to "procedurally generate
    # a set of visually-distinguishable colors within a certain tolerance", it is convenient to support color-blindness
    #   http://phrogz.net/css/distinct-colors.html

    # In the link below, a list of 128 distinct CIE Lab colours is given in HEX - may be useful to expand the palette.
    #   http://stackoverflow.com/questions/2328339/how-to-generate-n-different-colors-for-any-natural-number-n
    # Another approach is given below; it is a palette in RGB, HSL and LAB space, derived from this peer reviewed paper:
    #   Boynton. Eleven Colors That Are Almost Never Confused. (1989)
    #   http://alumni.media.mit.edu/~wad/color/palette.html
    # Derivation was based on matching the qualitative palette from the paper with roughly even distributions in Lab space.
    #           H    S    L         L    A    B        R    G    B
    #Black      0    0    0         0    0    0        0    0    0
    #Dk. Gray   0    0    34        50   0    0        87   87   87
    #Red        0    80   68        50   58   40       173  35   35
    #Blue       229  80   95        50   40   -77      42   75   215
    #Green      114  80   41        50   -50  42       29   105  20
    #Brown      28   80   51        50   20   44       129  74   25
    #Purple     275  80   75        50   65   -61      129  38   192
    #Lt. Gray   0    0    63        75   0    0        160  160  160
    #Lt. Green  114  38   77        80   -34  25       129  197  122
    #Lt. Blue   229  38   100       80   9    -34      157  175  255
    #Cyan       180  80   82        80   -43  -14      41   208  208
    #Orange     28   80   100       80   28   62       255  146  51
    #Yellow     60   80   97        96   -19  77       255  238  51
    #Tan        28   20   93        91   5    12       233  222  187
    #Pink       0    20   100       91   15    6       255  205  243
    #White      0    0    100       100  0    0        255  255  255

    # set of duller colors
    #red = (173, 35, 35)
    #blue = (42, 75, 215)
    #green = (29, 105, 20)
    #brown = (129, 74, 25)
    #purple = (129, 38, 192)
    # set of brighter colors
    #ltgreen = (129, 197, 122)
    #ltblue = (157, 175, 255)
    #cyan = (41, 208, 208)
    #orange = (255, 146, 51)
    #
    # gray can be lighter or darker
    #gray = (1, 1, 1)
    #
    #norm = 255.0
    #gray = [x*(87/norm) for x in gray] # gray that you can set at any level by changing one number
    #red = [x/norm for x in red]
    #blue = [x/norm for x in blue]
    #green = [x/norm for x in green]
    #brown = [x/norm for x in brown]
    #purple = [x/norm for x in purple]
    #ltgreen = [x/norm for x in ltgreen]
    #ltblue = [x/norm for x in ltblue]
    #cyan = [x/norm for x in cyan]
    #orange = [x/norm for x in orange]

    # HSL colors
    # Absolutely equiluminant colours can be selected simply by iterating around the colour wheel in 360/N arcs
    # HOWEVER, this is not based on perceptual findings, as described above.
    #def get_N_HexCol(N, S, L):
    #
    #    HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
    #    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    #    RGB_tuples = map(lambda x: tuple(map(lambda y: int(y * 255),x)),RGB_tuples)
    #    HEX_tuples = map(lambda x: tuple(map(lambda y: chr(y).encode('hex'),x)), RGB_tuples)
    #    HEX_tuples = map(lambda x: "".join(x), HEX_tuples)
    #
    #    return HEX_tuples
    #CMY, RGB
    #colc = (0, 1, 1)
    #colm = (1, 0, 1)
    #coly = (1, 1, 0)
    #colr = (1, 0, 0)
    #colg = (0, 1, 0)
    #colb = (0, 0, 1)

    colors = []
    colors.append( col1 )
    colors.append( col2 )
    colors.append( col3 )
    colors.append( col4 )
    #colors.append( gray )
    #colors.append( red )
    #colors.append( blue )
    #colors.append( green )
    #colors.append( brown )
    #colors.append( purple )
    #colors.append( ltgreen )
    #colors.append( ltblue )
    #colors.append( cyan )
    #colors.append( orange )
    
    return colors


# PARAMETERISED FOR ONE SET OF GLOBAL FACES OR LETTERS AT A TIME
generator(2, 1, 0,'00_00_00')

#def multigen(glob,clst,filt)
#    generator(glob,clst,filt,'00_00_00')
#    generator(glob,clst,filt,'00_00_01')
#    generator(glob,clst,filt,'00_00_02')
#    generator(glob,clst,filt,'00_00_03')
#    generator(glob,clst,filt,'00_01_00')
#    generator(glob,clst,filt,'00_01_01')
#    generator(glob,clst,filt,'00_01_02')
#    generator(glob,clst,filt,'00_01_03')
#    generator(glob,clst,filt,'00_02_00')
#    generator(glob,clst,filt,'00_02_01')
#    generator(glob,clst,filt,'00_02_02')
#    generator(glob,clst,filt,'00_02_03')
#    generator(glob,clst,filt,'00_03_00')
#    generator(glob,clst,filt,'00_03_01')
#    generator(glob,clst,filt,'00_03_02')
#    generator(glob,clst,filt,'00_03_03')
#    generator(glob,clst,filt,'01_00_00')
#    generator(glob,clst,filt,'01_00_01')
#    generator(glob,clst,filt,'01_00_02')
#    generator(glob,clst,filt,'01_00_03')
#    generator(glob,clst,filt,'01_01_00')
#    generator(glob,clst,filt,'01_01_01')
#    generator(glob,clst,filt,'01_01_02')
#    generator(glob,clst,filt,'01_01_03')
#    generator(glob,clst,filt,'01_02_00')
#    generator(glob,clst,filt,'01_02_01')
#    generator(glob,clst,filt,'01_02_02')
#    generator(glob,clst,filt,'01_02_03')
#    generator(glob,clst,filt,'01_03_00')
#    generator(glob,clst,filt,'01_03_01')
#    generator(glob,clst,filt,'01_03_02')
#    generator(glob,clst,filt,'01_03_03')
#    generator(glob,clst,filt,'02_00_00')
#    generator(glob,clst,filt,'02_00_01')
#    generator(glob,clst,filt,'02_00_02')
#    generator(glob,clst,filt,'02_00_03')
#    generator(glob,clst,filt,'02_01_00')
#    generator(glob,clst,filt,'02_01_01')
#    generator(glob,clst,filt,'02_01_02')
#    generator(glob,clst,filt,'02_01_03')
#    generator(glob,clst,filt,'02_02_00')
#    generator(glob,clst,filt,'02_02_01')
#    generator(glob,clst,filt,'02_02_02')
#    generator(glob,clst,filt,'02_02_03')
#    generator(glob,clst,filt,'02_03_00')
#    generator(glob,clst,filt,'02_03_01')
#    generator(glob,clst,filt,'02_03_02')
#    generator(glob,clst,filt,'02_03_03')
#    generator(glob,clst,filt,'03_00_00')
#    generator(glob,clst,filt,'03_00_01')
#    generator(glob,clst,filt,'03_00_02')
#    generator(glob,clst,filt,'03_00_03')
#    generator(glob,clst,filt,'03_01_00')
#    generator(glob,clst,filt,'03_01_01')
#    generator(glob,clst,filt,'03_01_02')
#    generator(glob,clst,filt,'03_01_03')
#    generator(glob,clst,filt,'03_02_00')
#    generator(glob,clst,filt,'03_02_01')
#    generator(glob,clst,filt,'03_02_02')
#    generator(glob,clst,filt,'03_02_03')
#    generator(glob,clst,filt,'03_03_00')
#    generator(glob,clst,filt,'03_03_01')
#    generator(glob,clst,filt,'03_03_02')
#    generator(glob,clst,filt,'03_03_03')
#
# THE FUNCTIONAL CODE (TESTING ONLY WITH FIRST CLUSTER):
#multigen(0,0,0)
#multigen(0,0,1)
#multigen(1,0,0)
