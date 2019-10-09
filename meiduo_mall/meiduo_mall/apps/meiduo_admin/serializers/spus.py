from rest_framework import serializers

from goods.models import SPU


class SPUSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField(read_only=True)
    category1 = serializers.StringRelatedField(read_only=True)
    category2 = serializers.StringRelatedField(read_only=True)
    category3 = serializers.StringRelatedField(read_only=True)

    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()
    class Meta:
        # 指定模型类
        model = SPU
        # 指定字段
        fields = '__all__'
