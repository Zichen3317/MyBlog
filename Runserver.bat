@echo off    
start cmd /k "cd /d %~dp0&&py -3 manage.py runserver"

