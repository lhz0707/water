from django import http
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import login
# settings获取Django配置文件中的属性数据
from django.conf import settings
from QQLoginTool.QQtool import OAuthQQ

from carts.utils import get_carts
from meiduo_mall.libs import sinaweibopy3
from oauth.models import OAuthQQUser
from django_redis import get_redis_connection
from users.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as TJS


# Create your views here.
class QQLoginView(View):
    def get(self, request):
        # 获取登录成功后的跳转连接
        next = request.GET.get('next')
        if next is None:
            next = '/'
        # 1、初始化创建qq对象
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 2、调用方法生成跳转连接
        login_url = qq.get_qq_url()
        # 3、返回跳转连接
        return JsonResponse({'login_url': login_url})


class QQCallBackView(View):
    def get(self, request):
        # 1、获取code值和state
        code = request.GET.get('code')
        state = request.GET.get('state')
        if code is None or state is None:
            return JsonResponse({'error': '缺少数据'}, status=400)
        # 2、生成qq对象
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        try:
            # 3、调用方法获取access_token值
            access_token = qq.get_access_token(code)
            # 4、调用方法获取open_id值
            open_id = qq.get_open_id(access_token)
        except:
            return JsonResponse({'errorr': '网路错误'}, status=400)
        # 5、判断openid是否绑定过美多用户
        try:
            qq_user = OAuthQQUser.objects.get(openid=open_id)
        except:
            # qq未绑定过
            tjs = TJS(settings.SECRET_KEY, 300)
            openid = tjs.dumps({'openid': open_id}).decode()
            return render(request, 'oauth_callback.html', {'token': openid})

        # 没有异常说明说明qq查询到绑定用户
        # 状态保持
        login(request, qq_user.user)

        # 将用户名写入cookie方便在页面中展示
        response = redirect(state)
        response.set_cookie('username', qq_user.user.username, 60 * 60 * 2)
        # 合并购物车
        response = get_carts(request, response, qq_user.user)
        return response

    def post(self, request):
        """
            绑定qq用户
        :param request:
        :return:
        """
        # 1、获取数据
        data = request.POST
        mobile = data.get('mobile')
        password = data.get('pwd')
        sms_code = data.get('sms_code')
        openid = data.get('access_token')
        # 2、验证数据
        # 短息验证
        client = get_redis_connection('verfycode')
        real_sms_code = client.get('sms_code_%s' % mobile)
        if real_sms_code is None:
            return render(request, 'oauth_callback.html', {'errmsg': '短信验证码已失效'})
        if sms_code != real_sms_code.decode():
            return render(request, 'oauth_callback.html', {'errmsg': '短信验证码错误'})
        # 3、绑定数据
        try:
            user = User.objects.get(mobile=mobile)
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'errmsg': '密码错误'})

        except:
            # 当前手机未注册为美多用户，使用当前手机号创建一个新用户
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        # 将openid 绑定表中
        # 解密openid
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(openid)
        except:
            return render(request, 'oauth_callback.html', {'errmsg': 'openid异常'})
        openid = data.get('openid')
        OAuthQQUser.objects.create(openid=openid, user=user)

        # 状态保持
        login(request, user)

        # 将用户名写入cookie方便在页面中展示
        response = redirect('/')
        response.set_cookie('username', user.username, 60 * 60 * 2)
        # 合并购物车
        response = get_carts(request, response, user)
        return response


class OAuthSinaURLView(View):
    def get(self, request):
        next_url = request.GET.get('next')

        # 创建授权对象
        client = sinaweibopy3.APIClient(app_key=3305669385, app_secret='74c7bea69d5fc64f5c3b80c802325276',redirect_uri='http://www.meiduo.site:8000/sina_callback')
        # 生成授权地址

        login_url =client.get_authorize_url()

        # 响应
        return http.JsonResponse({
            'code': '0',
            'errmsg': "OK",
            'login_url': login_url
        })

class OAuthSinaOpenidView(View):
    def get(self, request):
        code = request.GET.get('code')

        client = sinaweibopy3.APIClient(app_key=3305669385, app_secret='74c7bea69d5fc64f5c3b80c802325276',  redirect_uri='http://www.meiduo.site:8000/sina_callback')

        # 1.根据code获取access_token
        result = client.request_access_token(code)
        client.set_access_token(result.access_token, result.expires_in)
        openid=result.uid

        return JsonResponse({'ok':'ok'})

            # return http.HttpResponse(openid)
#
#     def post(self, request):
#         # 接收：openid,mobile,password,sms_code
#         access_token = request.POST.get('access_token')
#         mobile = request.POST.get('mobile')
#         pwd = request.POST.get('pwd')
#         sms_code = request.POST.get('sms_code')
#         state = request.GET.get('state', '/')
#
#         # 验证：参考注册的验证
#         openid_dict = meiduo_signature.loads(access_token, constants.OPENID_EXPIRES)
#         if openid_dict is None:
#             return http.HttpResponseForbidden('授权信息无效，请重新授权')
#         openid=openid_dict.get('openid')
#
#         # 处理：初次授权，完成openid与user的绑定
#         # 1.判断手机号是否已经使用
#         try:
#             user = User.objects.get(mobile=mobile)
#         except:
#             # 2.如果未使用，则新建用户
#             user = User.objects.create_user(mobile, password=pwd, mobile=mobile)
#         else:
#             # 3.如果已使用，则验证密码
#             # 3.1密码正确，则继续执行
#             if not user.check_password(pwd):
#                 # 3.2密码错误，则提示
#                 return http.HttpResponseForbidden('手机号已经使用，或密码错误')
#
#         # 4.绑定：新建OAuthSinaUser对象
#         qquser = OAuthSinaUser.objects.create(
#             user=user,
#             uid=openid
#         )
#         # 状态保持
#         login(request, user)
#         response = redirect(state)
#         response.set_cookie('username', user.username)
#
#         # 响应
#         return response