import json

from django.shortcuts import render
from django.views import View
# Django提供的分页类
from django.core.paginator import Paginator
from goods.models import GoodsCategory, SKU, SKUSpecification, GoodsVisitCount, GoodsCategory
from django.http import JsonResponse
from django_redis import get_redis_connection
from orders.models import OrderGoods

# Create your views here.
from contents.utils import get_categories


class GoodsListVIew(View):
    def get(self, request, categorie_id, page_num):
        """
            渲染列表页
        :param request:
        :param categorie_id:  三级分类id
        :param page_num: 页数
        :return:
        """
        # 频道分类数据
        categories = get_categories()

        # 面包屑导航数据
        cat3 = GoodsCategory.objects.get(id=categorie_id)
        cat2 = cat3.parent
        cat1 = cat2.parent
        # 一级分类额外指定url路径
        cat1.url = cat1.goodschannel_set.filter()[0].url
        breadcrumb = {}
        breadcrumb['cat1'] = cat1
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = cat3

        # 渲染当前分类下的所有商品
        # 获取排序字段
        sort = request.GET.get('sort')
        if sort is None or sort == 'create_time':
            sort = 'create_time'
            # 默认排序
            skus = SKU.objects.filter(category_id=categorie_id).order_by('create_time')
        elif sort == 'price':
            # 按照价格排序
            skus = SKU.objects.filter(category_id=categorie_id).order_by('price')

        else:
            # 按照销量排序
            skus = SKU.objects.filter(category_id=categorie_id).order_by('sales')

        # 分页
        page = Paginator(skus, 5)
        page_skus = page.page(page_num)

        data = {

            'categories': categories,  # 频道分类数据
            'breadcrumb': breadcrumb,  # 面包写导航数据
            'page_skus': page_skus,  # 分页后的商品数据
            'category': cat3,  # 分类对象
            'page_num': page_num,  # 当前页数
            'total_page': page.num_pages,  # 总页数
            'sort': sort  # 排序字段
        }
        return render(request, 'list.html', data)


class GoodsHotView(View):
    def get(self, request, categorie_id):
        """
            获取热销商品
        :param request:
        :param categorie_id:  分类id
        :return:
        """
        # 1、提取分类id
        # 2、根据分类id查询当前分类下的热销商品
        data = SKU.objects.filter(category_id=categorie_id).order_by('-sales')
        skus = data[0:3]
        hot_sku_list = []
        for sku in skus:
            hot_sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url

            })
        # 3、返回商品信息
        return JsonResponse({'hot_sku_list': hot_sku_list})


class GoodsSearchView(View):
    def get(self, request):
        # 获取查询关键字
        q = request.GET.get('q')

        # 根据关键字搜索数据库
        skus = SKU.objects.filter(name__contains=q)
        # 频道分类数据
        categories = get_categories()

        page = Paginator(skus, 5)
        page_skus = page.page(1)

        # 返回搜索结果

        data = {

            'categories': categories,  # 频道分类数据
            'page_skus': page_skus,  # 分页后的商品数据
            'page_num': 1,  # 当前页数
            'total_page': page.num_pages,  # 总页数
        }
        return render(request, 'search_list.html', data)


class GoodsDetailView(View):
    def get(self, request, pk):
        """
            渲染详情页
        :param request:
        :param pk:  sku的id值
        :return:
        """
        # 1、商品频道分类数据渲染
        categories = get_categories()
        # 2、面包屑导航数据
        try:
            # 查询sku对象
            sku = SKU.objects.get(id=pk)
        except:
            return JsonResponse({'error': '错误'})
        cat3 = GoodsCategory.objects.get(id=sku.category.id)
        cat2 = cat3.parent
        cat1 = cat2.parent
        # 一级分类额外指定url路径
        cat1.url = cat1.goodschannel_set.filter()[0].url
        breadcrumb = {}
        breadcrumb['cat1'] = cat1
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = cat3

        # 3、规格和选项参数
        # 3-1 通过spu商品获取当前商品的获取规格数据
        spu = sku.spu
        specs = spu.specs.all()
        # 3-2 给规格指定规格选项
        for spec in specs:
            # 获取当前规格的所有option规格选项
            spec.option_list = spec.options.all()

            for option in spec.option_list:
                # 判断遍历的这个选项是当前商品的选项
                if option.id == SKUSpecification.objects.get(sku=sku, spec=spec).option_id:
                    option.sku_id = sku.id

                else:
                    # 此时的option不是当前的sku的选项
                    other_good = SKU.objects.filter(specs__option_id=option.id)
                    # 查询当前商品的其它规格
                    sku_specs = SKUSpecification.objects.filter(sku=sku).exclude(sku=sku, spec=spec)
                    # 获取其它规格的规格选项
                    optionlist = []
                    for sku_spec in sku_specs:
                        optionid = sku_spec.option_id
                        optionlist.append(optionid)
                    other_good1 = SKU.objects.filter(specs__option_id__in=optionlist)
                    good = other_good & other_good1
                    option.sku_id = good[0].id

        data = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'spu': spu,
            'category_id': sku.category.id,
            'specs': specs,
        }

        return render(request, 'detail.html', data)


class GoodsVisitView(View):
    def post(self, reqeust, pk):
        """
            商品分类访问量统计
        :param reqeust:
        :param pk:  分类id
        :return:
        """
        # 判断分类是否存在
        try:
            GoodsCategory.objects.get(id=pk)
        except:
            return JsonResponse({'error': 'cuow'}, status=400)
        try:
            # 判断当前的分类是否保存过
            goodvisit = GoodsVisitCount.objects.get(category_id=pk)
        except:
            # 没有保存过进行保存
            GoodsVisitCount.objects.create(category_id=pk, count=1)
            return JsonResponse({'massage': 'ok'})

        goodvisit.count += 1
        goodvisit.save()

        return JsonResponse({'massage': 'ok'})


class GoodsHistoryView(View):
    def post(self, request):
        """
            用户浏览历史记录
        :param request:
        :return:
        """
        # 1、获取前端传递的sku_id   请求体
        data = request.body.decode()
        data_dict = json.loads(data)
        # 2、验证sku_id所对应的商品是否存在
        sku_id = data_dict.get('sku_id')
        try:
            SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({"error": '错误'}, status=400)
        # 3、获取当前登录用户
        user = request.user
        # 4、连接redis
        client = get_redis_connection('history')
        # 5、判断当前sku——id是否已经存储过，存储过则删除
        client.lrem('history_%s'%user,0,sku_id)
        # 6、将数据写入redis列表
        client.lpush('history_%s'%user,sku_id)
        # 7、控制存储数量，进行数据截取
        client.ltrim('history_%s'%user,0,5)
        # 8、返回结果
        return JsonResponse({'message':'ok'})

    def get(self,request):
        # 1、获取当前用户
        user=request.user
        # 2、连接reids
        client = get_redis_connection('history')
        # 3、提取sku_id数据
        sku_ids=client.lrange('history_%s'%user,0,-1)
        # 4、根据sku_id查询商品对象
        skus=SKU.objects.filter(id__in=sku_ids)
        sku_list=[]
        for sku in skus:
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url':sku.default_image.url,
                'price':sku.price
            })
        # 5、将查询到商品进行返回
        return JsonResponse({'skus':sku_list})


class GoodsCommentView(View):
    def get(self,request,sku_id):
        """
            获取商品评价信息
        :param request:
        :return:
        """
        # 1、根据sku_id查询订单商品
        try:
            SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'error':'商品不存在'},status=400)
        goods_order=OrderGoods.objects.filter(sku_id=sku_id,is_commented=True)
        # 2、获取订单商品的评价信息,构建返回数据的结构形式
        goods_comment_list=[]
        for good in goods_order:
            goods_comment_list.append({
                'username':good.order.user.username,
                'comment':good.comment,
                'score_class':good.score
            })
        # 3、返回结果
        return JsonResponse({'code':0,'goods_comment_list':goods_comment_list})
