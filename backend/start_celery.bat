@echo off
echo Starting Celery Worker...
start "Celery Worker" celery -A host_management worker -l info

echo Starting Celery Beat...
start "Celery Beat" celery -A host_management beat -l info

echo Celery services started!
pause

