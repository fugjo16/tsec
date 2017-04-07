@echo off
REM !/bin/bash
REM cd /home/asoul/tsec/

REM del /Q data

REM python crawl.py --check 2017 04 01
python crawl.py --back
python post_process.py
echo.
python analyze.py

pause

REM /usr/bin/git add .
REM /usr/bin/git commit -m "daily update"
REM /usr/bin/git push
REM /usr/bin/git fetch --depth=1
REM /usr/bin/git reflog expire --expire-unreachable=now --all
REM /usr/bin/git gc --aggressive --prune=all