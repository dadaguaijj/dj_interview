"""
工具函数模块
"""
import subprocess
import platform
import random
import string


def ping_host(ip_address, timeout=3):
    """
    探测主机是否ping可达
    
    Args:
        ip_address: IP地址
        timeout: 超时时间（秒）
    
    Returns:
        dict: {'reachable': bool, 'response_time': float or None}
    """
    try:
        # 根据操作系统选择ping命令
        if platform.system().lower() == 'windows':
            # Windows系统
            cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), ip_address]
        else:
            # Linux/Mac系统
            cmd = ['ping', '-c', '1', '-W', str(timeout), ip_address]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout + 1
        )
        
        # 检查返回码，0表示成功
        if result.returncode == 0:
            # 尝试从输出中提取响应时间（可选）
            output = result.stdout.decode('utf-8', errors='ignore')
            response_time = None
            
            # Windows格式: "时间<1ms" 或 "时间=10ms"
            # Linux格式: "time=10.123 ms"
            if 'ms' in output.lower():
                import re
                time_match = re.search(r'(\d+(?:\.\d+)?)\s*ms', output, re.IGNORECASE)
                if time_match:
                    response_time = float(time_match.group(1))
            
            return {
                'reachable': True,
                'response_time': response_time
            }
        else:
            return {
                'reachable': False,
                'response_time': None
            }
    except subprocess.TimeoutExpired:
        return {
            'reachable': False,
            'response_time': None
        }
    except Exception as e:
        return {
            'reachable': False,
            'response_time': None,
            'error': str(e)
        }


def generate_random_password(length=16):
    """
    生成随机密码
    
    Args:
        length: 密码长度
    
    Returns:
        str: 随机密码
    """
    # 包含大小写字母、数字和特殊字符
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

