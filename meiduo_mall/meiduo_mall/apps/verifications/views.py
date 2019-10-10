import code
import random
from celery_tasks import code_sms
import expire as expire
from django.db.models import constants
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from rest_framework.authtoken import serializers

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView


from meiduo_mall.libs.captcha.captcha import Captcha, captcha
from meiduo_mall.libs.yuntongxun.sms import CCP
from users.models import User
from celery_tasks.code_sms.tasks import send_sms_code
from threading import Thread




# Create your views here.
class ImgaeView(APIView):
    def get(self,request,image_code_id):
        # 获取图片验证码
        text, image = captcha.generate_captcha()
        redis_conn=get_redis_connection('verfycode')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image,content_type='image/jpg')

import verifications.serialiers
class SmsCodeView(GenericAPIView):
    # 短信验证码
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self,request,mobile):
        # 判断短信验证码
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证
        sms_code ='%06d'%random.randint(0,999999)
        # 保存短信验证码与发送记录
        # 保存短信验证码与发送记录
        redis_conn=get_redis_connection('verfycode')
        p1=redis_conn.pipeline()
        p1.setex('sms_%s'%mobile,constants.SMS_CODE_EXPIRES,sms_code)
        p1.setex('send_flag_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        p1.execute()

        # 发送短信验证码

        sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        code_sms.send_sms_code.delay(mobile, sms_code, sms_code_expires)

        return Response({'message':'OK'})
