# The process of building my own blog server through Django

My blog: https://blog.zeping.top
The url may not work because of Chinese legislation. At that time try [this one](http://111.229.136.123:8080) or [another one](111.229.136.123:80).

## 0. Feature

- Be able to post articles and support Markdown.
- Have `recent posts`, `category`, `tags` as side bar
- Be able to generate abstract automatically
- Comment
- Reading and comments counts.
- Paginatiom
- Global Search
- RSS

## 1. Preparation

### (1)Initialize Mariadb

First install LAMP:

```shell
yum update
yum install httpd mariadb-server mariadb sqlite wget vim mod_ssl
systemctl start mariadb
mysql -u root -p
```

Before I build up my own website, I need to create an account of database to manage data.

```SQL
CREATE DATABASE blog_db CHARSET=utf8;
GRANT ALL ON *.* TO 'blog'@'localhost' IDENTIFIED BY 'XzP1363380773';
SET PASSWORD FOR root@localhost=password('XzP1363380773');
flush privileges;
```

### (2) Install pip, mysqlclient, and Django

The OS of my server is CentOS, which has already installed python but only 2.7 version. In order to use the latest Django 3.0, I need to install python3, pip and other package.

```shell
yum -y install epel-release python-pip 
pip install --upgrade pip
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel 
wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz 
mkdir /usr/local/python3
mv Python-3.8.0.tgz /usr/local/python3
cd /usr/local/python3
tar zxvf Python-3.8.0.tgz
./configure --prefix=/usr/local/python3
make
make install
# soft link
ln -s /usr/local/python3/bin/python3 /usr/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
yum -y install python3-devel mariadb-devel
pip3 install mysqlclient
pip3 install django # 3.0.3
```

### (3) Configure of Django

1. Config Database:

In `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blog_db',
        'USER': 'blog',
        'PASSWORD': 'XzP1363380773',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}
```

2. Close _DEBUG_ and _TEMPLATE DEBUG_ (Should be closed before getting into use)
```python
import socket
if(socket.gethostname() == 'dev_local'):
    DEBUG = TEMPLATE_DEBUG = True
else:
    DEBUG = TEMPLATE_DEBUG = False
```

3. Email

When _DEBUG_ is `False`, Django will email the users listed in the _ADMINS_ setting whenever your code raises an unhandled exception and results in an internal server error (strictly speaking, for any response with an HTTP status code of 500 or greater). This gives the administrators immediate notification of any errors. The _ADMINS_ will get a description of the error, a complete Python traceback, and details about the HTTP request that caused the error.

In `global_settings.py`:
```python
SERVER_EMAIL = '1363380773@qq.com'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 25
```

In `settings.py`:
```python
MIDDLEWARE = [
    ...
    'django.middleware.common.BrokenLinkEmailsMiddleware',
]
# Email settings
ADMINS = (
    ('Zeping', '1363380773@qq.com')
)

MANAGERS = (
    ('Zeping', '1363380773@qq.com')
)
```

## 2. First application

Use command to create a new app:

```bash
$ python3 manage.py startapp myblog
```

Then add the new APP into `INSTALLED_APPS`(`myblog/settings.py`)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myblog',
]
```

Each App has file `apps.py`. We can alter config in this file. After configuration, the app can be included by this way:
```python
INSTALLED_APPS = [
    ...
    'myblog.apps.MyblogConfig',
]
```

Besides, don't forget to set URL parser `myblog/urls.py`:
Note: should import function `include()`

```python
urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'blog/', include('myblog.urls')),
]
```


Create First view in `myblog/views.py`:

```python
from django.shortcuts import render

from django.http import HttpResponse
# Create your views here.
def index(request):
        return HttpResponse('hello django myblog')
```

Create new file `myblog/urls.py`

```python
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
```

Then we can start server to view the result:

```bash
$ python3 manage.py runserver 0.0.0.0:80
```

<!--Result:

![First Result](/Users/apple/Workshop/code/Django/Tutorial/images/FirstApp.png)-->

When we view the result, that means the configure is finished.

## 3. Create the structure of table

Data in database is stored as table. Use _Object Relational Mapping_(ORM) to create our model in MySQL.

```python
from django.db import models
from django.contrib.auth.models import User
 
class Category(models.Model):
    name = models.CharField(max_length=100)
 
 
class Tag(models.Model):
    name = models.CharField(max_length=100)
 
 
class Post(models.Model):
    title = models.CharField(max_length=70)
 
    body = models.TextField()
 
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()
 
    excerpt = models.CharField(max_length=200, blank=True)
 
    # ForeignKey、ManyToManyField官方文档：
    # https://docs.djangoproject.com/en/1.10/topics/db/models/#relationships
    category = models.ForeignKey(Category,on_delete=models.CASCADE,)
    tags = models.ManyToManyField(Tag, blank=True)
 
    author = models.ForeignKey(User,on_delete=models.CASCADE,)
```

`on_delete = models.CASCADE` means if the category or author is deleted, the related posts will also be deleted.

Then don't forget to migrate(use `makemigrations` and `migrate`:
```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

Then the model(table) has been set up.


## 4. Django template

First, create a folder called `templates` in our project root directory (that is, the directory where the manage.py file is located), which will be used to store our templates.
Then create a folder called `blog` in `templates`

Then we can create the first template `templates/blog/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ title }}</title>
</head>
<body>
<h1>{{ welcome }}</h1>
</body>
</html>
```

Then we should tell django how to find the template. Edit `settings.py`:

```python
TEMPLATES = [
    {
        ...
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        ...
    },
]
```

Edit `myblog/view.py` to use the template:

```python
from django.shortcuts import render

# Create your views here.
def index(request):
        return render(request,"blog/index.html", context={
                'title' : 'Homepage',
                'welcome' : 'Welcome to my django blog!'
        })
```

<!--Result:

![first template](/Users/apple/Workshop/code/Django/Tutorial/images/Templates.png)-->



## 5. Static File

Create a new folder `static` under `myblog`, and another folder `blog` under `static`.

You can save all your static code, including Css table and JS script.

If you want to use these files in template, follow two steps:

- include `{% load static %}` at the top of template file.
- Use `href="{% static 'FILEPATH' %}"` to import.

## 6. Create an administrator account

```bash
> python3 manage.py createsuperuser
```

## 7. BackStage

If you want to administrate data at backstage, first register models in `admin.py`:

```python
from django.contrib import admin
from .models import Tag, Post, Category

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']

admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
```

## 8. How to create some property automatically

If you want to create it during setting up, just provide `default` value:

```python
created_time = models.DateTimeField('Created Time', default=timezone.now)
```

If you want to update it if anything changed occurs, Use `save` function and call `s` in `Admin`:

```python
# models.py
def save(self, *args, **kwargs):
        self.modified_time = timezone.now()
        super().save(*args, **kwargs)
```

```python
# admin.py
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']
    fields = ['title', 'body', 'excerpt', 'category', 'tags']
    

    def save_model(self, request, obj, form, change):
        obj.author = request.user # In my case, request.user is admin
        super().save_model(request, obj, form, change)
```

## 9. URL config

When I want to design article details page, first I should set up urls correctly.


```python
from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.detail, name='detail'),
]
```

## 10. Enable Markdown

Install Markdown Parsing tool:

```bash
> pip3 install markdown
```

Parsing Markdown formatted text into HTML text is very simple, just call the library's `markdown` method. The content of the blog post we wrote is parsed, and the Markdown text is converted to HTML text and then passed to the template:


```python
# blog/views.py
from django.shortcuts import render, get_object_or_404
from .models import Post
import markdown
 
def index(request):
    post_list = Post.objects.all().order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])
    return render(request, 'blog/detail.html', context={'post': post})
```

However, the transformed text will not display as HTML element, use `safe` filter.

```html
...
<div class="entry-content clearfix"> {{ post.body|safe}} </div>
...
```

## 11. Use self-defined template tags

Step 1: Create a folder `templatetags` under `blog`, and a file `__init__.py` to make it become a Python package.

Step 2: Create your file, for example, `blog_extras.py`, to save your own template tags.

Step 3: define your template tags in `blog_extras.py`.

Step : Import template tags `{% load blog_extras %}`

## 12. About Form

Why does django provide us with a form class? For the sake of understanding, we can compare the form with the django ORM system described earlier. Recall that we use the database to save the blog posts we created, but we haven't written any database-related code from the beginning to the end (we need to know that the database itself has a database language). This is because Django's ORM system has helped us to do some thing. We follow some Python code written by django's specifications, such as creating Post, Category classes, and then reacting this code to the database by running the database migration command.

Django's form is similar to this idea. The normal front-end form code should be the HTML code mentioned at the beginning of this article, but we have not written these codes at this time, but have written a CommentForm Python class. By calling some methods and properties of this class, Django will automatically create regular form code for us, and we will see how to do it in the next tutorial.

More information about form can be found in [official documentations](https://docs.djangoproject.com/en/2.2/ref/forms/)


## 13. Deployment : Using Nginx+Gunicorn+Supervisor to deploy Django Blog

My server belongs to [Tencent Cloud](https://intl.cloud.tencent.com), uses CentOS 7.

1. Add new user

```bash
adduser zeping
passwd zeping
usermod -aG wheel zeping
su -zeping
pip3 install gunicorn
sudo yum install nginx -y
```


2. Config Nginx

The config file of Nginx is located at `/etc/nginx/nginx.conf`.

```conf
user nobody nobody;
...
http {
    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;
 
    server {
        listen       80 default_server;
        listen       [::]:80 default_server;
        server_name  _;
        root         /usr/share/nginx/html;
 
        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;
 
        location / {
        }
    }
}
```

Change user to corresponding one.

Sentence `include /etc/nginx/default.d/*.conf;` shows that all file ending with `.conf` will also be imported. So I can set up my own server config ``. 
(In my opinion, it is quite like Apache VirtualServer. I know more about Apache. However, Nginx is more popular when using Django)

```conf
server {
    charset utf-8;
    listen 80;
    server_name YOURHOSTNAME;
 
 	# location has another approach to write: root
    location /static {
        alias STATIC FILE LOCATION;
    }
 
    location / {
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:8000;
    }
}
```


Then restart Nginx:

```bash
sudo systemctl restart nginx
```

Then start Gunicorn:
```
gunicorn mysite.wsgi -w 2 -k gthread -b 127.0.0.1:8000
```

It works now. However, if I want to keep running it, I need to use supervisor.

3. Use supervisor

```bash
pip3 install supervisor
```

Then make the following index structure:

```shell
# tree
.
`-- supervisor
    |-- conf.d
    `-- var
        `-- log
```

Then generate config file:

```shell
echo_supervisord_conf > supervisord.conf
```

Change the config:

```conf
[unix_http_server]
file=YOUR_PATH/etc/supervisor/var/supervisor.sock
...
logfile=YOUR_PATH/etc/supervisor/var/log/supervisord.log
pidfile=YOUR_PATH/etc/supervisor/var/supervisord.pid
user=YOUR_ROOT_NAME
...
[supervisorctl]
serverurl=unix:///YOUR_PATH/etc/supervisor/var/supervisor.sock
...
[include]
files = /root/etc/supervisor/conf.d/*.ini
```

`YOUR_PATH/etc/supervisor/conf.d/mysite.ini`

```conf
[program:mysite]
command=gunicorn mysite.wsgi -w 2 -k gthread -b 127.0.0.1:8000
directory=/root/mysite/
autostart=true
autorestart=unexpected
user=root
stdout_logfile=/root/etc/supervisor/var/log/mysite-stdout.log
stderr_logfile=/root/etc/supervisor/var/log/mysite-stderr.log
```

Start supervisor:

```shell
supervisord -c ~/etc/supervisord.conf
supervisorctl update
```

Then it works.


## 14. Generic class based view

[Official Documents](https://docs.djangoproject.com/en/3.0/topics/class-based-views/)

Django provides some pre-defined classes of view.

If you want to use them, the most direct way is to create them directly in your `URLconf`. If you’re only changing a few attributes on a class-based view, you can pass them into the `as_view()` method call itself:

```python
# Example
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('about/', TemplateView.as_view(template_name="about.html")),
]
```

I will change 4 view methods into class based views as a subclass of `ListView`.

```python
# blog/views.py
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

class ArchiveView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        return super(ArchiveView,self).get_queryset().filter(created_time__month=month,created_time__year=year)

class ArchiveView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        return super(ArchiveView,self).get_queryset().filter(created_time__month=month,created_time__year=year)


class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cat = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cat)

class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        t = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=t)

```

Don't forget to change url config:

```python
# blog/urls.py

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'), #
    path('posts/<int:pk>/', views.detail, name='detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('archives/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive'), #
    path('recent_posts', views.recent_posts, name='recent_posts'),
    path('categories/<int:pk>/', views.CategoryView.as_view(), name='category'), #
    path('tags/<int:pk>/', views.TagView.as_view(), name='tag'), #
]
```


Summary:

- `ListView` provides interface to get a list of data and rendering page.
- `DetailView` provides interface to get a specific data and rendering page.

## 15. Pagination

Django provides a demo for pagination:

```python
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
 
def listing(request):
    contact_list = Contacts.objects.all()
    paginator = Paginator(contact_list, 25) # 每页显示 25 个联系人
 
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果用户请求的页码号不是整数，显示第一页
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果用户请求的页码号超过了最大页码号，显示最后一页
        contacts = paginator.page(paginator.num_pages)
 
    return render(request, 'list.html', {'contacts': contacts})
```

`ListView` has already implemented this function. User only needs to use `paginate_by = ?` to call it:

```python
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    paginate_by = 1
```

It sends the following variables:

- `paginator`, the instance of paginator
- `page_obj`
- `is_paginated`, whether it is paginated, only over 2 pages will be treated as pagination.
- `object_list`

The simplest pagination:

```html
{% if is_paginated %}
                <div class="pagination-simple">
                {% if page_obj.has_previous %}
                    <a href="?page={{ page_obj.previous_page_number }}">previous</a>
                {% endif %}

                <span class="current">{{ page_obj.number }} / {{ paginator.num_pages }} </span>

                {% if page_obj.has_next %}
                    <a href="?page={{ page_obj.next_page_number }}">next</a>
                {% endif %}
                </div>
                {% endif %}

```

## 16. django-pure-pagination

[django-pure-pagination](https://github.com/jamespacileo/django-pure-pagination) is a third-party extension using for pagination. 

```shell
pip3 install django-pure-pagination
```

Then register it in `INSTALLED_APPS` and config:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog.apps.BlogConfig',
    'comments.apps.CommentsConfig',
    'pure_pagination',
]

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 4, # 分页条当前页前后应该显示的总页数（两边均匀分布，因此要设置为偶数），
    'MARGIN_PAGES_DISPLAYED': 2, # 分页条开头和结尾显示的页数
    'SHOW_FIRST_PAGE_WHEN_INVALID': True, # 当请求了不存在页，显示第一页
}
```

Change `IndexView`:
```python
from pure_pagination.mixins import PaginationMixin

class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10
```

Then insert following code in which you want the navigation bar.

## 17. Global search

Use following code to control the logic of search:

```python
# blog/views.py
def search(request):
    keywords = request.GET.get('keywords')

    if not keywords:
        error_msg = 'Please input keywords'
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    post_list = Post.objects.filter(Q(title__icontains=keywords) | Q(body__icontains=keywords))
    return render(request, 'blog/index.html', context={'post_list': post_list})
```

The corresponding form:
```html
<div id="search-form" class="search-form">
                        <form role="search" method="get" id="searchform" action="{% url 'blog:search'  %}">
                            <input type="search" placeholder="search" name='keywords' required>
                            <button type="submit"><span class="ion-ios-search-strong"></span></button>
                        </form>
                    </div>
```

Don't forget to config url.

More QuerySet API can be found [here](https://docs.djangoproject.com/en/2.2/ref/models/querysets/)

## 18. RSS

[RSS(Really Simple Syndication)](https://en.wikipedia.org/wiki/RSS) is a format to describe and synchronize website. It packs website as XML which satisfies RSS standard.

Django provides `Feed` to support this function.

Create new file `blog/feeds.py`


