from django.shortcuts import render, HttpResponse, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse, Http404, JsonResponse
from django.utils.encoding import escape_uri_path
from django.views.decorators.csrf import csrf_exempt
from pyquery import PyQuery as pq
from .models import Doc
import os
import logging
import numpy as np
import cv2
import base64

# 配置日志
logger = logging.getLogger(__name__)

# 服务名称映射
SERVICE_NAME_MAP = {
    'download': '资料下载',
    'platform': '人脸识别开放平台'
}

# 允许下载的根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_DOWNLOAD_ROOT = os.path.join(BASE_DIR, 'media')

# ========== 资料下载相关视图 ==========
def download(request, serviceName='download'):
    submenu = serviceName
    service_name = SERVICE_NAME_MAP.get(serviceName, '资料下载')

    doc_list = list(
        Doc.objects.filter(serviceType=service_name)
        .order_by('-publishDate')
        .only('id', 'title', 'serviceType', 'publishDate', 'description', 'file')
    )
    
    for doc in doc_list:
        try:
            if doc.description and doc.description.strip():
                html = pq(doc.description)
                doc.mytxt = html('p').text()
            else:
                doc.mytxt = '无描述信息'
        except Exception as e:
            logger.error(f"解析文档[{doc.id}-{doc.title}]描述失败：{str(e)}")
            doc.mytxt = "内容解析失败"

    paginator = Paginator(doc_list, 5)
    page_data = {}

    if paginator.num_pages > 1:
        page = request.GET.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1

        try:
            doc_list = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            doc_list = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        total_pages = paginator.num_pages
        page_range = paginator.page_range

        left = page_range[max(page - 3, 0):page - 1]
        right = page_range[page:page + 2]

        page_data = {
            'left': left,
            'right': right,
            'left_has_more': len(left) > 0 and left[0] > 2,
            'right_has_more': len(right) > 0 and right[-1] < total_pages - 1,
            'first': len(left) > 0 and left[0] > 1,
            'last': len(right) > 0 and right[-1] < total_pages,
            'total_pages': total_pages,
            'page': page,
        }

    return render(
        request, 'docList.html',  
        {
            'active_menu': 'service',
            'sub_menu': submenu,
            'serviceName': service_name,
            'docList': doc_list,
            'pageData': page_data,
        }
    )

def get_doc(request, id):
    doc = get_object_or_404(Doc, id=id)
    
    if not doc.file or not hasattr(doc.file, 'path'):
        logger.error(f"文档[{id}-{doc.title}]无有效下载文件")
        raise Http404("下载文件不存在")
    
    file_path = doc.file.path
    file_name = os.path.basename(file_path)
    
    normalized_file_path = os.path.normpath(file_path)
    if not normalized_file_path.startswith(ALLOWED_DOWNLOAD_ROOT):
        logger.warning(f"非法下载尝试：{file_path} 不在允许的目录范围内")
        raise Http404("无权下载该文件")
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        logger.error(f"文档[{id}-{doc.title}]的文件不存在：{file_path}")
        raise Http404("下载文件不存在")
    
    def read_file(file_path, chunk_size=512*1024):
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except PermissionError:
            logger.error(f"无权限读取文件：{file_path}")
            raise Http404("文件读取失败：权限不足")
        except Exception as e:
            logger.error(f"读取文件[{file_path}]失败：{str(e)}")
            raise Http404(f"文件读取失败：{str(e)}")
    
    response = StreamingHttpResponse(read_file(file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(file_name)}"'
    response['X-Content-Type-Options'] = 'nosniff'
    
    return response

# ========== 人脸识别相关视图 ==========
# 加载人脸检测器（使用OpenCV内置文件）
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 图片读取辅助函数
def read_image(stream=None):
    if stream is None:
        return None
    try:
        data_temp = stream.read()
        img = np.frombuffer(data_temp, np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        logger.error(f"读取图片失败：{str(e)}")
        return None

# 人脸识别平台页面
def platform(request):
    return render(request, 'platform.html', {
        'active_menu': 'service',
        'sub_menu': 'platform',
        'serviceName': '人脸识别开放平台',
        'pageData': {
            'page_name': '人脸识别开放平台',
        }
    })

# 人脸检测接口（返回坐标数据）
@csrf_exempt
def facedetect(request):
    result = {}
    if request.method == "POST":
        img = read_image(stream=request.FILES.get("image"))
        if img is None:
            result["#faceNum"] = 0
            result["faces"] = []
            return JsonResponse(result)
        
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        faces = face_detector.detectMultiScale(
            imgGray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        face_coords = [(int(x), int(y), int(x+w), int(y+h)) for (x,y,w,h) in faces]
        result["#faceNum"] = len(faces)
        result["faces"] = face_coords
    
    return JsonResponse(result)

# 人脸检测演示接口（返回带框图片）
@csrf_exempt
def facedetectDemo(request):
    result = {}
    if request.method == "POST":
        if request.FILES.get('image') is None:
            result["#faceNum"] = -1
            return JsonResponse(result)
        
        img = read_image(stream=request.FILES["image"])
        if img is None:
            result["#faceNum"] = -2
            return JsonResponse(result)
        
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        faces = face_detector.detectMultiScale(
            imgGray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # 绘制人脸检测框
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # 编码为Base64返回
        retval, buffer_img = cv2.imencode('.jpg', img)
        img64 = base64.b64encode(buffer_img).decode('utf-8')
        result["img64"] = img64
        result["#faceNum"] = len(faces)
    
    return JsonResponse(result)