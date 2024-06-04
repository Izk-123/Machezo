from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import View
from django.views.generic.edit import UpdateView, DeleteView
from .models import *
from .forms import *

#######################################################################################################################   
                                            #views for post
#######################################################################################################################   
@login_required
def postListView(request):
    logged_in_user = request.user
    posts = Post.objects.filter(
        author__profile__followers__in=[logged_in_user.id]
        )
    form = PostForm()
    share_form = SharedForm()
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            new_post.create_tags()
            
            for f in files:
                img = Image(image=f)
                img.save()
                new_post.image.add(img)
            
            new_post.save()
                
            return redirect('posts')
        else:
            form = PostForm()
            
    context = {
        'posts': posts,
        'form': form,
        'shareform': share_form,
    }
    
    template_url = 'social/posts.html'
    return render(request, template_url, context)

class SharedPostView(View):
    def Post(self, request, pk, *args, **kwargs):
        original_post = Post.objects.get(pk=pk)
        form = SharedForm(request.POST)
        
        if form.is_valid():
            new_post = Post(
                shared_body = self.request.POST.get('body'),
                author = original_post.author,
                shared_user = request.user,
                body = original_post.body,
                created_on = original_post.created_on,
                shared_on = timezone.now(),
            )
            new_post.save()
            new_post.create_tags()
            
            for img in original_post.image.all():
                new_post.image.add(img)
            new_post.save()
        
        return redirect('posts')

@login_required
def postDetailView(request, pk=None):
    post = get_object_or_404(Post, pk=pk)
    
    form = CommentForm()
    new_comment = None
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            notification = Notification.objects.create(notification_type=2, from_user=new_comment.author, to_user=post.author, post=new_comment.post)
            new_comment.save()
            new_comment.create_tags()
            
            return redirect('post', post.pk)
        else:
            form = CommentForm()
            
    comments = Comment.objects.filter(post=post).order_by('-created_on')
    
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    template_url = 'social/post.html'
    return render(request, template_url, context)

def commentReplyView(request, post_pk, pk):
    post = Post.objects.get(pk=post_pk)
    parent_comment = Comment.objects.get(pk=pk)
    form = CommentForm()
    
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.parent = parent_comment
        new_comment.save()
        new_comment.create_tags()
        
    notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)
    return redirect('post', pk=post_pk)
    
class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body', 'picture']
    template_name = 'social/post_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post', kwargs={'pk':pk})
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('posts')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'
    
    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post', kwargs={'pk':pk})
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    
#######################################################################################################################   
                                            # view for profile
#######################################################################################################################                                                
@login_required
def profileView(request, pk):
    profile = UserProfile.objects.get(pk=pk)
    user = profile.user
    posts = Post.objects.filter(author=user) 
    
    followers = profile.followers.all()
    
    if len(followers) == 0:
        is_following = False
        
    for follower in followers:
        if follower == request.user:
            is_following = True
            break
        else:
            is_following = False
         
    number_of_followers = len(followers)
    
    context = {
        'user': user,
        'profile': profile,
        'posts': posts,
        'number_of_followers': number_of_followers,
        'is_following': is_following,
    }
    
    template_name = 'social/profile.html'
    
    return render(request, template_name, context)

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['first_name', 'middle_name', 'last_name', 'location', 'bio', 'birth_date', 'picture']
    template_name = 'social/profile_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk':pk})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user
    
#######################################################################################################################   
                                            # views for following
#######################################################################################################################                                               
@login_required
def addFollowersView(request, pk):
    profile = UserProfile.objects.get(pk=pk)
    profile.followers.add(request.user)
    
    notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)
    return redirect('profile', pk=profile.pk)

@login_required
def removeFollowersView(request, pk):
    profile = UserProfile.objects.get(pk=pk)
    profile.followers.remove(request.user)
    
    return redirect('profile', pk=profile.pk)

@login_required
def addLikes(request, pk):
    post = Post.objects.get(pk=pk)
    is_dislike = False
    
    for dislike in post.dislikes.all():
        if dislike == request.user:
            is_dislike = True
            break
    if is_dislike:
        post.dislikes.remove(request.user)
        
    is_like = False
    
    for like in post.likes.all():
        if like == request.user:
            is_like = True
            break
    
    if not is_like:
        post.likes.add(request.user)
        notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)
        
    if is_like:
        post.likes.remove(request.user)
        
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)
        
@login_required
def addDislikes(request, pk):
    post = Post.objects.get(pk=pk)
    is_like = False
    
    for like in post.likes.all():
        if like == request.user:
            is_like = True
            break
    
    if is_like:
        post.likes.remove(request.user)
        
    is_dislike = False
    
    for dislike in post.dislikes.all():
        if dislike == request.user:
            is_dislike = True
            break
    
    if not is_dislike:
        post.dislikes.add(request.user)
        
    if is_dislike:
        post.dislikes.remove(request.user)
        
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

@login_required
def addCommentLikes(request, pk):
    comment = Comment.objects.get(pk=pk)
    is_dislike = False
    
    for dislike in comment.dislikes.all():
        if dislike == request.user:
            is_dislike = True
            break
    if is_dislike:
        comment.dislikes.remove(request.user)
        
    is_like = False
    
    for like in comment.likes.all():
        if like == request.user:
            is_like = True
            break
    
    if not is_like:
        comment.likes.add(request.user)
        notification = Notification.objects.create(
            notification_type=1,
            from_user=request.user, 
            to_user=comment.author, 
            comment=comment
            )
        
    if is_like:
        comment.likes.remove(request.user)
        
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)
        
@login_required
def addCommentDislikes(request, pk):
    comment = Comment.objects.get(pk=pk)
    is_like = False
    
    for like in comment.likes.all():
        if like == request.user:
            is_like = True
            break
    
    if is_like:
        comment.likes.remove(request.user)
        
    is_dislike = False
    
    for dislike in comment.dislikes.all():
        if dislike == request.user:
            is_dislike = True
            break
    
    if not is_dislike:
        comment.dislikes.add(request.user)
        
    if is_dislike:
        comment.dislikes.remove(request.user)
        
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

def userSearch(request):
    query = request.GET.get('query')
    profile_list = UserProfile.objects.filter(
        Q(user__username__icontains=query)
    )
    
    context = {
        'profile_list': profile_list,
    }
    template_url = 'social/search.html'
    
    return render(request, template_url, context)

def listFollowers(request, pk):
    profile = UserProfile.objects.get(pk=pk)
    followers = profile.followers.all()
    
    template_url = 'social/followers_list.html'
    context = {
        'profile': profile,
        'followers': followers,
    }
    
    return render(request, template_url, context)


#######################################################################################################################   
                                            #Views for notification
#######################################################################################################################
def postNotifications(request, notification_pk, post_pk):
    notification = Notification.objects.get(pk=notification_pk)
    post = Post.objects.get(pk=post_pk)
    
    notification.user_has_seen = True
    notification.save()
    
    return redirect('post', pk=post_pk)

def followNotifications(request, notification_pk, follow_pk):
    notification = Notification.objects.get(pk=notification_pk)
    user = UserProfile.objects.get(pk=follow_pk)
    
    notification.user_has_seen = True
    notification.save()
    
    return redirect('profile', pk=follow_pk)

def threadNotifications(request, notification_pk, thread_pk):
    notification = Notification.objects.get(pk=notification_pk)
    thread = Thread.objects.get(pk=thread_pk)
    
    notification.user_has_seen = True
    notification.save()
    
    return redirect('thread', pk=thread_pk)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        notification.user_has_seen = True
        notification.save()
        
        return HttpResponse('success', content_type='text/plain')
    

#######################################################################################################################   
                                            #view for DMs
######################################################################################################################
def listThreads(request):
    threads = Thread.objects.filter(Q(user=request.user) | Q(receiver=request.user))
    
    template_url = 'social/inbox.html'
    context = {
        'threads': threads,
    }
    return render(request, template_url, context)
    
class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        
        context = {
            'form': form,
        }
        
        template_url = 'social/create_thread.html'
        return render(request,template_url, context)
    
    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username =request.POST.get('username')
        
        try:
            receiver = User.objects.get(username=username)
            if Thread.objects.filter(user=request.user, receiver=receiver).exists():
                thread = Thread.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif Thread.objects.filter(user=receiver, receiver=request.user).exists():
                thread = Thread.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)
            
            if form.is_valid():
                thread = Thread(
                    user =request.user,
                    receiver = receiver
                )
                thread.save()
                return redirect('thread', pk=thread.pk)
        except:
            messages.error(request, 'Invalid username ')
            return redirect('create-thread')
        
class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = Thread.objects.get(pk=pk)
        message_list = Message.objects.filter(thread__pk__contains=pk)
        
        context = {
            'thread': thread,
            'form': form,
            'messages': message_list,
        }
        
        template_url= 'social/thread.html'
        
        return render(request, template_url, context)
    
class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        form = MessageForm(request.POST, request.FILES)
        thread = Thread.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver
            
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.receiver = receiver
            message.save()
             
        notification = Notification.objects.create(
            notification_type=4,
            from_user=request.user,
            to_user=receiver,
            thread= thread
            )
        return redirect('thread', pk=pk)
    
def explore(request):
    explore_form = ExploreForm()
    query = request.GET.get('query')
    tag = Tag.objects.filter(name=query).first()
    
    if tag:
        posts = Post.objects.filter(tags_in=[tag])
    else:
        posts = Post.objects.all()
        
    if request.method == 'POST':
        explore_form = ExploreForm(request.POST)
        if explore_form.is_valid():
            query = explore_form.cleaned_data['query']
            tag = Tag.objects.filter(name=query).first()
            posts = None
            if tag:
                posts = Post.objects.filter(tags_in=[tag])
            return HttpResponseRedirect(f'/social/explore?query={query}')
    
    context = {
        'tag': tag,
        'posts': posts,
        'exploreform': explore_form,
    }
    template_url = 'social/explore.html'
    return render(request, template_url, context)

class Explore(View):
    def get(self, request, *args, **kwargs):
        explore_form = ExploreForm()
        query = self.request.GET.get('query')
        tag = Tag.objects.filter(name=query).first()
        
        if tag:
            posts = Post.objects.filter(tags__in=[tag])
        else:
            posts = Post.objects.all()
            
        context = {
            'tag': tag,
            'posts': posts,
            'exploreform': explore_form,
        }
        template_url = 'social/explore.html'
        return render(request, template_url, context)
    
    def post(self, request, *args, **kwargs):
        explore_form = ExploreForm(request.POST)
        if explore_form.is_valid():
            query = explore_form.cleaned_data['query']
            tag = Tag.objects.filter(name=query).first()
            posts = None
            if tag:
                posts = Post.objects.filter(tags__in=[tag])
            if posts:
                context = {
                    'tag': tag,
                    'posts': posts,
                }
            else:
               context = {
                    'tag': tag,
                    'posts': posts,
                } 
            return HttpResponseRedirect(f'/social/explore?query={query}')
        return HttpResponseRedirect('social/explore')