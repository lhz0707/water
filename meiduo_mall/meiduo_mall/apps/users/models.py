from django.db import models
# Django自带的用户认证系统中的用户表模型类
from django.contrib.auth.models import AbstractUser


# Create your models here.
from meiduo_mall.utils.models import BaseModel


class User(AbstractUser):
    # 额外增加mobile字段，保存手机号信息
    mobile = models.CharField(max_length=11, unique=True)
    # 邮箱验证字段
    email_active = models.BooleanField(default=False, verbose_name='邮箱状态')
    default_address = models.ForeignKey('addresses.Address', related_name='users', null=True, blank=True)

    class Meta:
        # 指定用户表名
        db_table = 'tb_users'

