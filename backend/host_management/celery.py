"""
Celery配置模块
"""
import os
from celery import Celery

# 设置Django默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('host_management')

# 从Django设置中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks([
    "host_management.celery_tasks",
])

