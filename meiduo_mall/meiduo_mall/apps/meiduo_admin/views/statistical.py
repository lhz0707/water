from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from datetime import date, timedelta
from rest_framework.permissions import IsAdminUser
from goods.models import GoodsVisitCount


class UserTotalCount(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, reqeust):
        """
            获取用户总数
        :param reqeust:
        :return:
        """
        # 1、查询用户表获取所有注册用户数据
        count = User.objects.filter(is_staff=False).count()

        return Response({
            'count': count,
            'date': date.today()
        })


class UserDayCount(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, reqeust):
        """
            获取日增用户
        :param reqeust:
        :return:
        """
        # 1、获取当天日期 2019-09-23 0.0.0    2019-09-23 10.0.0 2019-09-23 9.23.23
        now_date = date.today()
        # 2、根据日期查询注册用户
        count = User.objects.filter(date_joined__gte=now_date, is_staff=False).count()

        return Response({
            'count': count,
            'date': now_date
        })


class UserDayActiveCount(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, reqeust):
        """
            获取日活用户
        :param reqeust:
        :return:
        """
        # 1、获取当天日期 2019-09-23 0.0.0    2019-09-23 10.0.0 2019-09-23 9.23.23
        now_date = date.today()
        # 2、根据日期查询登录用户
        count = User.objects.filter(last_login__gte=now_date, is_staff=False).count()

        return Response({
            'count': count,
            'date': now_date
        })


class UserDayOrdersCount(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, reqeust):
        """
            获取下单用户
        :param reqeust:
        :return:
        """
        # 1、获取当天日期 2019-09-23 0.0.0    2019-09-23 10.0.0 2019-09-23 9.23.23
        now_date = date.today()
        # 2、根据日期查询下单用户  关联过滤查询 以订单表的信息作为过滤条件查询下单的用户信息
        users = set(User.objects.filter(orderinfo__create_time__gte=now_date, is_staff=False))
        count = len(users)

        return Response({
            'count': count,
            'date': now_date
        })


class UserMonthCount(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, reqeust):
        """
            获取月增用户
        :param reqeust:
        :return:
        """
        # 1、获取当天时间
        now_date = date.today()
        # 2、获取30天前日期
        old_date = now_date - timedelta(days=30)
        # 3、遍历30天范围内每天的注册用户数量，每当遍历一天添加到列表中
        date_list = []
        for i in range(31):
            # 获取当前日期
            index_date = old_date + timedelta(i)
            # 获取下一天日期
            next_date = old_date + timedelta(i + 1)

            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=next_date, is_staff=False).count()

            date_list.append({
                'count': count,
                'date': index_date
            })

        # 4、返回统计后的列表数据

        return Response(date_list)


class GoodsTypeCount(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, reqeust):
        """
            获取商品分类访问量
        :param reqeust:
        :return:
        """
        # 1、获取当天时间
        now_date = date.today()
        # 2、查询商品分类访问量表
        goodscount = GoodsVisitCount.objects.filter(date=now_date)
        # 3、获取数量
        data_list = []
        for goods in goodscount:
            data_list.append({
                'count': goods.count,
                'category': goods.category.name
            })

        return Response(data_list)
