from django.contrib import admin
from .models import City, DataCenter, Host, HostPassword, HostStatistics, RequestLog


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']


@admin.register(DataCenter)
class DataCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'created_at']
    search_fields = ['name', 'code', 'city__name']
    list_filter = ['city', 'created_at']


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'ip_address', 'city', 'data_center', 'status', 'created_at']
    search_fields = ['hostname', 'ip_address']
    list_filter = ['city', 'data_center', 'status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HostPassword)
class HostPasswordAdmin(admin.ModelAdmin):
    list_display = ['host', 'password_changed_at', 'created_at']
    readonly_fields = ['encrypted_password', 'password_changed_at', 'created_at']
    search_fields = ['host__hostname']


@admin.register(HostStatistics)
class HostStatisticsAdmin(admin.ModelAdmin):
    list_display = ['city', 'data_center', 'host_count', 'active_host_count', 'statistics_date']
    list_filter = ['statistics_date', 'city', 'data_center']
    readonly_fields = ['created_at']


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['path', 'method', 'status_code', 'duration_ms', 'created_at']
    list_filter = ['method', 'status_code', 'created_at']
    search_fields = ['path']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
