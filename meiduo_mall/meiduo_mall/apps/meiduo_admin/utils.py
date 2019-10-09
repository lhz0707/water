# 重写JWT返回结果方法
from collections import OrderedDict
from rest_framework.response import Response


def jwt_response_payload_handler(token, user, request):

    return {
        'token':token,
        'username':user.username,
        'id':user.id
    }

from rest_framework.pagination import PageNumberPagination
# 自定义分页器
class PageNum(PageNumberPagination):

    page_size_query_param = 'pagesize'
    max_page_size = 5

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('lists', data),
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('pagesize',self.max_page_size ),
        ]))