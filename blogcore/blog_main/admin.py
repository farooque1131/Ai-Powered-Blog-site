from django.contrib import admin
from .models import Tag, Post, EntryForm, Comment, LoginData,InquiryForm
# Register your models here.
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(InquiryForm)