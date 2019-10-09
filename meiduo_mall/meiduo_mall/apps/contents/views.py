from django.shortcuts import render,redirect
from django.views import View

from contents.utils import get_categories
from goods.models import SKU
from collections import OrderedDict
from goods.models import GoodsChannel
from contents.models import ContentCategory
from django.http import HttpResponse, JsonResponse


# Create your views here.
class ImageView(View):
    def get(self, request):
        skus = SKU.objects.all()
        skus_list = []
        for sku in skus:
            skus_list.append({
                'img_url': sku.default_image.url
            })
        return render(request, 'img.html', {'skus': skus_list})


class IndexView(View):
    def get(self, request):
#         """
#             渲染首页
#         :param request:
#         :return:
# {
#     "1":{
#         "channels":[
#             {"id":1, "name":"手机", "url":"http://shouji.jd.com/"},
#             {"id":2, "name":"相机", "url":"http://www.itcast.cn/"}
#         ],
#         "sub_cats":[
#             {
#                 "id":38,
#                 "name":"手机通讯",
#                 "sub_cats":[
#                     {"id":115, "name":"手机"},
#                     {"id":116, "name":"游戏手机"}
#                 ]
#             },
#             {
#                 "id":39,
#                 "name":"手机配件",
#                 "sub_cats":[
#                     {"id":119, "name":"手机壳"},
#                     {"id":120, "name":"贴膜"}
#                 ]
#             }
#         ]
#     },
#     "2":{
#         "channels":[],
#         "sub_cats":[]
#     }
# }
#         """

        # 1、渲染分类导航数据
        # categories={ '分组编号':{'channels':"第一级分类",'sub_cats':[{'id':'第二级分类id','sub_cats':['第三级分类']}]}}
        categories = get_categories()

        # 2、渲染广告数据
        contents = {}
        # 查询所有广告分类
        contentcategorys = ContentCategory.objects.all()
        for contentcategory in contentcategorys:
            contents[contentcategory.key] = contentcategory.content_set.filter(status=True).order_by('sequence')

        data = {
            'categories': categories,
            'contents': contents
        }

        return render(request, 'index.html', data)

        # def get(self,request):
        #
        #     return redirect('/static/index.html')
