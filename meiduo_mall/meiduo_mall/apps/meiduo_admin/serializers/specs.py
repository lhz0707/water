from rest_framework import serializers
from goods.models import SPUSpecification, SPU


class SPUSpecificationSerializer(serializers.ModelSerializer):
    # 关联嵌套序列化返回
    # 返回关联字段名称
    spu = serializers.StringRelatedField()
    # 根据数据表中的返回关联字段id值
    spu_id = serializers.IntegerField()

    class Meta:
        # 指定模型类
        model = SPUSpecification
        # 指定字段
        fields = ('id', 'name','spu','spu_id')


class SPUSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定模型类
        model = SPU
        # 指定字段
        fields = ('id', 'name')
