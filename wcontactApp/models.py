import os
import locale
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings  # 新增：导入Django配置
from docxtpl import DocxTemplate
from docxtpl import InlineImage
from docx.shared import Mm

# ========== 新增：解决中文编码问题 ==========
# 设置系统区域为中文，兼容strftime处理中文字符
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Chinese (Simplified)_China.936')
    except:
        pass  # 兼容不同系统的locale名称


class Ad(models.Model):
    title = models.CharField(max_length=50, verbose_name='招聘岗位')
    description = models.TextField(verbose_name='岗位要求')
    publishDate = models.DateTimeField(max_length=20,
                                       default=timezone.now,
                                       verbose_name='发布时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '招聘广告'
        verbose_name_plural = '招聘广告'
        ordering = ('-publishDate',)


class Resume(models.Model):
    name = models.CharField(max_length=20, verbose_name='姓名', default='未填写')
    personID = models.CharField(max_length=30, verbose_name='身份证号', default='000000000000000000')
    sex = models.CharField(max_length=5, default='男', verbose_name='性别')
    email = models.EmailField(max_length=30, verbose_name='邮箱', default='noemail@example.com')
    birth = models.DateField(max_length=20,
                             default=datetime.strftime(datetime.now(), "%Y-%m-%d"),
                             verbose_name='出生日期')
    edu = models.CharField(max_length=5, default='本科', verbose_name='学历')
    school = models.CharField(max_length=40, verbose_name='毕业院校', default='未填写')
    major = models.CharField(max_length=40, verbose_name='专业', default='未填写')
    position = models.CharField(max_length=40, verbose_name='申请职位', default='未填写')
    experience = models.TextField(blank=True,
                                  null=True,
                                  verbose_name='学习或工作经历')
    photo = models.ImageField(upload_to='contact/recruit/%Y-%m-%d',
                              verbose_name='个人照片', blank=True, null=True)
    grade_list = (
        (1, '未审'),
        (2, '通过'),
        (3, '未通过'),
    )
    status = models.IntegerField(choices=grade_list,
                                 default=1,
                                 verbose_name='面试成绩')
    publishDate = models.DateTimeField(max_length=20,
                                       default=timezone.now,
                                       verbose_name='提交时间')
    # 新增：存储生成的Word文件路径（方便后台查看）
    generated_resume = models.FileField('生成的简历', upload_to='generated_resumes', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '简历'
        verbose_name_plural = '简历'
        ordering = ('-status', '-publishDate')


# 保存简历后发邮件+生成Word
@receiver(post_save, sender=Resume)
def after_save_resume(sender, instance,** kwargs):
    # 1. 发送邮件逻辑
    EMAIL_FROM = '2018166039@qq.com'
    if instance.status == 2:
        email_title = '通知：亨达科技招聘初试结果'
        email_body = '恭喜您通过本企业初试'
        send_mail(email_title, email_body, EMAIL_FROM, [instance.email])
    elif instance.status == 3:
        email_title = '通知：亨达科技招聘初试结果'
        email_body = '很遗憾，您未通过本企业初试，谢谢您的关注'
        send_mail(email_title, email_body, EMAIL_FROM, [instance.email])

    # 2. 仅当状态为“通过”时生成Word
    if instance.status == 2:
        # ========== 核心修改1：硬编码模板的实际绝对路径 ==========
        template_path = 'D:\\whengdaProject\\whengdaProject\\templates\\word_templates\\recruit_template.docx'

        # 检查模板文件是否存在（不存在则抛出明确错误）
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Word模板文件不存在，请检查路径：{template_path}")

        # 加载模板
        template = DocxTemplate(template_path)

        # 构造上下文（处理图片为空的情况）
        # ========== 核心修改2：替换strftime，避免中文编码问题 ==========
        # 手动拼接日期，不用strftime处理中文字符
        birth_str = f"{instance.birth.year}年{instance.birth.month}月{instance.birth.day}日"
        
        context = {
            'name': instance.name,
            'personID': instance.personID,
            'sex': instance.sex,
            'email': instance.email,
            'birth': birth_str,  # 使用手动拼接的日期
            'edu': instance.edu,
            'school': instance.school,
            'major': instance.major,
            'position': instance.position,
            'experience': instance.experience or '无',
        }
        # 处理照片（仅当有照片时才添加，避免报错）
        if instance.photo and os.path.exists(instance.photo.path):
            context['photo'] = InlineImage(template, instance.photo.path, width=Mm(30), height=Mm(40))
        else:
            context['photo'] = ''

        # 配置生成文件的保存路径
        generate_dir = os.path.join(settings.MEDIA_ROOT, 'generated_resumes')
        if not os.path.exists(generate_dir):
            os.makedirs(generate_dir)
        # 生成唯一文件名（避免重复）
        filename = f'{instance.name}_{instance.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.docx'
        save_path = os.path.join(generate_dir, filename)

        # 渲染并保存Word文件
        template.render(context)
        template.save(save_path)

        # 关联生成的文件到模型字段（后台可查看/下载）
        instance.generated_resume = f'generated_resumes/{filename}'
        # 避免再次触发post_save信号，用filter+update更新
        Resume.objects.filter(pk=instance.pk).update(generated_resume=instance.generated_resume)