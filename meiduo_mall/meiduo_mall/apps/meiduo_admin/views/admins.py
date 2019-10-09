from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.admin import AdminSerializer
from meiduo_admin.serializers.groups import GroupSerializer
from meiduo_admin.utils import PageNum
from django.contrib.auth.models import Group
from users.models import User


class AdminView(ModelViewSet):
    # 指定序列化器
    serializer_class = AdminSerializer
    # 指定数据的查询集
    queryset = User.objects.filter(is_staff=True)
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 获取分组信息
    def groups(self, request):
        # 1、获取所有分组
        data = Group.objects.all()
        # 2、序列化返回分组信息
        ser = GroupSerializer(data, many=True)
        return Response(ser.data)

