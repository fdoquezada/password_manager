from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from .models import PasswordEntry
from .utils import encrypt_password, decrypt_password

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'vaul/home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'vaul/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm  = request.POST.get('confirm_password', '').strip()

        if not username:
            messages.error(request, 'Debes ingresar un nombre de usuario.')
            return render(request, 'vaul/register.html', {'username_value': username})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe. Elige otro nombre de usuario.')
            return render(request, 'vaul/register.html', {'username_value': username})

        if not password or not confirm:
            messages.error(request, 'Debes ingresar y confirmar la contraseña.')
            return render(request, 'vaul/register.html', {'username_value': username})

        if password != confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'vaul/register.html', {'username_value': username})

        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'vaul/register.html', {'username_value': username})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        messages.success(request, 'Cuenta creada correctamente. ¡Bienvenido!')
        return redirect('dashboard')
    return render(request, 'vaul/register.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    entries = PasswordEntry.objects.filter(user=request.user)
    return render(request, 'vaul/dashboard.html', {'entries': entries})

@login_required
def add_password(request):
    if request.method == 'POST':
        encrypted = encrypt_password(request.POST['password'])
        PasswordEntry.objects.create(
            user=request.user,
            site_name=request.POST['site_name'],
            site_url=request.POST['site_url'],
            username=request.POST['username'],
            encrypted_password=encrypted
        )
        messages.success(request, 'Contraseña guardada correctamente.')
        return redirect('dashboard')
    return render(request, 'vaul/add_password.html')

@login_required
def edit_password(request, entry_id: int):
    entry = get_object_or_404(PasswordEntry, id=entry_id)
    if entry.user_id != request.user.id:
        return HttpResponseForbidden('No autorizado')
    if request.method == 'POST':
        site_name = request.POST.get('site_name', '').strip()
        site_url = request.POST.get('site_url', '').strip()
        username = request.POST.get('username', '').strip()
        new_password = request.POST.get('password', '')

        entry.site_name = site_name or entry.site_name
        entry.site_url = site_url or entry.site_url
        entry.username = username or entry.username
        if new_password:
            entry.encrypted_password = encrypt_password(new_password)
        entry.save()
        messages.success(request, 'Entrada actualizada correctamente.')
        return redirect('dashboard')
    # No enviamos la contraseña en claro. Mostramos campos para reemplazar.
    return render(request, 'vaul/edit_password.html', {'entry': entry})

@login_required
def help_view(request):
    return render(request, 'vaul/help.html')

@login_required
def reveal_password(request, entry_id: int):
    if request.method != 'POST':
        return HttpResponseForbidden('Método no permitido')
    entry = get_object_or_404(PasswordEntry, id=entry_id)
    if entry.user_id != request.user.id:
        return HttpResponseForbidden('No autorizado')
    try:
        decrypted = decrypt_password(entry.encrypted_password)
        return JsonResponse({'password': decrypted})
    except Exception:
        return JsonResponse({'error': 'No se pudo descifrar'}, status=400)
