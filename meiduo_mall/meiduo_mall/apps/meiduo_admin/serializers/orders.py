from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class SKUSerialzier(serializers.ModelSerializer):
    """
          SKU商品序列化器
      """

    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """
        订单商品序列化器
    """

    # 嵌套返回sku商品表  子嵌套父表返回
    sku = SKUSerialzier()

    class Meta:
        # 指定模型类
        model = OrderGoods
        # 指定字段
        fields = ('sku', 'price', 'count')


class OrderInfoSerializer(serializers.ModelSerializer):
    """
        订单序列化器
    """

    # 嵌套返回订单商品表  父嵌套子表返回
    skus = OrderGoodsSerializer(many=True)

    class Meta:
        # 指定模型类
        model = OrderInfo
        # 指定字段
        fields = "__all__"
