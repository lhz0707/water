from rest_framework.generics import ListAPIView,CreateAPIView,ListCreateAPIView
from rest_framework.permissions import IsAdminUser

from meiduo_admin.serializers.users import UsersSerializer
from meiduo_admin.utils import PageNum
from users.models import User

class UsersView(ListCreateAPIView):

    # 指定序列化器
    serializer_class = UsersSerializer
    # 指定数据的查询集
    # queryset = User.objects.filter(is_staff=False)
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 通过判断keyword参数返回不同的查询集数据
    def get_queryset(self):
        # 1、获取keyword 查询字符串
        keyword=self.request.query_params.get('keyword')
        if keyword is None or keyword == '':
            return User.objects.filter(is_staff=False)
        else:
            return User.objects.filter(is_staff=False,username__contains=keyword)





