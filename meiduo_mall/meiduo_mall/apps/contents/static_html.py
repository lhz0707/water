from django.shortcuts import render
from django.template import loader

from contents.models import ContentCategory
from contents.utils import get_categories
from datetime import datetime

def get_index_static():
        """
            渲染首页
        :param request:
        :return:
        """
        # time=datetime.now().strftime('%Y%m%d%H%M%S')
        print('首页静态化定时任务--')

        # 1、渲染分类导航数据
        categories = get_categories()

        # 2、渲染广告数据
        contents = {}
        # 查询所有广告分类
        contentcategorys = ContentCategory.objects.all()
        for contentcategory in contentcategorys:
            contents[contentcategory.key] = contentcategory.content_set.filter(status=True).order_by('sequence')

        data = {
            'categories': categories,
            'contents': contents
        }
        # 调用模版渲染数据
        template=loader.get_template('index.html')
        html_str=template.render(data)

        with open('/Users/august/Desktop/python45/meiduo/meiduo_mall/meiduo_mall/static/index.html','w',encoding='utf-8') as f:
            f.write(html_str)

