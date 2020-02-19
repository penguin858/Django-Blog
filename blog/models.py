# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import markdown
from django.utils.html import strip_tags
from django.views.generic import ListView, DetailView
from comments.models import Comment
 
class Category(models.Model):
    name = models.CharField(max_length=100)
    
 
 
class Tag(models.Model):
    name = models.CharField(max_length=100)
 
 
class Post(models.Model):
    title = models.CharField(max_length=70)

    body = models.TextField()
 
    created_time = models.DateTimeField(default=timezone.now)
    modified_time = models.DateTimeField()
 
    excerpt = models.CharField(max_length=200, blank=True)
 
    # ForeignKey、ManyToManyField官方文档：
    # https://docs.djangoproject.com/en/1.10/topics/db/models/#relationships
    category = models.ForeignKey(Category,on_delete=models.CASCADE,)
    tags = models.ManyToManyField(Tag, blank=True)
 
    author = models.ForeignKey(User,on_delete=models.CASCADE,)

    counts = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        verbose_name = 'article'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def save(self, *args, **kwargs):
        self.modified_time = timezone.now()

        # 首先实例化一个 Markdown 类，用于渲染 body 的文本。
        # 由于摘要并不需要生成文章目录，所以去掉了目录拓展。
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])
 
        # 先将 Markdown 文本渲染成 HTML 文本
        # strip_tags 去掉 HTML 文本的全部 HTML 标签
        # 从文本摘取前 54 个字符赋给 excerpt 
        # 这一块如果自己输入摘要的话应该不使用 之后要记得回来修改
        self.excerpt = strip_tags(md.convert(self.body))[:100]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
 
    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def increase_views(self):
        self.counts += 1
        self.save(update_fields=['counts'])

    def get_num_comments(self):
        return len(Comment.objects.filter(post=self))

    @property
    def toc(self):
        return self.rich_content.get("toc", "")
 
    @property
    def body_html(self):
        return self.rich_content.get("content", "")
 
    @property
    def rich_content(self):
        return generate_rich_content(self.body)
    
def generate_rich_content(value):
        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.extra",
                "markdown.extensions.codehilite",
            ]
        )
        content = md.convert(value)
        
        return {"content": content}