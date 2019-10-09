from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.options import SpecificationOptionSerializer
from meiduo_admin.serializers.specs import SPUSpecificationSerializer, SPUSerializer
from meiduo_admin.utils import PageNum
from goods.models import SPUSpecification, SPU, SpecificationOption


class SpecificationOptionView(ModelViewSet):
    """
        规格选项表增删改查
    """
    # 指定序列化器
    serializer_class = SpecificationOptionSerializer
    # 指定数据的查询集
    queryset = SpecificationOption.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 获取所有的规格信息
    def simple(self, request):
        # 1、查询规格表
        data = SPUSpecification.objects.all()
        # 2、序列化返回规格信息
        ser = SPUSpecificationSerializer(data, many=True)

        return Response(ser.data)
