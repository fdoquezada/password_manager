from django.contrib import admin
from .models import PasswordEntry

# Register your models here.

@admin.register(PasswordEntry)
class PasswordEntryAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_url', 'username', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('site_name', 'site_url', 'username')
    ordering = ('-created_at',)
    list_per_page = 10
    # Enlaces solo en 'site_name' para evitar conflicto con list_editable
    list_display_links = ('site_name',)
    # Editables en lista (no pueden estar en list_display_links)
    list_editable = ('site_url', 'username')