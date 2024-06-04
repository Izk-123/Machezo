from django import forms
from .models import Post, Comment, Message, Thread

class PostForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say something on your mind...',
            '': '',
            
        })
    )
    
    image = forms.ImageField(
        label='',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
            'class': 'fa fa-file-photo-o',
            'aria-hidden': True
        })
        )
    class Meta:
        model = Post
        fields = ['body']
        
class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say something on your mind...',
            '': '',
            
        })
    )
    class Meta:
        model = Comment
        fields = ['comment']
        
class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)
    
class MessageForm(forms.ModelForm):
    body = forms.CharField(label='', max_length=100)
    image = forms.ImageField(required=False)
    
    class Meta:
        model = Message
        fields = ['body', 'image']

class SharedForm(forms.Form):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Say something on your mind...',
            '': '',
            
        })
    )
    
class ExploreForm(forms.Form):
    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Explore tags'
        })
    )