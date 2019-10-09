from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.specs import SPUSpecificationSerializer, SPUSerializer
from meiduo_admin.utils import PageNum
from goods.models import SPUSpecification, SPU


class SpecView(ModelViewSet):
    """
        规格表增删改查
    """
    # 指定序列化器
    serializer_class = SPUSpecificationSerializer
    # 指定数据的查询集
    queryset = SPUSpecification.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 获取spu信息
    def simple(self, request):
        # 1、获取所有spu信息
        spus = SPU.objects.all()
        # 2、返回spu信息
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)
