// Utilidad CSRF (Django)
export function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name + '=')) return decodeURIComponent(c.substring(name.length + 1));
    }
    return null;
}

// Toasts simples
export function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.right = '16px';
        container.style.bottom = '16px';
        container.style.display = 'grid';
        container.style.gap = '8px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    const el = document.createElement('div');
    el.textContent = message;
    el.style.padding = '10px 12px';
    el.style.borderRadius = '10px';
    el.style.border = '1px solid #1f2937';
    el.style.background = type === 'error' ? '#3f1d1d' : (type === 'success' ? '#022c22' : '#111827');
    el.style.color = type === 'error' ? '#fecaca' : (type === 'success' ? '#a7f3d0' : '#e5e7eb');
    container.appendChild(el);
    setTimeout(() => el.remove(), 2500);
}

// Copiar texto al portapapeles
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copiado al portapapeles', 'success');
    } catch (e) {
        showToast('No se pudo copiar', 'error');
    }
}

// Cálculo simple de fortaleza de contraseña
export function calculatePasswordStrength(password) {
    let score = 0;
    if (!password) return 0;
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1;
    if (/\d/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    return Math.min(score, 5);
}

export function attachPasswordStrengthMeter(inputSelector, meterSelector, labelSelector) {
    const input = document.querySelector(inputSelector);
    const meter = document.querySelector(meterSelector);
    const label = document.querySelector(labelSelector);
    if (!input || !meter || !label) return;
    const update = () => {
        const score = calculatePasswordStrength(input.value);
        meter.value = score;
        const texts = ['Muy débil', 'Débil', 'Aceptable', 'Buena', 'Fuerte', 'Muy fuerte'];
        label.textContent = texts[score] || 'Muy débil';
    };
    input.addEventListener('input', update);
    update();
}

export function attachPasswordToggle(toggleSelector, inputSelector) {
    const toggle = document.querySelector(toggleSelector);
    const input = document.querySelector(inputSelector);
    if (!toggle || !input) return;
    toggle.addEventListener('click', () => {
        input.type = input.type === 'password' ? 'text' : 'password';
        toggle.textContent = input.type === 'password' ? 'Mostrar' : 'Ocultar';
    });
}

export function preventDoubleSubmit(formSelector) {
    const form = document.querySelector(formSelector);
    if (!form) return;
    form.addEventListener('submit', () => {
        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Procesando...';
        }
    });
}

// Auto-ocultar contraseña después de ms
export function scheduleAutoHide(entryId, ms = 10000) {
    const maskEl = document.getElementById(`pwd-mask-${entryId}`);
    const valEl = document.getElementById(`pwd-value-${entryId}`);
    const btn = document.getElementById(`btn-toggle-${entryId}`);
    if (!maskEl || !valEl || !btn) return;
    setTimeout(() => {
        if (valEl.style.display === 'inline') {
            valEl.style.display = 'none';
            maskEl.style.display = 'inline';
            btn.textContent = 'Mostrar';
            showToast('Contraseña oculta automáticamente');
        }
    }, ms);
}


