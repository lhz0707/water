from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.images import SKUImageSerializer, SKUSerializer
from meiduo_admin.utils import PageNum
from goods.models import SKUImage, SKU


class ImageView(ModelViewSet):
    """
        图片表增删改查
    """
    # 指定序列化器
    serializer_class = SKUImageSerializer
    # 指定数据的查询集
    queryset = SKUImage.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 获取sku表信息数据
    def simple(self,request):
        # 1、获取所有sku信息
        skus = SKU.objects.all()
        # 2、返回sku信息
        ser = SKUSerializer(skus, many=True)
        return Response(ser.data)



