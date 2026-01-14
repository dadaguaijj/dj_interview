"""
API路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CityViewSet, DataCenterViewSet, HostViewSet,
    HostPasswordViewSet, HostStatisticsViewSet
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'data-centers', DataCenterViewSet, basename='datacenter')
router.register(r'hosts', HostViewSet, basename='host')
router.register(r'host-passwords', HostPasswordViewSet, basename='hostpassword')
router.register(r'statistics', HostStatisticsViewSet, basename='statistics')

urlpatterns = [
    path('api/', include(router.urls)),
]

