from rest_framework import serializers

from celery_tasks.static_html.tasks import get_detail_static
from goods.models import SKU, GoodsCategory, SPUSpecification, SpecificationOption, SKUSpecification
from django.db import transaction


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """
        sku具体规格表的序列化器
    """
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        # 指定模型类
        model = SKUSpecification
        # 指定字段
        fields = ('spec_id', 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """
        sku表序列化器
    """
    # 显示指明字断
    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    # 关联嵌套字段  sku具体规格表
    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        # 指定模型类
        model = SKU
        # 指定字段
        fields = '__all__'

    # 父类保存时没有保存sku具体规格表，所以需要重写保存方法
    def create(self, validated_data):
        # 1、调用父类保存sku表
        specs = validated_data['specs']
        del validated_data['specs']
        # 开启事务
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            try:
                sku = super().create(validated_data)
                # 2、保存sku具体规格表
                for spec in specs:
                    SKUSpecification.objects.create(sku=sku, spec_id=spec['spec_id'], option_id=spec['option_id'])
            except:
                # 回滚保存点
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')
            else:
                # 提交
                transaction.savepoint_commit(save_point)
                # 页面静态化
                get_detail_static.delay(sku.id)
                return sku



    def update(self, instance, validated_data):
        # 1、调用父类更新sku表
        specs = validated_data['specs']
        del validated_data['specs']
        # 开启事务
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            try:
                sku = super().update(instance,validated_data)
                # 2、保存sku具体规格表
                for spec in specs:
                    SKUSpecification.objects.filter(sku=sku,spec_id=spec['spec_id']).update(option_id=spec['option_id'])
            except:
                # 回滚保存点
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')
            else:
                # 提交
                transaction.savepoint_commit(save_point)
                # 页面静态化
                get_detail_static.delay(sku.id)
                return sku


class GoodsCategorySerializer(serializers.ModelSerializer):
    """
           商品分类表序列化器
    """

    class Meta:
        # 指定模型类
        model = GoodsCategory
        # 指定字段
        fields = '__all__'


class SpecificationOptionSerializer(serializers.ModelSerializer):
    """
               商品规格选项表序列化器
    """

    class Meta:
        # 指定模型类
        model = SpecificationOption
        # 指定字段
        fields = ('id', 'value')


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """
            商品规格表序列化器
    """
    # 子表嵌套父表返回   嵌套spu信息返回
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    # 父表嵌套子表返回  嵌套规格选项表返回
    options = SpecificationOptionSerializer(many=True)

    class Meta:
        # 指定模型类
        model = SPUSpecification
        # 指定字段
        fields = '__all__'
