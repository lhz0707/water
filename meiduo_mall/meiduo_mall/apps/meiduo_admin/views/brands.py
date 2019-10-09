from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.brands import BrandSerializer
from meiduo_admin.utils import PageNum
from goods.models import Brand


class BrandChannelView(ModelViewSet):
    """
        品牌表增删改查
    """
    # 指定序列化器
    serializer_class = BrandSerializer
    # 指定数据的查询集
    queryset = Brand.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum
