"""
中间件模块 - 统计请求耗时
"""
import time
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog


class RequestTimingMiddleware(MiddlewareMixin):
    """
    请求耗时统计中间件
    记录每个请求的路径、方法、状态码、耗时等信息
    """
    
    def process_request(self, request):
        """请求开始时记录时间"""
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        """请求结束时计算耗时并记录"""
        if hasattr(request, '_start_time'):
            duration = (time.time() - request._start_time) * 1000  # 转换为毫秒
            
            # 获取客户端IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # 获取User Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            # 记录请求日志（异步保存，避免影响响应时间）
            try:
                RequestLog.objects.create(
                    path=request.path[:500],
                    method=request.method,
                    status_code=response.status_code,
                    duration_ms=duration,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            except Exception as e:
                # 记录日志失败不应该影响正常响应
                # 在生产环境中应该使用日志系统记录错误
                pass
        
        return response

