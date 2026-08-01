from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product


def products(request, productName):
    """产品列表 + 分页"""
    # 1. 解析类别
    submenu = productName
    if productName == 'robot':
        productName = '家用机器人'
    elif productName == 'monitor':
        productName = '智能监控'
    else:
        productName = '人脸识别'

    # 2. 取数据
    product_list = Product.objects.filter(
        productType=productName).order_by('-publishDate')

    # 3. 分页
    paginator = Paginator(product_list, 2)          # 每页 2 条
    page = int(request.GET.get('page', 1))
    product_page = paginator.page(page)

    # 4. 页码条数据
    page_range = list(paginator.page_range)
    total_pages = paginator.num_pages

    left, right = [], []
    left_has_more = right_has_more = first = last = False

    if page == 1:                       # 当前是第一页
        right = page_range[page:page + 2]
        if right:                       # 先保证非空
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
    elif page == total_pages:           # 最后一页
        left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]
        if left:
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
    else:                               # 中间页
        left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]
        right = page_range[page:page + 2]
        if left:
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        if right:
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

    page_data = {
        'left': left,
        'right': right,
        'left_has_more': left_has_more,
        'right_has_more': right_has_more,
        'first': first,
        'last': last,
        'total_pages': total_pages,
        'page': page,
    }

    return render(request, 'productList.html', {
        'active_menu': 'products',
        'sub_menu': submenu,
        'productName': productName,
        'productList': product_page,
        'pageData': page_data,
    })


def productDetail(request, id):
    """详情页：/product/<int:pk>/"""
    product = get_object_or_404(Product, id=id)
    product.views += 1
    product.save()
    return render(request, 'productDetail.html', {
        'active_menu': 'products',
        'product': product,
        })


