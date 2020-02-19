from django.contrib.syndication.views import Feed
 
from .models import Post

class AllPostsRssFeed(Feed):
    title = "Zeping's Home"
    link = '/'
    Description = "All Articles in Zeping's Blog"

    def items(self):
        return Post.objects.all()

    def item_title(self, item):
        return "[{}] {}".format(item.category, item.title)
        
    def item_description(self, item):
        return item.body_html