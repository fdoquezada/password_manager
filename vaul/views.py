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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Por favor, ingresa tu usuario y contraseña.')
            return render(request, 'vaul/login.html', {'username_value': username})
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Por favor, intenta de nuevo.')
            return render(request, 'vaul/login.html', {'username_value': username})
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
    
    # Estadísticas
    total_entries = PasswordEntry.objects.filter(user=request.user).count()
    category_stats = {}
    for choice in PasswordEntry.CATEGORY_CHOICES:
        category_stats[choice[0]] = PasswordEntry.objects.filter(user=request.user, category=choice[0]).count()
    
    # Detección de contraseñas duplicadas y débiles
    all_entries = PasswordEntry.objects.filter(user=request.user)
    password_hashes = {}
    weak_passwords = []
    duplicate_passwords = []
    
    for entry in all_entries:
        try:
            decrypted = decrypt_password(entry.encrypted_password)
            # Detectar contraseñas débiles (menos de 8 caracteres o solo números/letras)
            if len(decrypted) < 8 or (decrypted.isdigit() or decrypted.isalpha()):
                weak_passwords.append(entry.id)
            
            # Detectar duplicados
            if decrypted in password_hashes:
                if entry.id not in duplicate_passwords:
                    duplicate_passwords.append(entry.id)
                if password_hashes[decrypted] not in duplicate_passwords:
                    duplicate_passwords.append(password_hashes[decrypted])
            else:
                password_hashes[decrypted] = entry.id
        except:
            pass  # Si no se puede descifrar, omitir
    
    # Búsqueda
    search_query = request.GET.get('q', '').strip()
    if search_query:
        entries_list = entries_list.filter(
            Q(site_name__icontains=search_query) |
            Q(site_url__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    # Filtro por categoría
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        entries_list = entries_list.filter(category=category_filter)
    
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
        'search_query': search_query,
        'category_filter': category_filter,
        'total_entries': total_entries,
        'category_stats': category_stats,
        'weak_passwords': weak_passwords,
        'duplicate_passwords': duplicate_passwords,
        'category_choices': PasswordEntry.CATEGORY_CHOICES,
    })

@login_required
def add_password(request):
    if request.method == 'POST':
        site_name = request.POST.get('site_name', '').strip()
        site_url = request.POST.get('site_url', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        category = request.POST.get('category', 'other')
        notes = request.POST.get('notes', '').strip()

        if not site_name or not site_url or not username or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'vaul/add_password.html', {
                'site_name': site_name,
                'site_url': site_url,
                'username': username,
                'notes': notes,
            })

        if len(site_url) > 2048:
            messages.error(request, 'La URL es demasiado larga (máximo 2048 caracteres).')
            return render(request, 'vaul/add_password.html', {
                'site_name': site_name,
                'site_url': site_url,
                'username': username,
                'notes': notes,
            })

        encrypted = encrypt_password(password)
        PasswordEntry.objects.create(
            user=request.user,
            site_name=site_name,
            site_url=site_url,
            username=username,
            encrypted_password=encrypted,
            category=category,
            notes=notes[:500] if notes else None
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
        category = request.POST.get('category', 'other')
        notes = request.POST.get('notes', '').strip()

        entry.site_name = site_name or entry.site_name
        entry.site_url = site_url or entry.site_url
        entry.username = username or entry.username
        entry.category = category
        entry.notes = notes[:500] if notes else None
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

@login_required
def export_passwords(request):
    """Exporta todas las contraseñas del usuario en formato JSON"""
    if request.method != 'GET':
        return HttpResponseForbidden('Método no permitido')
    
    entries = PasswordEntry.objects.filter(user=request.user).order_by('-created_at')
    import json
    from datetime import datetime
    
    data = {
        'export_date': timezone.now().isoformat(),
        'total_entries': entries.count(),
        'entries': []
    }
    
    for entry in entries:
        try:
            decrypted = decrypt_password(entry.encrypted_password)
            data['entries'].append({
                'site_name': entry.site_name,
                'site_url': entry.site_url,
                'username': entry.username,
                'password': decrypted,
                'category': entry.category,
                'notes': entry.notes or '',
                'created_at': entry.created_at.isoformat(),
            })
        except:
            pass  # Omitir entradas que no se pueden descifrar
    
    response = HttpResponse(
        json.dumps(data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="passwords_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@login_required
def import_passwords(request):
    """Importa contraseñas desde un archivo JSON"""
    if request.method != 'POST':
        return HttpResponseForbidden('Método no permitido')
    
    if 'file' not in request.FILES:
        messages.error(request, 'No se proporcionó ningún archivo.')
        return redirect('dashboard')
    
    import json
    
    try:
        file = request.FILES['file']
        content = file.read().decode('utf-8')
        data = json.loads(content)
        
        if 'entries' not in data:
            messages.error(request, 'Formato de archivo inválido.')
            return redirect('dashboard')
        
        imported = 0
        skipped = 0
        
        for entry_data in data['entries']:
            try:
                site_name = entry_data.get('site_name', '').strip()
                site_url = entry_data.get('site_url', '').strip()
                username = entry_data.get('username', '').strip()
                password = entry_data.get('password', '')
                category = entry_data.get('category', 'other')
                notes = entry_data.get('notes', '').strip()
                
                if not site_name or not site_url or not username or not password:
                    skipped += 1
                    continue
                
                # Verificar si ya existe (evitar duplicados)
                if PasswordEntry.objects.filter(
                    user=request.user,
                    site_name=site_name,
                    site_url=site_url,
                    username=username
                ).exists():
                    skipped += 1
                    continue
                
                encrypted = encrypt_password(password)
                PasswordEntry.objects.create(
                    user=request.user,
                    site_name=site_name,
                    site_url=site_url,
                    username=username,
                    encrypted_password=encrypted,
                    category=category,
                    notes=notes[:500] if notes else None
                )
                imported += 1
            except Exception as e:
                skipped += 1
                continue
        
        messages.success(request, f'Importación completada: {imported} entradas importadas, {skipped} omitidas.')
    except json.JSONDecodeError:
        messages.error(request, 'El archivo no es un JSON válido.')
    except Exception as e:
        messages.error(request, f'Error al importar: {str(e)}')
    
    return redirect('dashboard')
