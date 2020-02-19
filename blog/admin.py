from django.contrib import admin

from .models import Tag, Post, Category

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']
    fields = ['title', 'body', 'excerpt', 'category', 'tags']
    

    def save_model(self, request, obj, form, change):
        obj.author = request.user # In my case, request.user is admin
        super().save_model(request, obj, form, change)

admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)