from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
import markdown
from comments.models import Comment
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.views.generic import ListView
from pure_pagination.mixins import PaginationMixin
from django.contrib import messages
from django.db.models import Q
 
# def index(request):
#     post_list = Post.objects.all().order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})
class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    paginate_by = 10


def about(request):
    return render(request, 'blog/about.html', context={})

def contact(request):
    return render(request, 'blog/contact.html', context={})

def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    post.counts += 1 # count of view

    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    post.body = md.convert(post.body)
    post.toc = md.toc
 
    return render(request, 'blog/detail.html', context={'post': post})


# def archive(request, year, month):
#     post_list = Post.objects.filter(created_time__year=year,
#                                     created_time__month=month
#                                     ).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})
class ArchiveView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        return super(ArchiveView,self).get_queryset().filter(created_time__month=month,created_time__year=year)

def recent_posts(request):
    post_list = Post.objects.all().order_by('-created_time')[:10]
    return render(request, 'blog/index.html', context={'post_list' : post_list})

# def category(request, pk):
#     # 记得在开始部分导入 Category 类
#     cat = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cat).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})
class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cat = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cat)


# def tag(request, pk):
#     # 记得在开始部分导入 Tag 类
#     t = get_object_or_404(Tag, pk=pk)
#     post_list = Post.objects.filter(tags=t).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        t = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=t)

def search(request):
    keywords = request.GET.get('keywords')

    if not keywords:
        error_msg = 'Please input keywords'
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    post_list = Post.objects.filter(Q(title__icontains=keywords) | Q(body__icontains=keywords))
    return render(request, 'blog/index.html', context={'post_list': post_list})
