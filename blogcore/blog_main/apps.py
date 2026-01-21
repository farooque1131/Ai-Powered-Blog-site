from django.apps import AppConfig
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
import os   

def create_default_superuser(sender, **kwargs):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    admin_username = os.getenv("ADMIN_USERNAME", "farooque")
    admin_password = os.getenv("ADMIN_PASSWORD", "Farooque@123")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")

    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        print("✅ Auto superuser created")


class BlogMainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_main'

    def ready(self):
        post_migrate.connect(create_default_superuser, sender=self)
        import blog_main.signals
