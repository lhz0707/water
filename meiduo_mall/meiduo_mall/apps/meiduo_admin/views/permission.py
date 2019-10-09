from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.permission import PermissionSerializer, ContentTypeSerializer
from meiduo_admin.utils import PageNum
from django.contrib.auth.models import Permission, ContentType


class PermissionView(ModelViewSet):
    # 指定序列化器
    serializer_class = PermissionSerializer
    # 指定数据的查询集
    queryset = Permission.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 获取权限类型
    def content_types(self, request):
        # 1、查询获取所有的权限类型
        data = ContentType.objects.all()
        # 2、序列化返回权限类型
        ser=ContentTypeSerializer(data,many=True)
        return Response(ser.data)

