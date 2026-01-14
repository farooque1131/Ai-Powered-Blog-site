from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from datetime import datetime
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.


class LoginData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    login_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class Tag(models.Model):
    name = models.CharField(max_length=50) 
    def __str__(self):
        # show the title on the admin panel
        return self.name


class Post (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = CKEditor5Field('Content', config_name='default')
    tag = models.ManyToManyField(Tag, blank=False,null=True)
    summary = models.TextField(blank=True, null=True)
    post_image = models.ImageField(upload_to='post_media/',default='post_media/1.png')
    published_date = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)  # NEW
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

# str function is used to show the name of the objects instead of id
    def __str__(self):
        # show the title on the admin panel
        return self.title


class EntryForm (models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    contact_number = models.CharField(max_length=10)
    password = models.CharField(max_length=100)    

    def __str__(self):
        return self.name
    

class Comment(models.Model):
    comment = models.TextField() 
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name="comments")     
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f"{self.user} - {self.comment[:30]}"
    
class InquiryForm(models.Model):
    name= models.CharField(max_length=50)
    email= models.EmailField(max_length=254)
    subject= models.CharField(max_length=100)
    message=models.TextField()
    created_at=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profiles/', default='profiles/default.png')
    about_me = models.TextField(blank=True)

    def __str__(self):
        return self.user.username