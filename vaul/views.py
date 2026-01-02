from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, time
import csv
from .models import PasswordEntry, RevealLog
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
    return redirect('home')

@login_required
def dashboard(request):
    entries_list = PasswordEntry.objects.filter(user=request.user).order_by('-id')
    
    # Búsqueda
    search_query = request.GET.get('q', '').strip()
    if search_query:
        entries_list = entries_list.filter(
            Q(site_name__icontains=search_query) |
            Q(site_url__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    paginator = Paginator(entries_list, 12)  # 12 entradas por página (3x3 grid)
    
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, mostrar la primera página
        entries = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        entries = paginator.page(paginator.num_pages)
    
    return render(request, 'vaul/dashboard.html', {
        'entries': entries,
        'search_query': search_query
    })

@login_required
def add_password(request):
    if request.method == 'POST':
        site_name = request.POST.get('site_name', '').strip()
        site_url = request.POST.get('site_url', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not site_name or not site_url or not username or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'vaul/add_password.html', {
                'site_name': site_name,
                'site_url': site_url,
                'username': username,
            })

        if len(site_url) > 2048:
            messages.error(request, 'La URL es demasiado larga (máximo 2048 caracteres).')
            return render(request, 'vaul/add_password.html', {
                'site_name': site_name,
                'site_url': site_url,
                'username': username,
            })

        encrypted = encrypt_password(password)
        PasswordEntry.objects.create(
            user=request.user,
            site_name=site_name,
            site_url=site_url,
            username=username,
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
def delete_password(request, entry_id: int):
    if request.method != 'POST':
        return HttpResponseForbidden('Método no permitido')
    entry = get_object_or_404(PasswordEntry, id=entry_id)
    if entry.user_id != request.user.id:
        return HttpResponseForbidden('No autorizado')
    entry.delete()
    messages.success(request, 'Entrada eliminada correctamente.')
    return redirect('dashboard')

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
        # Log de auditoría
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')
        RevealLog.objects.create(user=request.user, entry=entry, ip_address=ip, user_agent=ua)
        return JsonResponse({'password': decrypted})
    except Exception:
        return JsonResponse({'error': 'No se pudo descifrar'}, status=400)

@login_required
def reveal_logs(request):
    logs = RevealLog.objects.filter(user=request.user).select_related('entry')

    start_str = request.GET.get('start', '').strip()
    end_str = request.GET.get('end', '').strip()

    start_dt = None
    end_dt = None
    try:
        if start_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            start_dt = timezone.make_aware(datetime.combine(start_date, time.min))
        if end_str:
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            end_dt = timezone.make_aware(datetime.combine(end_date, time.max))
    except Exception:
        start_dt = None
        end_dt = None

    if start_dt:
        logs = logs.filter(revealed_at__gte=start_dt)
    if end_dt:
        logs = logs.filter(revealed_at__lte=end_dt)

    if request.GET.get('format') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="reveal_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(['Entrada', 'Usuario', 'Revelado en', 'IP', 'User-Agent'])
        for log in logs:
            writer.writerow([
                f"{log.entry.site_name} ({log.entry.username})",
                request.user.username,
                timezone.localtime(log.revealed_at).strftime('%Y-%m-%d %H:%M:%S'),
                log.ip_address or '',
                (log.user_agent or '')[:500]
            ])
        return response

    context = {
        'logs': logs,
        'start': start_str,
        'end': end_str,
    }
    return render(request, 'vaul/reveal_logs.html', context)
