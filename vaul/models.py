from django.db import models
from django.contrib.auth.models import User

class PasswordEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site_name = models.CharField(max_length=100)
    site_url = models.URLField()
    username = models.CharField(max_length=100)
    encrypted_password = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
