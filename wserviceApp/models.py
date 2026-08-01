from django.db import models
import django.utils.timezone as timezone

class Doc(models.Model):
    # 服务类型选项（与视图中SERVICE_NAME_MAP匹配）
    SERVICE_TYPE_CHOICES = (
        ('资料下载', '资料下载'),
        ('人脸识别开放平台', '人脸识别开放平台'),
    )
    title = models.CharField(max_length=250, verbose_name='资料名称')
    
    # 新增服务类型字段（视图筛选核心）
    serviceType = models.CharField(
        max_length=50,
        choices=SERVICE_TYPE_CHOICES,
        default='资料下载',
        verbose_name='服务类型'
    )
    
    # 新增描述字段（视图解析HTML用）
    description = models.TextField(blank=True, null=True, verbose_name='资料描述')
    
    file = models.FileField(
        upload_to='Service/',
        blank=True,
        null=True,
        verbose_name='文件资料'
    )
    
   
    publishDate = models.DateTimeField(
        default=timezone.now,
        verbose_name='发布时间'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publishDate']
        verbose_name = "资料"
        verbose_name_plural = verbose_name