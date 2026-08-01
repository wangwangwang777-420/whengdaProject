from django.urls import path
from . import views

app_name = 'wserviceApp'

urlpatterns = [
    # 1. 资料下载路由（保留原有参数逻辑，兼容无参数访问）
    path('download/<str:serviceName>/', views.download, name='download'),
    path('download/', views.download, {'serviceName': 'download'}, name='download_no_param'),
    
    # 2. 文件下载路由（保留原有getDoc命名，匹配模板中的调用）
    path('getDoc/<int:id>/', views.get_doc, name='getDoc'),
    
    # 3. 人脸识别平台页面路由（无参数）
    path('platform/', views.platform, name='platform'),
    
    # 4. 人脸检测接口路由（API调用）
    path('facedetect/', views.facedetect, name='facedetect'),
    path('facedetectDemo/', views.facedetectDemo, name='facedetectDemo'),
]