from django.contrib.auth.backends import ModelBackend
import re
from users.models import User


class UserUtils(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断是否是后台的登录请求 request为空说明是后台登录
        if request is None:
            #  如果是判断账户是否是管理员
            try:
                user = User.objects.get(username=username,is_staff=True)
            except:
                user =None

            if user is not None and user.check_password(password):
                return user
        else:
            # 1、判断username是用户名还是手机号
            try:
                if re.match(r'1[3-9]\d{9}', username):
                    # 匹配到username接收到的是手机号数据
                    user = User.objects.get(mobile=username)
                else:
                    # 匹配到username接收到的是用户名数据
                    user = User.objects.get(username=username)
            except:
                user = None

            # 2、查询到对象则校验密码是否正确
            if user is not None and user.check_password(password):
                return user


