@echo off    
start cmd /k "cd /d %~dp0&&py -3 manage.py makemigrations&&py -3 manage.py migrate&&exit"

