"""
Celery配置文件
用于独立运行Celery worker和beat
"""
from celery.schedules import crontab

# Broker配置
broker_url = 'redis://localhost:6379/0'

# Result backend配置
result_backend = 'redis://localhost:6379/0'

# 时区配置
timezone = 'Asia/Shanghai'

# 任务序列化格式
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# 定时任务配置
beat_schedule = {
    'update-host-passwords-every-8-hours': {
        'task': 'host_management.celery_tasks.update_host_passwords',
        'schedule': 28800.0,  # 每8小时执行一次
    },
    'generate-host-statistics-daily-at-midnight': {
        'task': 'host_management.celery_tasks.generate_host_statistics',
        'schedule': crontab(hour=0, minute=0),  # 每天00:00执行
    },
}

