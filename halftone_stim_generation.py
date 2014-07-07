
from psychopy import visual,core,monitors,event,gui
import itertools
import random
import os
import colorsys
import copy

from PIL import Image

def generator(globaltype, localtype, filtertype, savef):

    cluster=1
    # Global type, set FACES=0 or LETTERS=1 or TEST=2
    gtype = globaltype
    # Local type, set shapes=0 or LETTERS=1 or TEST=2
    ltype = localtype
    # version of stim prep to use
    ftype=filtertype
    gstims=['faces_final', 'letters_final']
    filter=[]
    filter.append(['shelimdf', 'shsmimdf'])
    filter.append(['bow', 'bowsl'])
#    filter.append(['wob', 'wobsl'])
    # cluster sets
    clsets=['AVXY', 'DJLU', 'CGOQ', 'HMNW']

    SAVE_FRAMES = savef
    IMG_W = 512
    IMG_H= 512
    DIMX = 26
    DIMY = 26

    s = os.sep
    pth = '..'+s+ 'stimuli' +s+ gstims[gtype] +s+ 'cluster_size_4' +s+ str(cluster+1) +s+ filter[gtype][ftype] +s
    tystr = ['face', 'letter', 'test']
    outdir = '..' +s+ 'stimuli' +s+'output' +s+ tystr[gtype] + '_' + tystr[ltype] + '_' + filter[gtype][ftype]
    # debugging:
#    if ltype != 1:
#        inltr = 0
#    if inltr > 0:
#        outdir = outdir + inltr
    
    outdir = outdir + '_cards' + s
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # CREATING MONITORS
    #lenovo
#    myMon=monitors.Monitor('yoga', width=29.3, distance=40); myMon.setSizePix((3200, 1800))
    #HP Elitebook 2560p
#    myMon=monitors.Monitor('Bens', width=31.5, distance=40); myMon.setSizePix((1366, 768))
    #DELL Latitude
    myMon=monitors.Monitor('BensTTL', width=31.5, distance=40); myMon.setSizePix((1600, 900))
    #desktop
    #myMon=monitors.Monitor('asus', width=37.8, distance=40); myMon.setSizePix((1920, 1080))
    win = visual.Window( size=(IMG_W, IMG_H),units='pix',fullscr=False,monitor=myMon,color=(1.0, 1.0, 1.0),colorSpace='rgb')

    imgs = []

    if gtype == 0:
        for i in range(4):
            imgs.append( Image.open(pth + 'f' + '%02d' % (i+1,) + '.png') )   #faces
    elif gtype == 1:
        letters=clsets[cluster]
        for i in range(4):
            imgs.append( Image.open(pth + filter[gtype][ftype] + letters[i] + '.png') )    #letters
    else:
        imgs.append( Image.open('26x26' +s+ 'testi.png') )   #TEST!


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


    # VISUAL FEATURES ----------------------------------------------------------------------------------------------
    feats=[]

    #SHAPES
    featTriangle = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                             fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                             vertices=((0, 10), (8, -10), (-8, -10), (0, 10)), closeShape=True )
                             
    featDiamond = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                             fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                             vertices=((0, 10), (8, -6), (0,-10), (-8, -6), (0, 10)),\
                             closeShape=True )

    featHouse = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                             fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                             vertices=((0, 10), (5.7, 0), (5.7,-9), (-5.7, -9), (-5.7,0), (0, 10)), 
                             closeShape=True )

    featArrow = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                             fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                             vertices=((0, 10), (8, 0), (4,0), (4, -10), (-4,-10), (-4, 0), (-8, 0), (0,10)),\
                             closeShape=True )

    #not used
    #featDrop = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
    #                         fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
    #                         vertices=((0, 10), (7, 1), (6.9, -4), (5.65, -5.65), (4, -6.9), (0,-8), (-4, -6.9), (-5.65, -5.65), (-6.9, -4), (-7, 1), (0, 10)), 
    #                         closeShape=True )

    featStarTrek = visual.ShapeStim( win, lineWidth=1.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
                             fillColor=(0.0, 0.0, 0.0), fillColorSpace='rgb',\
                             vertices=((0, 10), (8, -10), (0,0), (-8, -10), (0, 10)),\
                             closeShape=True )

    #featA = visual.ShapeStim( win, lineWidth=2.0, lineColor=(0.0, 0.0, 0.0), lineColorSpace='rgb',\
    #                         fillColor=None, fillColorSpace='rgb',\
    #                         vertices=((-6, -8), (0,10), (6,-8), (3,-4), (-3,-4) ),\
    #                         closeShape=True )


    #LETTERS
    ltrH = (IMG_H/DIMY)+3
    # REFERENCE:
    #visual.TextStim( win, text='a letter', font='a system font', pos=(0.0, 0.0), depth=0, rgb=None, color=(0.0, 0.0, 0.0),\
    #                colorSpace='rgb', opacity=1.0, contrast=1.0, units='', ori=0.0, height=None, antialias=True,\
    #                bold=False, italic=False, alignHoriz='center', alignVert='center', fontFiles=[], wrapWidth=None,\
    #                flipHoriz=False, flipVert=False, name=None, autoLog=None ) )

    #visual.TextStim( win, text='', fontFiles=['Sloan.otf'] )   # Uncomment IF SLOAN FONT IS NOT ON YOUR SYSTEM;

    if ltype == 0:
        feats.append( featTriangle )
        feats.append( featDiamond )
        feats.append( featHouse )
        feats.append( featArrow )
    elif ltype == 1:
        letters=clsets[cluster]
#        letters=inltr   # DEBUGGING
        lenltrs = len(letters)
        for ltr in range(len(letters)):
            feats.append( visual.TextStim( win, text=letters[ltr], font='Sloan', bold=True, height=ltrH ) )
    else:
        feats.append( featStarTrek )

#    f= copy.copy(feats)

    # BUILDING CARDS AS STIM/COLOR/FEATURE/ORIENTATION COMBINATIONS -------------------------------------------------------

    PREVAIL_COL_RATIO = 0.5
    N_OF_FACES = len(imgs)
    N_OF_FEATS = len(feats)
    N_CLRS = len(colors)

    #card generation
    for faceN in range( N_OF_FACES ):
        
        # Build color probabilities by observation
        gt = 0  # greytotal
        for xi in range(DIMX):
            for yi in range(DIMY):
                vali = imgs[faceN].getpixel( (xi,DIMY-1-yi) )
                gt = gt + (255-vali)/255.0
#        print 'image gt=' + str(round(gt)) # DEBUG PRINT

        for cardColor in range(N_CLRS):
            colIdx = range(N_CLRS)
            colIdx.remove( cardColor )

            for featN in range( N_OF_FEATS ):

                for featOrientation in range( 4 ):

                    # Here we draw one card
                    cardMaker(win, outdir, DIMX, DIMY, IMG_W, IMG_H, gt, feats[featN], featN, imgs[faceN], faceN, cardColor, colIdx, colors, featOrientation, SAVE_FRAMES, ltype)

    #cleanup
    win.close()
#    core.quit()

def cardMaker(win, outdir, DIMX, DIMY, IMG_W, IMG_H, gt, feat, fN, img, iN, cardColor, colIdx, colors, featOri, SAVE_FRAMES, ltype):
#    ct = 0  # color total - to collect how much of the total coloured area is dominant
#    nt = 0  # other colors
#    myMon=monitors.Monitor('Bens', width=31.5, distance=40); myMon.setSizePix((1366, 768))
#    win = visual.Window( size=(IMG_W, IMG_H),units='pix',fullscr=False,monitor=myMon, color=(1.0, 1.0, 1.0), colorSpace='rgb')

    ltrH = (IMG_H/DIMY)+3
    step = IMG_W/DIMX
    half = -1*IMG_W/2 #image coords are centered
    coef = (DIMX * DIMY) / 3
    for x in range(DIMX):
        for y in range(DIMY):

            feat.pos = (half+(x+1)*step, half+(y+1)*step)

            val = img.getpixel( (x,DIMY-1-y) )
            #flip y-axis
            sz = (255-val)/255.0
            
            PREVAIL_COL_RATIO = (sz/gt)*coef
            
    #            print 'size=' + str(round(sz,3)) + '; PCR=' + str(round(PREVAIL_COL_RATIO,2)) # DEBUG PRINT
            
            if (random.random() < PREVAIL_COL_RATIO):
                c = cardColor
    #                ct = ct + sz
            else:
                c = colIdx[random.randint(0,2)]
    #                nt = nt + sz
            
            feat.setOri( 45+90*featOri )
            if ltype == 0:
                feat.fillColor  = colors[c]
                feat.lineColor  = colors[c]
                feat.size       = sz
            elif ltype == 1:
                feat.setColor( colors[c] )
                feat.setHeight( sz*ltrH )
                feat.text = feat.text

            feat.draw( win )

    win.flip()
    if( SAVE_FRAMES ):
        win.getMovieFrame()
        win.saveMovieFrames( outdir + '%02d_%02d_%02d_%02d.png' % (iN, cardColor, fN, featOri))

    #    if ltype == 1:  print feats[featN].text # DEBUG PRINT
    #    print 'image ct=' + str(round(ct)) + '; nt=' + str(round(nt)) + '; ratio=' + str(round(ct/gt, 2)) # DEBUG PRINT

#    win.close()


#generator(0,0,0,True)
#generator(0,0,1,True)
#generator(0,1,0,True)
#generator(0,1,1,True)
generator(1,0,0,True)
generator(1,0,1,True)
#generator(1,1,0,True)
#generator(1,1,1,True)