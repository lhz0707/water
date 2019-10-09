from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.skus import SKUSerializer, GoodsCategorySerializer, SPUSpecificationSerializer
from meiduo_admin.utils import PageNum
from goods.models import SKU, GoodsCategory, SPU


class SKUView(ModelViewSet):
    # 指定序列化器
    serializer_class = SKUSerializer
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 通过判断keyword参数返回不同的查询集数据
    def get_queryset(self):
        # 1、获取keyword 查询字符串
        keyword = self.request.query_params.get('keyword')
        if keyword is None or keyword == '':
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)

    # 获取三级分类信息
    @action(methods=['get'], detail=False)
    def categories(self, request):
        # 1、查询分类表三级分类信息
        data = GoodsCategory.objects.filter(subs=None)
        # 2、序列化返回三级分类信息
        ser = GoodsCategorySerializer(data, many=True)
        return Response(ser.data)

    # 获取规格信息
    def specs(self, request, pk):
        """
            获取规格信息
        :param request:
        :param pk: spu的ID值
        :return:
        """
        # 1、根据id查询spu商品
        try:
            spu = SPU.objects.get(id=pk)
        except:
            return Response({'error': 'id不存在'}, status=400)
        # 2、根据spu商品查询对应规格
        specs_data = spu.specs

        # 3、序列化返回规格数据
        ser = SPUSpecificationSerializer(specs_data, many=True)

        return Response(ser.data)
