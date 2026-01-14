"""
生成测试数据的管理命令
使用方法: python manage.py generate_test_data
"""
from django.core.management.base import BaseCommand
from host_management.models import City, DataCenter, Host
import random


class Command(BaseCommand):
    help = '生成测试数据：创建城市、机房和主机'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hosts',
            type=int,
            default=10,
            help='要生成的主机数量（默认：10）',
        )
        parser.add_argument(
            '--cities',
            type=int,
            default=3,
            help='要生成的城市数量（默认：3）',
        )
        parser.add_argument(
            '--data-centers',
            type=int,
            default=2,
            help='每个城市要生成的机房数量（默认：2）',
        )

    def handle(self, *args, **options):
        hosts_count = options['hosts']
        cities_count = options['cities']
        data_centers_per_city = options['data_centers']

        self.stdout.write(self.style.SUCCESS('开始生成测试数据...'))

        # 城市数据
        city_names = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安']
        city_codes = ['BJ', 'SH', 'GZ', 'SZ', 'HZ', 'CD', 'WH', 'XA']

        # 创建城市
        cities = []
        for i in range(min(cities_count, len(city_names))):
            city_name = city_names[i]
            city_code = city_codes[i]
            
            city, created = City.objects.get_or_create(
                code=city_code,
                defaults={
                    'name': city_name,
                    'description': f'{city_name}市'
                }
            )
            cities.append(city)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ 创建城市: {city_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  城市已存在: {city_name}'))

        # 创建机房
        data_centers = []
        for city in cities:
            for j in range(data_centers_per_city):
                dc_name = f'{city.name}机房{j+1}'
                dc_code = f'{city.code}-DC{j+1}'
                
                dc, created = DataCenter.objects.get_or_create(
                    code=dc_code,
                    defaults={
                        'name': dc_name,
                        'city': city,
                        'address': f'{city.name}市某区某街道{j+1}号',
                        'description': f'{city.name}的机房{j+1}'
                    }
                )
                data_centers.append(dc)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ 创建机房: {dc_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  机房已存在: {dc_name}'))

        # 创建主机
        os_types = ['Linux', 'Windows Server', 'CentOS', 'Ubuntu']
        statuses = ['active', 'active', 'active', 'inactive', 'maintenance']  # 大部分是active
        
        created_hosts = 0
        for i in range(hosts_count):
            # 随机选择机房
            data_center = random.choice(data_centers)
            city = data_center.city
            
            # 生成主机名
            hostname = f'host-{city.code.lower()}-{data_center.code.split("-")[-1].lower()}-{str(i+1).zfill(3)}'
            
            # 生成IP地址（使用私有IP段）
            ip_octets = [
                random.choice([192, 10, 172]),
                random.randint(1, 255),
                random.randint(1, 255),
                random.randint(1, 254)
            ]
            ip_address = '.'.join(map(str, ip_octets))
            
            # 检查主机名和IP是否已存在
            if Host.objects.filter(hostname=hostname).exists():
                self.stdout.write(self.style.WARNING(f'  主机名已存在，跳过: {hostname}'))
                continue
            
            if Host.objects.filter(ip_address=ip_address).exists():
                # 如果IP已存在，生成新的
                ip_octets[3] = random.randint(1, 254)
                ip_address = '.'.join(map(str, ip_octets))
            
            # 创建主机
            host = Host.objects.create(
                hostname=hostname,
                ip_address=ip_address,
                city=city,
                data_center=data_center,
                status=random.choice(statuses),
                os_type=random.choice(os_types),
                cpu_cores=random.choice([2, 4, 8, 16]),
                memory_gb=random.choice([4, 8, 16, 32]),
                disk_gb=random.choice([50, 100, 200, 500]),
                description=f'测试主机 {i+1}'
            )
            created_hosts += 1
            self.stdout.write(self.style.SUCCESS(
                f'✓ 创建主机: {hostname} ({ip_address}) - {city.name}/{data_center.name}'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'\n生成完成！\n'
            f'  城市: {len(cities)} 个\n'
            f'  机房: {len(data_centers)} 个\n'
            f'  主机: {created_hosts} 个'
        ))

