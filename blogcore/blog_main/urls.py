from django.urls import path
from .views import PostList, CommentList
from . import views 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('api/posts/',PostList.as_view(),name='posts'),
    path('api/comments',CommentList.as_view(),name="Comments"),
    path('home/',views.home,name='home'),
    path('profile/', views.profile_view, name='profile'), 
    path("profile/<str:username>/", views.profile_view, name="user_profile"),
    path('create-post/', views.create_post, name='create_post'),
    path('edit-post/<int:id>/', views.edit_post, name='edit_post'),
    path('delete/<int:id>/', views.delete_post, name='post_delete'),
    path('about/',views.about_us, name='aboutus'),
    # path('posts/',views.blog_post,name='blog_post'),
    path('blogs/',views.blogs,name='blogs'),
    path('contact/',views.contact_us,name='contact'),
    path('team/',views.authors,name='authors'),
    path('inquiry-from/',views.inquiry_form,name='inquiry-form'),
    path('blog/<slug:slug>/', views.content, name='blog_detail'),
    path("register/", views.register_form, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    
]
