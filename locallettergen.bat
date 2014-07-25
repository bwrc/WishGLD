@echo off
set pth=C:\Users\admin\OneDrive\ReKnow\PsychoPhysiology\experiment\code
set py="C:\Program Files (x86)\PsychoPy2\python.exe"

REM do the local letters for 
REM g = of global faces, letters 
REM c = given clusters
REM f = preprocessing filters
REM four globals, four colors, locals; with four orientations inbuilt
REM for %%g in (0,1) do (
 REM for %%c in (0,1,2,3) do (
  REM for %%f in (0,1) do (
   REM for %%i in (0,1,2,3) do (
    REM for %%j in (0,1,2,3) do (
	 REM for %%k in (0,1,2,3) do (
	  REM %py% halftone_localletters_param.py %%g %%c %%f %%i %%j %%k
	 REM )
	REM )
   REM )
  REM )
 REM )
REM )
REM do some specific full sets
for %%i in (0,1,2,3) do (
 for %%j in (0,1,2,3) do (
  for %%k in (0) do (
   %py% halftone_localletters_param.py 0 3 0 %%i %%j %%k
  )
 )
)
for %%i in (0,1,2,3) do (
 for %%j in (0,1,2,3) do (
  for %%k in (0) do (
   %py% halftone_localletters_param.py 1 1 1 %%i %%j %%k
  )
 )
)
REM do the local letters' global noise -------------------------------------------
REM for %%g in (2) do (
 REM for %%c in (1) do (
  REM for %%f in (0) do (
   REM for %%i in (0) do (
    REM for %%j in (0) do (
	 REM for %%k in (0) do (
	  REM REM echo %%g %%c %%f %%i %%j %%k
	  REM %py% halftone_localletters_param.py %%g %%c %%f %%i %%j %%k
	  REM REM pause
	 REM )
	REM )
   REM )
  REM )
 REM )
REM )

REM do the local shapes' all globals ----------------------------------------------
REM %py% halftone_localshapes_gen.py

REM for %%i in (0,1,2,3) do (
 REM for %%l in (0,1,2,3) do (
	REM %py% halftone_localletters_param.py 1 0 0 %%i 0 %%l
 REM )
REM )
pause