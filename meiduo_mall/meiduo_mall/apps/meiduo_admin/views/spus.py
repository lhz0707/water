from django.conf import settings
from fdfs_client.client import Fdfs_client, os
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.brands import BrandSerializer
from meiduo_admin.serializers.skus import GoodsCategorySerializer
from meiduo_admin.serializers.spus import SPUSerializer
from meiduo_admin.utils import PageNum
from goods.models import SPU,Brand,GoodsCategory


class SPUView(ModelViewSet):
    """
        SPU表增删改查
    """
    # 指定序列化器
    serializer_class = SPUSerializer
    # 指定数据的查询集
    queryset = SPU.objects.all()
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = PageNum

    # 获取商品品牌
    def brands(self,request):
        data=Brand.objects.all()
        ser=BrandSerializer(data,many=True)
        return Response(ser.data)

    # 获取一级分类
    def categories(self,request):
        data=GoodsCategory.objects.filter(parent=None)
        ser=GoodsCategorySerializer(data,many=True)
        return Response(ser.data)

    # 获取二级分类
    def categories_child(self, request,pk):
        data = GoodsCategory.objects.filter(parent=pk)
        ser = GoodsCategorySerializer(data, many=True)
        return Response(ser.data)
    # 保存上传的图片
    def image(self,request):
        # 1、初始化生成连接对象
        client = Fdfs_client(os.path.join(settings.BASE_DIR, 'utils/fasfdfs/client.conf'))
        # 2、获取图片数据
        image = request.data.get('image')
        # 3、上传图片
        res = client.upload_by_buffer(image.read())
        # 4、判断图片是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response({'error':'上传失败'})
        # 5、将图片在fasfDFS中的连接地址保存在图片表
        image_path = res['Remote file_id']
        image_url='http://10.211.55.30:8888/'+image_path
        return Response({'img_url':image_url})