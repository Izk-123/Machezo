from django.urls import path
from . import views

urlpatterns = [
    #urls for post
    path('', views.postListView, name='posts'),
    path('explore', views.Explore.as_view(), name='explore'),
    path('post/<int:pk>/', views.postDetailView, name='post'),
    path('post/edit/<int:pk>/', views.PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('post/comment/<int:pk>/like', views.addCommentLikes, name='comment-like'),
    path('post/comment/<int:pk>/dislike', views.addCommentDislikes, name='comment-dislike'),
    path('post/<int:post_pk>/comment/<int:pk>/reply', views.commentReplyView, name='comment-reply'),
    path('post/<int:pk>/like', views.addLikes, name='like'),
    path('post/<int:pk>/dislike', views.addDislikes, name='dislike'),
    path('post/<int:pk>/share', views.SharedPostView.as_view(), name='share-post'),
    #urls for profile
    path('profile/<int:pk>/', views.profileView, name='profile'),
    path('profile/edit/<int:pk>/', views.ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/', views.listFollowers, name='list-followers'),
    path('profile/<int:pk>/followers/add', views.addFollowersView, name='add-followers'),
    path('profile/<int:pk>/followers/remove', views.removeFollowersView, name='remove-followers'),
    #urls for search
    path('search/', views.userSearch, name='profile-search'),
    #url for notifications
    path('notification/<int:notification_pk>/post/<int:post_pk>', views.postNotifications, name='post-notification'),
    path('notification/<int:notification_pk>/profile/<int:follow_pk>', views.followNotifications, name='follow-notification'),
    path('notification/<int:notification_pk>/thread/<int:thread_pk>', views.threadNotifications, name='thread-notification'),
    path('notification/delete/<int:notification_pk>/', views.RemoveNotification.as_view(), name='delete-notification'),
    #urls for DMs
    path('inbox/', views.listThreads, name='inbox'),
    path('inbox/create-thread', views.CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/', views.ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message', views.CreateMessage.as_view(), name='create-message'),
]