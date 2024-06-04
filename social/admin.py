from django.contrib import admin
from .models import Post, Comment, UserProfile, Notification, Thread, Message

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'body', 'created_on')
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'comment', 'created_on')
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'location', 'bio', 'birth_date')
    
admin.site.register(Notification)
admin.site.register(Thread)
admin.site.register(Message)
