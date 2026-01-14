"""
序列化器模块
"""
from rest_framework import serializers
from .models import City, DataCenter, Host, HostPassword, HostStatistics


class CitySerializer(serializers.ModelSerializer):
    """城市序列化器"""
    class Meta:
        model = City
        fields = ['id', 'name', 'code', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DataCenterSerializer(serializers.ModelSerializer):
    """机房序列化器"""
    city_name = serializers.CharField(source='city.name', read_only=True)
    city_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = DataCenter
        fields = ['id', 'name', 'code', 'city', 'city_id', 'city_name', 'address', 
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_city_id(self, value):
        """验证城市ID是否存在"""
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("城市不存在")
        return value

    def create(self, validated_data):
        city_id = validated_data.pop('city_id')
        city = City.objects.get(id=city_id)
        validated_data['city'] = city
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'city_id' in validated_data:
            city_id = validated_data.pop('city_id')
            city = City.objects.get(id=city_id)
            validated_data['city'] = city
        return super().update(instance, validated_data)


class HostSerializer(serializers.ModelSerializer):
    """主机序列化器"""
    city_name = serializers.CharField(source='city.name', read_only=True)
    data_center_name = serializers.CharField(source='data_center.name', read_only=True)
    city_id = serializers.IntegerField(write_only=True)
    data_center_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Host
        fields = ['id', 'hostname', 'ip_address', 'city', 'city_id', 'city_name',
                  'data_center', 'data_center_id', 'data_center_name', 'status',
                  'os_type', 'cpu_cores', 'memory_gb', 'disk_gb', 'description',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_city_id(self, value):
        """验证城市ID是否存在"""
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("城市不存在")
        return value

    def validate_data_center_id(self, value):
        """验证机房ID是否存在"""
        if not DataCenter.objects.filter(id=value).exists():
            raise serializers.ValidationError("机房不存在")
        return value

    def validate(self, attrs):
        """验证城市和机房的关联关系"""
        city_id = attrs.get('city_id')
        data_center_id = attrs.get('data_center_id')
        
        if city_id and data_center_id:
            data_center = DataCenter.objects.get(id=data_center_id)
            if data_center.city_id != city_id:
                raise serializers.ValidationError("机房必须属于指定的城市")
        
        return attrs

    def create(self, validated_data):
        city_id = validated_data.pop('city_id')
        data_center_id = validated_data.pop('data_center_id')
        city = City.objects.get(id=city_id)
        data_center = DataCenter.objects.get(id=data_center_id)
        
        if data_center.city_id != city.id:
            raise serializers.ValidationError("机房必须属于指定的城市")
        
        validated_data['city'] = city
        validated_data['data_center'] = data_center
        return super().create(validated_data)

    def update(self, instance, validated_data):
        city_id = validated_data.pop('city_id', None)
        data_center_id = validated_data.pop('data_center_id', None)
        
        if city_id:
            city = City.objects.get(id=city_id)
            validated_data['city'] = city
        
        if data_center_id:
            data_center = DataCenter.objects.get(id=data_center_id)
            if city_id and data_center.city_id != city_id:
                raise serializers.ValidationError("机房必须属于指定的城市")
            validated_data['data_center'] = data_center
        
        return super().update(instance, validated_data)


class HostPasswordSerializer(serializers.ModelSerializer):
    """主机密码序列化器（不返回实际密码）"""
    hostname = serializers.CharField(source='host.hostname', read_only=True)

    class Meta:
        model = HostPassword
        fields = ['id', 'host', 'hostname', 'password_changed_at', 'created_at']
        read_only_fields = ['encrypted_password', 'password_changed_at', 'created_at']


class HostStatisticsSerializer(serializers.ModelSerializer):
    """主机统计序列化器"""
    city_name = serializers.CharField(source='city.name', read_only=True)
    data_center_name = serializers.CharField(source='data_center.name', read_only=True)

    class Meta:
        model = HostStatistics
        fields = ['id', 'city', 'city_name', 'data_center', 'data_center_name',
                  'host_count', 'active_host_count', 'statistics_date', 'created_at']
        read_only_fields = ['created_at']

