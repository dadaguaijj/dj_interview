"""
Celery定时任务模块
"""
from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta
from .models import Host, HostPassword, HostStatistics, City, DataCenter
from .utils import generate_random_password
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_host_passwords():
    """
    每隔8小时随机修改每台主机的密码并加密记录
    """
    try:
        hosts = Host.objects.all()
        updated_count = 0
        
        for host in hosts:
            try:
                # 生成新密码
                new_password = generate_random_password(length=16)
                
                # 获取或创建密码记录
                password_record, created = HostPassword.objects.get_or_create(
                    host=host,
                    defaults={'encrypted_password': ''}
                )
                
                # 设置新密码（会自动加密）
                password_record.set_password(new_password)
                updated_count += 1
                
                logger.info(f"已更新主机 {host.hostname} 的密码")
            except Exception as e:
                logger.error(f"更新主机 {host.hostname} 密码失败: {str(e)}")
                continue
        
        logger.info(f"密码更新任务完成，共更新 {updated_count} 台主机")
        return f"成功更新 {updated_count} 台主机的密码"
    except Exception as e:
        logger.error(f"密码更新任务执行失败: {str(e)}")
        raise


@shared_task
def generate_host_statistics():
    """
    每天00:00按城市和机房维度统计主机数量，并把统计数据写入数据库
    """
    try:
        today = date.today()
        
        # 获取所有城市和机房的组合
        cities = City.objects.all()
        
        for city in cities:
            data_centers = DataCenter.objects.filter(city=city)
            
            for data_center in data_centers:
                # 统计该城市和机房的主机数量
                total_hosts = Host.objects.filter(
                    city=city,
                    data_center=data_center
                ).count()
                
                active_hosts = Host.objects.filter(
                    city=city,
                    data_center=data_center,
                    status='active'
                ).count()
                
                # 创建或更新统计记录
                statistics, created = HostStatistics.objects.update_or_create(
                    city=city,
                    data_center=data_center,
                    statistics_date=today,
                    defaults={
                        'host_count': total_hosts,
                        'active_host_count': active_hosts
                    }
                )
                
                logger.info(
                    f"统计完成: {city.name}-{data_center.name} "
                    f"总主机数: {total_hosts}, 运行中: {active_hosts}"
                )
        
        logger.info(f"主机统计任务完成，统计日期: {today}")
        return f"成功生成 {today} 的主机统计数据"
    except Exception as e:
        logger.error(f"主机统计任务执行失败: {str(e)}")
        raise

