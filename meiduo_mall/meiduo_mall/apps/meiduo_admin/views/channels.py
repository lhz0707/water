from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.channels import GoodsChannelSerializer, GoodsChannelGroupSerializer
from meiduo_admin.serializers.options import SpecificationOptionSerializer
from meiduo_admin.serializers.skus import GoodsCategorySerializer
from meiduo_admin.utils import PageNum
from goods.models import GoodsChannel, GoodsChannelGroup,GoodsCategory


class GoodsChannelView(ModelViewSet):
    """
        商品频道表增删改查
    """
    # 指定序列化器
    serializer_class = GoodsChannelSerializer
    # 指定数据的查询集
    queryset = GoodsChannel.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 获取频道分组
    def simple(self, request):
        data = GoodsChannelGroup.objects.all()
        ser = GoodsChannelGroupSerializer(data, many=True)
        return Response(ser.data)

    # 获取一级分类
    def category(self, request):
        data = GoodsCategory.objects.filter(parent=None)
        ser = GoodsCategorySerializer(data, many=True)
        return Response(ser.data)