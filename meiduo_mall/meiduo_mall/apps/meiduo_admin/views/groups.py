from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.groups import GroupSerializer
from meiduo_admin.serializers.permission import PermissionSerializer
from meiduo_admin.utils import PageNum
from django.contrib.auth.models import Group,Permission


class GroupView(ModelViewSet):
    # 指定序列化器
    serializer_class = GroupSerializer
    # 指定数据的查询集
    queryset = Group.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum


    # 获取权限信息
    def simple(self,reqeust):
        # 1、获取权限表数据
        data=Permission.objects.all()
        # 2、序列化返回数据
        ser=PermissionSerializer(data,many=True)
        return Response(ser.data)


