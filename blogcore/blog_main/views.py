from django.shortcuts import render
from rest_framework import generics
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.core.paginator import Paginator
from blog_main.serializers import PostSerializer, TagSerializer, EntryFormSerializer, CommentSerializer
from django.contrib.auth.models import User
from blog_main.models import Tag, Post, EntryForm, Comment, LoginData, InquiryForm, Profile
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required
from .utils import generate_summary,is_abusive, unauthorized_user
from django.utils.html import strip_tags
# import google.generativeai as genai
import requests
# Create your views here.


def home(request):
    post = Post.objects.all().order_by("-published_date")[:6]
    
    return render(request, 'front-end/index.html',{'post':post})
def inquiry_form(request):
    if request.method == "POST":
        InquiryForm.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject = request.POST.get('subject'),
            message = request.POST.get('message'))
        messages.success(request, "Message sent successfully!")
         # redirect back to whichever page the user was on
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('/')
        
def about_us(request):
    return render(request, 'front-end/about.html')


# def generate_summary(text):
#     model = genai.GenerativeModel("gemini-2.5-flash")
#     response = model.generate_content(f"Summarize this blog content in 2-3 lines:\n\n{text}")
    # return response.text

def content(request, slug):
    print("Slug:", slug)
    blog_content = get_object_or_404(Post, slug=slug)
    # summary = generate_summary(blog_content.description)
    if not blog_content.summary:
        clean_text = strip_tags(blog_content.description)
        blog_content.summary = generate_summary(clean_text)
        blog_content.save(update_fields=['summary'])
    summary = blog_content.summary
    print("Found:", blog_content)
    blog_content.views += 1
    blog_content.save(update_fields=['views'])
    # store viewed tags with frequency
    viewed_tags = request.session.get('viewed_tags', {})

    for tag_id in blog_content.tag.values_list('id', flat=True):
        tag_id = str(tag_id)
        viewed_tags[tag_id] = viewed_tags.get(tag_id, 0) + 1

    request.session['viewed_tags'] = viewed_tags
    comments = Comment.objects.filter(
        post=blog_content,
        parent__isnull=True
    ).select_related('user').prefetch_related('replies')

    form = CommentForm()

    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment_text = form.cleaned_data['comment']

                if is_abusive(comment_text):
                    messages.error(request, "Your comment contains abusive language.")
                    return redirect(request.path)
                messages.success(request, "Comment posted successfully.")
                parent_id = request.POST.get('parent_id')
                parent = Comment.objects.filter(id=parent_id).first()

                comment = form.save(commit=False)
                comment.user = request.user
                comment.post = blog_content
                comment.parent = parent
                comment.save()

                return redirect(request.path)
        else:
            return redirect('login')

    return render(request, 'front-end/blog-post.html',{'blog_content':blog_content,'comments': comments,'form': form,'summary':summary})

def blogs(request):
    blog = Post.objects.all()
    search  = request.GET.get('search','')
    if search:
        blog = blog.filter(title__icontains=search)

    pages = Paginator(blog,6,orphans=0)
    pag_obj = request.GET.get('page',1)
    page_obj = pages.get_page(pag_obj)
      # session-based recommendation
    viewed_tags = request.session.get('viewed_tags', {})

    if viewed_tags:
        tag_ids = list(map(int, viewed_tags.keys()))

        recommended_posts = (
            Post.objects
            .filter(tag__in=tag_ids)
            .exclude(id__in=page_obj.object_list.values_list('id', flat=True))
            .annotate(match_count=Count('tag'))
            .order_by('-match_count', '-views')
            .distinct()[:4]
        )
    else:
        recommended_posts = Post.objects.order_by('-views')[:4]

    return render(request,'front-end/blog.html',{'page_obj':page_obj, 'search':search,'recommended_posts': recommended_posts})



def contact_us(request):
    return render(request, 'front-end/contact.html')

def authors(request):
    authors = Profile.objects.filter(
        user__isnull=False
    ).distinct()

    return render(request, 'front-end/team.html', {
        'authors': authors
    })

def register_form(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("register")
        
          # Correct: hash password
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        messages.success(request, "Your account is registered")
        return redirect("login")
    return render(request, "front-end/register.html")
@unauthorized_user
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 1️⃣ Authenticate using Django session login
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password")
            return render(request, "front-end/login.html")  # 🔑 KEY CHANGE 

        # 2️⃣ Get JWT tokens for API usage (optional but recommended)
        # token_url = request.build_absolute_uri(reverse("token_obtain_pair"))
        # response = requests.post(token_url, data={
        #     "username": username,
        #     "password": password
        # })

        # if response.status_code == 200:
        #     tokens = response.json()
        #     request.session["access"] = tokens["access"]
        #     request.session["refresh"] = tokens["refresh"]
        #     request.session["username"] = username
        login(request, user)
        messages.success(request, "Logged in successfully")
        return redirect("blogs")

        # If JWT fails
        # messages.error(request, "Invalid username or password")
        # return redirect("login")

    return render(request, "front-end/login.html")

def logout_user(request):
    logout(request)  # clears Django session authentication

    # Optional: clear JWT tokens from session
    request.session.pop("access", None)
    request.session.pop("refresh", None)
    request.session.pop("username", None)

    messages.success(request, "Logged out successfully")
    return redirect("login")
@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            try:
                post.save()
                form.save_m2m()  # 🔥 REQUIRED
                messages.success(request, "Post created successfully!")
                return redirect('profile')
            except Exception as e:
                # Catch unique slug error
                messages.error(request, "Slug must be unique! Please change it.")
                
        else:
            # Form validation failed (e.g., slug not unique)
            messages.error(request, "Please correct the errors below.")
            
    else:
        form = PostForm()

    return render(request, 'front-end/create-post.html', {'form': form})
@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id, user=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
           
            messages.success(request, "Post updated successfully")
            return redirect('profile')
    else:
        form = PostForm(instance=post)

    return render(request, 'front-end/create-post.html', {
        'form': form,
        'post': post
    })
@login_required
def delete_post(request, id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request")

    post = get_object_or_404(Post, id=id, user=request.user)
    post.delete()
    return redirect('profile')

@login_required
def profile_view(request, username=None):
    # 🔹 Decide whose profile to show
    if username:
        user_obj = get_object_or_404(User, username=username)
        is_owner = (user_obj == request.user)
    else:
        user_obj = request.user
        is_owner = True

    profile = get_object_or_404(Profile, user=user_obj)

    posts_list = Post.objects.filter(user=user_obj).order_by('-published_date')

    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    total_posts = posts_list.count()
    total_comments = Comment.objects.filter(post__user=user_obj).count()

    # 🔒 Allow update ONLY if owner
    if request.method == "POST" and is_owner:
        profile.about_me = request.POST.get('about_me')
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES.get('profile_image')
        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile')

    context = {
        'profile_user': user_obj,
        'profile': profile,
        'posts': posts,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'is_owner': is_owner,  # 🔥 key flag
    }

    return render(request, 'front-end/profile.html', context)


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
