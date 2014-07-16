import json, random
from psychopy import gui
import NewDlg
import os
import string

# JUST MODIFY THESE
s = os.sep
setpath = '.'+s+'stims'+s+'letters'+s
rules = [0, 1, 2, 3]
repeatNs =  [5, 6, 7]
# how many time each rule should be repeated (MUST BE multiple of 3 to match with repeat counts!)
rulerepeats = 3
# how many time each repetition count gets repeated within a rule <- 
# MUST BE rulerepeats / 3 (as there are 3 rules per rule category)
reprepeats = rulerepeats / 3

setDlg = NewDlg.NewDlg( title='Set Params' )
setDlg.addField('Stimulus Path:', width=40)
setDlg.addField('Rule repeats (multiple of 3!):', rulerepeats)
setDlg.show()
if setDlg.OK:
    setpath = setDlg.data[0] #'.\\stims\\letters\\'
    rulerepeats = int(setDlg.data[1])
    reprepeats = rulerepeats / 3

# PATH CHECKING & SHAPING
thispth=os.path.realpath(__file__)
root=string.find(setpath, thispth)
while root == -1:
    thispth=thispth[0:len(thispth)-1]
    root=string.find(setpath, thispth)
setpath = string.replace(setpath, thispth, '')

pl=len(setpath)
if setpath[pl-1] != s:
    setpath = setpath + s

if setpath[0] != '.':
    if setpath[0] != s:
        setpath = '.' + s + setpath
    else:
        setpath = '.' + setpath

if not os.path.exists(setpath):
    setpath = '.' + setpath
    if not os.path.exists(setpath):
        print 'FAILED TO FIND STIMULUS PATH - ' + setpath
        exit()

# CONTROLLED RANDOMISATION OF TRIALS
def randomize_carefully(elems, n_repeat=2):
    s = set(elems)
    res = []
    for n in range(n_repeat):
        if res:
            # Avoid the last placed element
            lst = list(s.difference({res[-1]}))
            # Shuffle
            random.shuffle(lst)
            lst.append(res[-1])
            # Shuffle once more to avoid obvious repeating patterns in the last position
            lst[1:] = random.sample(lst[1:], len(lst)-1)
        else:
            lst = elems[:]
            random.shuffle(lst)
        res.extend(lst)
    return res

rows = []

ruleset = randomize_carefully( rules, rulerepeats)

reps = []
reps.append( [] ) #per rule repeats
reps.append( [] )
reps.append( [] )
reps.append( [] )

for i in range(reprepeats):
    reps[0].append(repeatNs[0])
    reps[0].append(repeatNs[1])
    reps[0].append(repeatNs[2])

    reps[1].append(repeatNs[0])
    reps[1].append(repeatNs[1])
    reps[1].append(repeatNs[2])
        
    reps[2].append(repeatNs[0])
    reps[2].append(repeatNs[1])
    reps[2].append(repeatNs[2])

    reps[3].append(repeatNs[0])
    reps[3].append(repeatNs[1])
    reps[3].append(repeatNs[2])

for i in range( len( reps ) ):
    reps[i] = sorted(reps[i], key = lambda *args: random.random() )

for item in ruleset:
    print item
    rows.append( (item, reps[item].pop()) )

print rows

#json generation
data = {'set': {'stimpath': setpath, 'segments':[]}}

for i in rows:
    data['set']['segments'].append( {'rule': i[0], 'reps': i[1]} )

jsontext = json.dumps(data)

print jsontext

saveFile = gui.fileSaveDlg(initFilePath='.'+s+'configs'+s+'sets'+s, allowed='JSON | .json' )
if saveFile:
   sf = open( saveFile, 'w' )
   sf.write( jsontext )
   sf.close()
   