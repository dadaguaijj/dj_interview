#!/bin/bash
# 启动Celery Worker和Beat

echo "Starting Celery Worker..."
celery -A host_management worker -l info &
worker_pid=$!

echo "Starting Celery Beat..."
celery -A host_management beat -l info &
beat_pid=$!

echo "Celery services started!"
echo "Worker PID: $worker_pid"
echo "Beat PID: $beat_pid"

