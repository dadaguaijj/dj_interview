"""
主机管理系统模型
"""
from django.db import models
from django.utils import timezone
from django.core.validators import validate_ipv4_address
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os


class City(models.Model):
    """城市模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name="城市名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="城市代码")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "城市"
        verbose_name_plural = "城市"
        ordering = ['name']

    def __str__(self):
        return self.name


class DataCenter(models.Model):
    """机房模型"""
    name = models.CharField(max_length=100, verbose_name="机房名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="机房代码")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='data_centers', verbose_name="所属城市")
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name="地址")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "机房"
        verbose_name_plural = "机房"
        ordering = ['city', 'name']
        unique_together = [['city', 'name']]

    def __str__(self):
        return f"{self.city.name}-{self.name}"


class Host(models.Model):
    """主机模型"""
    STATUS_CHOICES = [
        ('active', '运行中'),
        ('inactive', '已停止'),
        ('maintenance', '维护中'),
    ]

    hostname = models.CharField(max_length=100, unique=True, verbose_name="主机名")
    ip_address = models.GenericIPAddressField(protocol='IPv4', verbose_name="IP地址")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hosts', verbose_name="所属城市")
    data_center = models.ForeignKey(DataCenter, on_delete=models.CASCADE, related_name='hosts', verbose_name="所属机房")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="状态")
    os_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="操作系统类型")
    cpu_cores = models.IntegerField(default=0, verbose_name="CPU核心数")
    memory_gb = models.IntegerField(default=0, verbose_name="内存(GB)")
    disk_gb = models.IntegerField(default=0, verbose_name="磁盘(GB)")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "主机"
        verbose_name_plural = "主机"
        ordering = ['hostname']

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"


class HostPassword(models.Model):
    """主机密码记录模型（加密存储）"""
    host = models.OneToOneField(Host, on_delete=models.CASCADE, related_name='password_record', verbose_name="主机")
    encrypted_password = models.TextField(verbose_name="加密后的密码")
    password_changed_at = models.DateTimeField(auto_now=True, verbose_name="密码修改时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "主机密码"
        verbose_name_plural = "主机密码"

    def __str__(self):
        return f"{self.host.hostname} 密码记录"

    @staticmethod
    def get_encryption_key():
        """获取加密密钥"""
        from django.core.cache import cache
        
        # 先从环境变量获取
        key = os.environ.get('ENCRYPTION_KEY')
        
        # 如果环境变量没有，从settings获取
        if not key:
            key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        # 如果都没有，生成并缓存（仅开发环境）
        if not key:
            cache_key = 'host_management_encryption_key'
            key = cache.get(cache_key)
            if not key:
                key = Fernet.generate_key().decode()
                cache.set(cache_key, key, timeout=None)  # 永久缓存
        
        if isinstance(key, str):
            key = key.encode()
        return key

    def encrypt_password(self, password):
        """加密密码"""
        key = self.get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(password.encode())
        return encrypted.decode()

    def decrypt_password(self):
        """解密密码"""
        key = self.get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(self.encrypted_password.encode())
        return decrypted.decode()

    def set_password(self, password):
        """设置密码（自动加密）"""
        self.encrypted_password = self.encrypt_password(password)
        self.save()

    def get_password(self):
        """获取密码（自动解密）"""
        return self.decrypt_password()


class HostStatistics(models.Model):
    """主机统计模型（按城市和机房维度）"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='statistics', verbose_name="城市")
    data_center = models.ForeignKey(DataCenter, on_delete=models.CASCADE, related_name='statistics', verbose_name="机房")
    host_count = models.IntegerField(default=0, verbose_name="主机数量")
    active_host_count = models.IntegerField(default=0, verbose_name="运行中主机数量")
    statistics_date = models.DateField(verbose_name="统计日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "主机统计"
        verbose_name_plural = "主机统计"
        ordering = ['-statistics_date', 'city', 'data_center']
        unique_together = [['city', 'data_center', 'statistics_date']]

    def __str__(self):
        return f"{self.city.name}-{self.data_center.name} ({self.statistics_date}): {self.host_count}台"


class RequestLog(models.Model):
    """请求日志模型（用于记录请求耗时）"""
    path = models.CharField(max_length=500, verbose_name="请求路径")
    method = models.CharField(max_length=10, verbose_name="请求方法")
    status_code = models.IntegerField(verbose_name="状态码")
    duration_ms = models.FloatField(verbose_name="耗时(毫秒)")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="客户端IP")
    user_agent = models.CharField(max_length=500, blank=True, null=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "请求日志"
        verbose_name_plural = "请求日志"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['path', 'method']),
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.duration_ms}ms ({self.created_at})"
