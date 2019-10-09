from rest_framework import serializers
from django.contrib.auth.models import Group

class GroupSerializer(serializers.ModelSerializer):
    """
              分组表序列化器
    """

    class Meta:
        # 指定模型类
        model = Group
        # 指定字段
        fields = '__all__'
