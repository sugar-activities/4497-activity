@echo off
rem This script builds the Timeline installation executable
rem for the Windows target os.

set TIMELINE_DIR=..\..\..\
set PACKAGE_DIR=..
set ICALENDAR_DIR=%TIMELINE_DIR%\libs\dependencies\icalendar-2.1\icalendar
set PYSVG_DIR=%TIMELINE_DIR%\libs\dependencies\pysvg-0.2.1\pysvg

echo ***. Copying icalendar package to timeline directory.
mkdir %TIMELINE_DIR%\icalendar
copy %ICALENDAR_DIR%\*.*  %TIMELINE_DIR%\icalendar\*.*
pause

echo ***. Copying pysvg package to timeline directory.
mkdir %TIMELINE_DIR%\pysvg
copy %PYSVG_DIR%\*.*  %TIMELINE_DIR%\pysvg\*.*
pause

echo *** Copying setup.py to timeline directory
copy ..\inno\setup.py  %TIMELINE_DIR%\setup.py
pause

echo *** Copying timeline.ico to icons directory
copy ..\inno\Timeline.ico  %TIMELINE_DIR%\icons\Timeline.ico
pause

echo ***. Modifyng timeline.py
python mod_timeline_py.py  > %TIMELINE_DIR%\timeline_tmp.py
del %TIMELINE_DIR%\timeline.py
ren %TIMELINE_DIR%\timeline_tmp.py timeline.py
pause

echo ***. Modifyng paths.py
python mod_paths_py.py  > %TIMELINE_DIR%\timelinelib\config\paths_tmp.py
del %TIMELINE_DIR%\timelinelib\config\paths.py
ren %TIMELINE_DIR%\timelinelib\config\paths_tmp.py paths.py
pause

echo ***. Modifyng timeline.iss
python mod_timeline_iss.py  > ..\inno\timeline_tmp.iss
ren ..\inno\timeline.iss  _timeline.iss
ren ..\inno\timeline_tmp.iss timeline.iss
pause

echo *** Running scons command
pushd %TIMELINE_DIR%
call scons
popd
pause

echo *** Running py2exe
pushd %TIMELINE_DIR%
setup.py py2exe
popd
pause

echo ***. Copying icons to dist directory.
mkdir %TIMELINE_DIR%\dist\icons
copy %TIMELINE_DIR%\icons\*.*  %TIMELINE_DIR%\dist\icons\*.*
pause

echo ***. Copying po to dist directory.
mkdir %TIMELINE_DIR%\dist\po
xcopy %TIMELINE_DIR%\po\*.*  %TIMELINE_DIR%\dist\po\*.* /S
del %TIMELINE_DIR%\dist\po\*.po
del %TIMELINE_DIR%\dist\po\*.pot
pause

echo ***. Compile Inno Std script
pushd  ..\inno
call "%ProgramFiles%\Inno Setup 5\iscc.exe" Timeline.iss
pause

