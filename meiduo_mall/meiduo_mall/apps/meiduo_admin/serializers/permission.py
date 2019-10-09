from rest_framework import serializers
from django.contrib.auth.models import Permission,ContentType

class PermissionSerializer(serializers.ModelSerializer):
    """
              权限表序列化器
    """

    class Meta:
        # 指定模型类
        model = Permission
        # 指定字段
        fields = '__all__'

class ContentTypeSerializer(serializers.ModelSerializer):
    """
        权限类型表序列化器
    """

    class Meta:
        # 指定模型类
        model = ContentType
        # 指定字段
        fields = ('id','name')

