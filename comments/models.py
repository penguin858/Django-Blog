from django.db import models
from django.utils import timezone
 
 
class Comment(models.Model):
    name = models.CharField('name', max_length=50)
    email = models.EmailField('mailbox')
    url = models.URLField('url', blank=True)
    text = models.TextField('contents')
    created_time = models.DateTimeField('created_time', default=timezone.now)
    post = models.ForeignKey('blog.Post', verbose_name='article', on_delete=models.CASCADE)
 
    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = verbose_name
 
    def __str__(self):
        return '{}: {}'.format(self.name, self.text[:20])