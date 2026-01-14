from rest_framework import serializers
from .models import Tag, Post, EntryForm, Comment, LoginData

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = "__all__"

class EntryFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryForm
        fields = "__all__"

