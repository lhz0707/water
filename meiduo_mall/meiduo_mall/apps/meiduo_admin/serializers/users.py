from rest_framework import serializers

from users.models import User

import re


class UsersSerializer(serializers.ModelSerializer):
    """
        用户序列化器
    """

    class Meta:
        # 指定模型类
        model = User
        # 指定字段
        fields = ('id', 'username', 'mobile', 'email', 'password')

        # password只参与反序列化 需要指定write_only=True
        # extra_kwargs 给字段增加或修改选项参数
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 5
            },
            'username': {
                'max_length': 20,
                'min_length': 5
            },

        }

    # 验证手机号格式
    def validate_mobile(self, attrs):
        if not re.match(r'1[3-9]\d{9}', attrs):
            raise serializers.ValidationError('手机号格式不正确')

        return attrs

    # 重写保存用户表的操作实现密码的加密
    def create(self, validated_data):
        # 1、调用用父类保存逻辑得到保存后用户对象
        user = super().create(validated_data)
        # 2、使用用户对象完成密码加密
        user.set_password(validated_data['password'])
        user.save()

        return user
