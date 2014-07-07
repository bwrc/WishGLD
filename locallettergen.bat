@echo off
set pth=C:\Users\admin\OneDrive\ReKnow\PsychoPhysiology\experiment\code
set py="C:\Program Files (x86)\PsychoPy2\python.exe"
REM set glob=0
REM set clst=0
REM set filt=0
REM set "param=00_00_00 00_00_01 00_00_02 00_00_03 00_01_00 00_01_01 00_01_02 00_01_03 00_02_00 00_02_01 00_02_02 00_02_03 00_03_00 00_03_01 00_03_02 00_03_03 01_00_00 01_00_01 01_00_02 01_00_03 01_01_00 01_01_01 01_01_02 01_01_03 01_02_00 01_02_01 01_02_02 01_02_03 01_03_00 01_03_01 01_03_02 01_03_03 02_00_00 02_00_01 02_00_02 02_00_03 02_01_00 02_01_01 02_01_02 02_01_03 02_02_00 02_02_01 02_02_02 02_02_03 02_03_00 02_03_01 02_03_02 02_03_03 03_00_00 03_00_01 03_00_02 03_00_03 03_01_00 03_01_01 03_01_02 03_01_03 03_02_00 03_02_01 03_02_02 03_02_03 03_03_00 03_03_01 03_03_02 03_03_03"
REM for %%i in (%param%) do (
 REM echo %glob%
 REM echo %clst%
 REM echo %filt%
 REM echo %%i
 REM %py% %pth%\halftone_localletters_param.py %glob% %clst% %filt% %%i
 REM pause
REM )

for %%c in (0,1) do (
 for %%g in (2) do (
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