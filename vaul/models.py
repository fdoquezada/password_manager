from django.db import models
from django.contrib.auth.models import User

class PasswordEntry(models.Model):
    CATEGORY_CHOICES = [
        ('work', 'Trabajo'),
        ('personal', 'Personal'),
        ('social', 'Redes Sociales'),
        ('finance', 'Finanzas'),
        ('shopping', 'Compras'),
        ('entertainment', 'Entretenimiento'),
        ('education', 'Educación'),
        ('other', 'Otro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site_name = models.CharField(max_length=100)
    site_url = models.URLField(max_length=2048)
    username = models.CharField(max_length=100)
    encrypted_password = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    notes = models.TextField(blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-created_at',)
        verbose_name_plural = 'Password Entries'

# Create your models here.

class RevealLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey(PasswordEntry, on_delete=models.CASCADE)
    revealed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('-revealed_at',)
