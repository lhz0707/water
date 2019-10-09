from time import sleep

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django_redis import get_redis_connection

from carts.utils import get_carts
from users.models import User
from django.contrib.auth.decorators import login_required
from celery_tasks.send_email.tasks import send_emails
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
import re
import json, pickle, base64


# Create your views here.


class IndexView(View):
    def get(self, request):
        # request.user可以获取当前登录过的用户对象
        user = request.user
        return render(request, 'index.html')


class UserRegisterView(View):
    """
        用户注册
    """

    def get(self, request):
        """
            获取注册页面
        :param request:
        :return:
        """
        return render(request, 'register.html')

    def post(self, request):
        # 1、获取前端传递的表单数据
        data = request.POST
        username = data.get('user_name')
        pwd1 = data.get('pwd')
        pwd2 = data.get('cpwd')
        mobile = data.get('phone')
        image_code = data.get('pic_code')
        sms_code = data.get('msg_code')
        allow = data.get('allow')
        # 2、验证表单数据
        # 验证表单数据否存在
        if username is None or pwd1 is None or pwd2 is None or mobile is None or image_code is None or sms_code is None or allow is None:
            return render(request, 'register.html', {'error_message': '数据不能为空'})
        # 验证用户名长度
        if len(username) < 5 or len(username) > 20:
            return render(request, 'register.html', {'error_message': '长度不符合要求'})

        # 支持手机号作为用户名进行注册
        if re.match(r'1[3-9]\d{9}', username):
            if username != mobile:
                return render(request, 'register.html', {'error_message': '用户名和手机号不一致'})

        # 验证用户名是否存在
        try:
            user = User.objects.get(username=username)
        except:
            user = None
        if user:
            return render(request, 'register.html', {'error_message': '用户存在'})

        # 验证两次密码是否一致
        if pwd1 != pwd2:
            return render(request, 'register.html', {'error_message': '密码不一致'})
        # 验证手机号格式
        if not re.match(r'1[3-9]\d{9}', mobile):
            return render(request, 'register.html', {'error_message': '手机格式不正确'})

        # 手机号长度
        if len(mobile) != 11:
            return render(request, 'register.html', {'error_message': '手机格式不正确'})
        # 验证短信验证码长度
        if len(sms_code) != 6:
            return render(request, 'register.html', {'error_message': '短信验证码不正确'})
        # 取出redis中的保存的当前手机号所对应的验证码
        client = get_redis_connection('verfycode')
        real_sms_code = client.get('sms_code_%s' % mobile)
        if real_sms_code is None:
            return render(request, 'register.html', {'error_message': '短信验证码已失效'})
        if sms_code != real_sms_code.decode():
            return render(request, 'register.html', {'error_message': '短信验证码错误'})
        # 3、保存数据到数据库中
        # User.objects.create(username=username,mobile=mobile,password=pwd1)
        user = User.objects.create_user(username=username, mobile=mobile, password=pwd1)
        # 注册保存数据成功后，进行状态保持
        login(request, user)
        # 4、注册成功后，引导用户跳转首页
        return redirect('/')


class UserLoginView(View):
    def get(self, request):
        """
            渲染返回登录页面
        :param request:
        :return:
        """
        return render(request, 'login.html')

    def post(self, request):
        """
            登录业务
        :param request:
        :return:
        """
        # 1、获取数据
        data = request.POST
        username = data.get('username')
        password = data.get('pwd')
        remembered = data.get('remembered')
        next = request.GET.get('next')
        if next is None:
            next = '/'
        # 2、数据验证
        # if username is None or password is None or username == '':
        #     return render(request, 'login.html', {'loginerror': '数据不能为空'})
        # try:
        #     user=User.objects.get(username=username)
        # except:
        #     return render(request, 'login.html', {'loginerror': '用户名错误'})
        #
        # # 校验密码 加密1111111——————》aasasdasd
        # if not user.check_password(password):
        #     return render(request, 'login.html', {'loginerror': '密码错误'})

        # authenticate是Django认证系统提供的用户校验方法，成功返回用户对象，失败返回None
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'loginerror': '用户名或密码错误'})

        # 3、状态保持
        login(request, user)

        # 判断用户是否选择记住登录
        if remembered == 'on':
            request.session.set_expiry(60 * 60 * 24 * 7)
            response = redirect(next)
            response.set_cookie('username', username, 60 * 60 * 24 * 7)
        else:
            request.session.set_expiry(60 * 60 * 2)
            response = redirect(next)
            response.set_cookie('username', username, 60 * 60 * 2)
        # 合并购物车
        response = get_carts(request, response, user)
        # 4、跳转到首页
        return response


class UserLogoutView(View):
    """
        退出登录
    """

    def get(self, request):
        # 使用Django认证系统的方法完成退出登录  删除session
        logout(request)

        response = redirect('/login/')
        if request.COOKIES.get('username'):
            # 删除cookie中的username
            response.delete_cookie('username')

        return response


@method_decorator(login_required, name='dispatch')
# login_required本身只能装饰方法，配合method_decorator类装饰器一块进行使用
class UserInfoView(View):
    """
        用户中心
    """

    def get(self, request):
        return render(request, 'user_center_info.html')


@method_decorator(login_required, name='dispatch')
class UserEmailView(View):
    def put(self, request):
        """
            邮箱更新
        :param request:
        :return:
        """
        # 1、获取json数据
        data = request.body.decode()
        # 2、将json转化为字典
        data_dict = json.loads(data)
        to_email = data_dict['email']
        # 3、验证邮箱的有效性 往用户输入的邮箱中发送邮件
        # 1-标题 2-邮件信息内容 3-用户看到发件人信息 4-收件人的邮箱 html_message 将标签当html标签使用
        user = request.user
        tjs = TJS(settings.SECRET_KEY, 300)
        token = tjs.dumps({'username': user.username, 'email': to_email}).decode()
        verify_url = settings.EMAIL_VERIFY_URL + '?token=%s' % token
        send_emails.delay(to_email, verify_url, settings.EMAIL_FROM)
        # 4、更新邮箱
        if not user.is_authenticated:
            return JsonResponse({'code': 4101})
        user.email = to_email
        # save方法必须执行
        user.save()

        return JsonResponse({'code': 0})


@method_decorator(login_required, name='dispatch')
class UserEmailVerifyView(View):
    def get(self, request):
        """
            验证跳转到美多的邮箱验证验证连接
        :param request:
        :return:
        """
        # 1、获取token数据
        token = request.GET.get('token')
        if token is None:
            return HttpResponse("缺少token值", status=400)
        # 2、解密token
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(token)
        except:
            return HttpResponse("无效token值", status=400)
        # 3、提取username和email
        username = data.get('username')
        email = data.get('email')
        if username is None or email is None:
            return HttpResponse("token值失效", status=400)
        # 4、验证username和email的数据机用户是否正确
        try:
            user = User.objects.get(username=username, email=email)
        except:
            return HttpResponse("错误的数据", status=400)
        # 5、更细邮箱状态
        user.email_active = True
        user.save()
        # 6、返回结果
        return render(request, 'user_center_info.html')


@method_decorator(login_required, name='dispatch')
class ChangePWDView(View):
    def get(self, request):
        """
            获取修改密码页面
        :param request:
        :return:
        """
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """
            修改密码
        :param requeat:
        :return:
        """
        # 1、获取表单中的密码信息
        data = request.POST
        old_pwd = data.get('old_pwd')
        new_pwd = data.get('new_pwd')
        new_cpwd = data.get('new_cpwd')
        # 2、校验密码
        user = request.user
        if not user.check_password(old_pwd):
            return render(request, 'user_center_pass.html', {'errors_pwd': '密码错误'})
        if new_cpwd != new_pwd:
            return render(request, 'user_center_pass.html', {'errors_pwd': '两次密码不一致'})
        # 3、更新新密码
        user.set_password(new_pwd)
        user.save()
        # 4、返回结果
        return render(request, 'user_center_pass.html', {'errors_pwd': '修改成功'})
