from rest_framework import serializers

from goods.models import SpecificationOption


class SpecificationOptionSerializer(serializers.ModelSerializer):
    # 嵌套序列化返回
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()

    class Meta:
        # 指定模型类
        model = SpecificationOption
        # 指定字段
        fields = '__all__'
