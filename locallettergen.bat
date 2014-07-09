@echo off
set pth=C:\Users\admin\OneDrive\ReKnow\PsychoPhysiology\experiment\code
set py="C:\Program Files (x86)\PsychoPy2\python.exe"

REM do the local letters for all clusters of global faces, letters, across two preprocessing modes, four colors, with four orientations
for %%c in (0,1,2) do (
 for %%g in (0,1) do (
  for %%f in (0,1) do (
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
REM do the local letters' global noise
for %%c in (0) do (
 for %%g in (2) do (
  for %%f in (0) do (
   for %%i in (0) do (
    for %%j in (0) do (
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