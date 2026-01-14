"""
API视图模块
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from host_management.models import City, DataCenter, Host, HostPassword, HostStatistics
from host_management.serializers import (
    CitySerializer, DataCenterSerializer, HostSerializer,
    HostPasswordSerializer, HostStatisticsSerializer
)
from host_management.utils import ping_host


class CityViewSet(viewsets.ModelViewSet):
    """城市视图集"""
    queryset = City.objects.all()
    serializer_class = CitySerializer


class DataCenterViewSet(viewsets.ModelViewSet):
    """机房视图集"""
    queryset = DataCenter.objects.all()
    serializer_class = DataCenterSerializer

    def get_queryset(self):
        """支持按城市过滤"""
        queryset = DataCenter.objects.all()
        city_id = self.request.query_params.get('city_id', None)
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset


class HostViewSet(viewsets.ModelViewSet):
    """主机视图集"""
    queryset = Host.objects.all()
    serializer_class = HostSerializer

    def get_queryset(self):
        """支持按城市和机房过滤"""
        queryset = Host.objects.all()
        city_id = self.request.query_params.get('city_id', None)
        data_center_id = self.request.query_params.get('data_center_id', None)
        status_filter = self.request.query_params.get('status', None)
        
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if data_center_id:
            queryset = queryset.filter(data_center_id=data_center_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    @action(detail=True, methods=['get'])
    def ping(self, request, pk=None):
        """探测主机是否ping可达"""
        host = self.get_object()
        result = ping_host(host.ip_address)
        
        return Response({
            'host_id': host.id,
            'hostname': host.hostname,
            'ip_address': host.ip_address,
            'reachable': result['reachable'],
            'response_time_ms': result.get('response_time'),
            'error': result.get('error')
        })


class HostPasswordViewSet(viewsets.ReadOnlyModelViewSet):
    """主机密码视图集（只读，密码不返回）"""
    queryset = HostPassword.objects.all()
    serializer_class = HostPasswordSerializer


class HostStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """主机统计视图集（只读）"""
    queryset = HostStatistics.objects.all()
    serializer_class = HostStatisticsSerializer

    def get_queryset(self):
        """支持按日期、城市、机房过滤"""
        queryset = HostStatistics.objects.all()
        city_id = self.request.query_params.get('city_id', None)
        data_center_id = self.request.query_params.get('data_center_id', None)
        statistics_date = self.request.query_params.get('statistics_date', None)
        
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if data_center_id:
            queryset = queryset.filter(data_center_id=data_center_id)
        if statistics_date:
            queryset = queryset.filter(statistics_date=statistics_date)
        
        return queryset

