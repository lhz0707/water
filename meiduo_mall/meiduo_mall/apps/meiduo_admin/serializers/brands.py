from django.conf import settings
from fdfs_client.client import Fdfs_client, os

from rest_framework import serializers

from goods.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定模型类
        model = Brand
        # 指定字段
        fields = '__all__'


    def create(self, validated_data):
        # 1、初始化生成连接对象
        client = Fdfs_client(os.path.join(settings.BASE_DIR, 'utils/fasfdfs/client.conf'))
        # 2、获取图片数据
        image = validated_data['logo']
        # 3、上传图片
        res = client.upload_by_buffer(image.read())
        # 4、判断图片是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('图片上传失败')
        # 5、将图片在fasfDFS中的连接地址保存在图片表
        image_path = res['Remote file_id']

        brand=Brand.objects.create(logo=image_path,name=validated_data['name'],first_letter=validated_data['first_letter'])
        return brand

    def update(self, instance, validated_data):
        # 1、初始化生成连接对象
        client = Fdfs_client(os.path.join(settings.BASE_DIR, 'utils/fasfdfs/client.conf'))
        # 2、获取图片数据
        image = validated_data['logo']
        # 3、上传图片
        res = client.upload_by_buffer(image.read())
        # 4、判断图片是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('图片上传失败')
        # 5、将图片在fasfDFS中的连接地址保存在图片表
        image_path = res['Remote file_id']
        instance.logo=image_path
        instance.name=validated_data['name']
        instance.first_letter=validated_data['first_letter']
        instance.save()
        return instance