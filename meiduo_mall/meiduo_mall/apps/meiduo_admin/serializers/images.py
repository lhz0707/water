from django.conf import settings
from rest_framework import serializers
from goods.models import SKUImage, SKU
# from fdfs_client.client import Fdfs_client, os
from celery_tasks.static_html.tasks import get_detail_static

# from meiduo_mall.utils.static_html import get_detail_static


class SKUImageSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定模型类
        model = SKUImage
        # 指定字段
        fields = ('id', 'sku', 'image')

    # 将图片保存在fasfDFS中
    def create(self, validated_data):
        # 1、初始化生成连接对象
        client = Fdfs_client(os.path.join(settings.BASE_DIR, 'utils/fasfdfs/client.conf'))
        # 2、获取图片数据
        image = validated_data['image']
        # 3、上传图片
        res = client.upload_by_buffer(image.read())
        # 4、判断图片是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('图片上传失败')
        # 5、将图片在fasfDFS中的连接地址保存在图片表
        image_path = res['Remote file_id']
        sku=validated_data['sku']
        img = SKUImage.objects.create(sku=sku, image=image_path)

        sku.default_image=image_path
        sku.save()
        # 详情静态化
        # get_detail_static(validated_data['sku'].id)
        get_detail_static.delay(validated_data['sku'].id)
        # 6、返回图片对象
        return img


    def update(self, instance, validated_data):
        # 1、初始化生成连接对象
        client = Fdfs_client(os.path.join(settings.BASE_DIR, 'utils/fasfdfs/client.conf'))
        # 2、获取图片数据
        image = validated_data['image']
        # 3、上传图片
        res = client.upload_by_buffer(image.read())
        # 4、判断图片是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('图片上传失败')
        # 5、将图片在fasfDFS中的连接地址更新在图片表
        image_path = res['Remote file_id']

        instance.image=image_path
        instance.save()
        instance.sku.default_image=image_path
        instance.sku.save()
        # 详情静态化
        # get_detail_static(instance.sku.id)
        # 6、返回图片对象
        return instance

class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定模型类
        model = SKU
        # 指定字段
        fields = ('id', 'name')
