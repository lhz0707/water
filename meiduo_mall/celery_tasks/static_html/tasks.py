from django.template import loader

from contents.utils import get_categories
from goods.models import SKU, GoodsCategory, SKUSpecification
from celery_tasks.main import celery_app
@celery_app.task(name='get_detail_static')
def get_detail_static(pk):
    categories = get_categories()
    # 2、面包屑导航数据
    try:
        # 查询sku对象
        sku = SKU.objects.get(id=pk)
    except:
        return None
    cat3 = GoodsCategory.objects.get(id=sku.category.id)
    cat2 = cat3.parent
    cat1 = cat2.parent
    # 一级分类额外指定url路径
    cat1.url = cat1.goodschannel_set.filter()[0].url
    breadcrumb = {}
    breadcrumb['cat1'] = cat1
    breadcrumb['cat2'] = cat2
    breadcrumb['cat3'] = cat3

    # 3、规格和选项参数
    # 3-1 通过spu商品获取当前商品的获取规格数据
    spu = sku.spu
    specs = spu.specs.all()
    # 3-2 给规格指定规格选项
    for spec in specs:
        # 获取当前规格的所有option规格选项
        spec.option_list = spec.options.all()

        for option in spec.option_list:
            # 判断遍历的这个选项是当前商品的选项
            if option.id == SKUSpecification.objects.get(sku=sku, spec=spec).option_id:
                option.sku_id = sku.id

            else:
                # 此时的option不是当前的sku的选项
                other_good = SKU.objects.filter(specs__option_id=option.id)
                # 查询当前商品的其它规格
                sku_specs = SKUSpecification.objects.filter(sku=sku).exclude(sku=sku, spec=spec)
                # 获取其它规格的规格选项
                optionlist = []
                for sku_spec in sku_specs:
                    optionid = sku_spec.option_id
                    optionlist.append(optionid)
                other_good1 = SKU.objects.filter(specs__option_id__in=optionlist)
                good = other_good & other_good1
                option.sku_id = good[0].id

    data = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'spu': spu,
        'category_id': sku.category.id,
        'specs': specs,
    }
    # 调用模版渲染数据
    template = loader.get_template('detail.html')
    html_str = template.render(data)
    path='/Users/august/Desktop/python45/meiduo/meiduo_mall/meiduo_mall/static/detail/%d.html'%pk
    with open(path, 'w',encoding='utf-8') as f:
        f.write(html_str)