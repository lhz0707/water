from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from meiduo_admin.serializers.orders import OrderInfoSerializer
from meiduo_admin.serializers.users import UsersSerializer
from meiduo_admin.utils import PageNum
from orders.models import OrderInfo


class OrderInfoView(ReadOnlyModelViewSet):
    # 指定序列化器
    serializer_class = OrderInfoSerializer
    # 指定数据的查询集
    # queryset = User.objects.filter(is_staff=False)
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 通过判断keyword参数返回不同的查询集数据
    def get_queryset(self):
        # 1、获取keyword 查询字符串
        keyword = self.request.query_params.get('keyword')
        if keyword is None or keyword == '':
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)

    # 修改订单状态
    @action(methods=['put'],detail=True)
    def status(self, request, pk):
        # 1、根据order_id查询订单对象
        try:
            order = OrderInfo.objects.get(order_id=pk)
        except:
            return Response({'error': '订单错误'}, status=400)
        # 2、使用订单对象修改当前订单状态
        status = request.data.get('status')
        if status is None:
            return Response({'error': '订单状态错误'}, status=400)
        order.status = status
        order.save()

        return Response({'status':status})
