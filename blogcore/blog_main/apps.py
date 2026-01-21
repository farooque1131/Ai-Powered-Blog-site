from django.apps import AppConfig
from django.contrib.auth.models import User
import os   

User = get_user_model()
class BlogMainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_main'
    
    def ready(self):
        import blog_main.signals
        try:
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

        except Exception as e:
            print("❌ Superuser creation skipped:", e)
    
