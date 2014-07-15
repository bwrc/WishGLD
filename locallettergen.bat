@echo off
set pth=C:\Users\admin\OneDrive\ReKnow\PsychoPhysiology\experiment\code
set py="C:\Program Files (x86)\PsychoPy2\python.exe"

REM do the local letters for all clusters of global faces, letters, across two preprocessing modes, four colors, with four orientations
for %%c in (1,2) do (
 for %%g in (1) do (
  for %%f in (0) do (
   for %%i in (0,1,2,3) do (
    for %%j in (0,1,2,3) do (
	 for %%k in (0,1,2,3) do (
	  REM echo %%g %%c %%f %%i %%j %%k
	  %py% halftone_localletters_param.py %%g %%c %%f %%i %%j %%k
	  REM pause
	 )
	)
   )
  )
 )
)
REM %py% halftone_localshapes_gen.py

REM for %%i in (0,1,2,3) do (
 REM for %%l in (0,1,2,3) do (
	REM %py% halftone_localletters_param.py 1 0 0 %%i 0 %%l
 REM )
REM )
pause
REM do the local letters' global noise
REM for %%c in (0) do (
 REM for %%g in (2) do (
  REM for %%f in (0) do (
   REM for %%i in (0) do (
    REM for %%j in (0) do (
	 REM for %%k in (0,1,2,3) do (
	  REM REM echo %%g %%c %%f %%i %%j %%k
	  REM %py% halftone_localletters_param.py %%g %%c %%f %%i %%j %%k
	  REM REM pause
	 REM )
	REM )
   REM )
  REM )
 REM )
REM )