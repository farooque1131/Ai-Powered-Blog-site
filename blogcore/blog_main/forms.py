from django import forms
from .models import Comment, Post
from django_ckeditor_5.widgets import CKEditor5Widget

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your comment...'
            })
        }   

class PostForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default')
    )
    class Meta:
        model = Post
        fields = ['title', 'slug', 'description','tag', 'post_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'tag': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 5  # optional: shows 5 items at once
            }),
            'post_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }