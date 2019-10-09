from rest_framework import serializers

from goods.models import GoodsChannel,GoodsChannelGroup


class GoodsChannelSerializer(serializers.ModelSerializer):
    # 嵌套序列化返回
    group=serializers.StringRelatedField(read_only=True)
    category=serializers.StringRelatedField(read_only=True)
    group_id=serializers.IntegerField()
    category_id=serializers.IntegerField()
    class Meta:
        # 指定模型类
        model = GoodsChannel
        # 指定字段
        fields = '__all__'


class GoodsChannelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        # 指定模型类
        model = GoodsChannelGroup
        # 指定字段
        fields = '__all__'
