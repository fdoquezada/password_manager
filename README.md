# Gestor de Contraseñas

Un sistema seguro de gestión de contraseñas desarrollado con Django que permite almacenar y administrar credenciales de forma cifrada.

## 🚀 Características

- **Cifrado seguro**: Todas las contraseñas se cifran usando el algoritmo Fernet antes de guardarse
- **Interfaz intuitiva**: Dashboard limpio y fácil de usar
- **Control de acceso**: Solo puedes ver y editar tus propias contraseñas
- **Revelado bajo demanda**: Las contraseñas se muestran ocultas por defecto
- **Edición completa**: Modifica cualquier entrada guardada
- **Diseño responsivo**: Optimizado para dispositivos móviles y desktop
- **Sistema de usuarios**: Registro e inicio de sesión seguro

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.6
- **Base de datos**: PostgreSQL
- **Cifrado**: Cryptography (Fernet)
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **UI**: Bootstrap 5.3.3 + Font Awesome 6.5.2
- **Configuración**: python-decouple para variables de entorno

## 📋 Requisitos Previos

- Python 3.8+
- PostgreSQL
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd password_manager
   ```

2. **Crea un entorno virtual**:
   ```bash
   python -m venv entorno/env
   ```

3. **Activa el entorno virtual**:
   - En Windows:
     ```bash
     entorno\env\Scripts\activate
     ```
   - En Linux/Mac:
     ```bash
     source entorno/env/bin/activate
     ```

4. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configura la base de datos**:
   - Crea una base de datos PostgreSQL
   - Crea un archivo `.env` en la raíz del proyecto con:
     ```env
     DB_NAME=tu_nombre_base_datos
     DB_USER=tu_usuario_postgres
     DB_PASSWORD=tu_contraseña_postgres
     DB_HOST=localhost
     DB_PORT=5432
     FERNET_KEY=tu_clave_fernet_generada
     ```

6. **Genera una clave Fernet**:
   ```bash
   python clave.py
   ```
   Copia la clave generada al archivo `.env`

7. **Ejecuta las migraciones**:
   ```bash
   python manage.py migrate
   ```

8. **Crea un superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

9. **Inicia el servidor**:
   ```bash
   python manage.py runserver
   ```

## 🎯 Uso del Sistema

### Registro e Inicio de Sesión
- Accede a `/register/` para crear una nueva cuenta
- Usa `/login/` para iniciar sesión con credenciales existentes

### Gestión de Contraseñas
1. **Agregar contraseñas**: Ve a "Agregar nueva" desde el dashboard
2. **Ver contraseñas**: Presiona "Mostrar" para revelar una contraseña específica
3. **Editar entradas**: Usa el botón "Editar" para modificar cualquier entrada
4. **Ayuda**: Consulta la página de ayuda integrada para más información

### Características de Seguridad
- Las contraseñas se cifran automáticamente al guardarse
- Solo se muestran cuando el usuario lo solicita explícitamente
- Cada usuario solo puede acceder a sus propias contraseñas
- Las contraseñas se ocultan por defecto en el dashboard

## 📱 Responsividad

El sistema está optimizado para:
- **Desktop**: Layout de 3 columnas en el dashboard
- **Tablet**: Layout de 2 columnas
- **Móvil**: Layout de 1 columna con navegación adaptada

## 🔒 Seguridad

- **Cifrado**: Fernet con clave configurable
- **Autenticación**: Sistema de usuarios de Django
- **Autorización**: Control de acceso por usuario
- **CSRF**: Protección contra ataques CSRF
- **Variables de entorno**: Configuración sensible fuera del código

## 📁 Estructura del Proyecto

```
password_manager/
├── contacto/          # App de contacto
├── vaul/             # App principal de gestión de contraseñas
├── password_manager/ # Configuración del proyecto Django
├── templates/        # Plantillas base
├── static/          # Archivos estáticos (CSS, JS)
├── entorno/         # Entorno virtual
├── manage.py        # Script de gestión de Django
└── requirements.txt # Dependencias del proyecto
```

## 🚀 Despliegue en Producción

1. **Configuración de producción**:
   - Cambia `DEBUG = False` en `settings.py`
   - Configura `ALLOWED_HOSTS`
   - Usa un servidor web como Nginx + Gunicorn

2. **Base de datos**:
   - Usa PostgreSQL en producción
   - Configura backups regulares

3. **Seguridad**:
   - Cambia `SECRET_KEY` por una nueva
   - Usa HTTPS en producción
   - Configura variables de entorno seguras

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Fernando Quezada**
- Desarrollador del sistema de gestión de contraseñas

## 📞 Soporte

Si tienes problemas o preguntas:
- Revisa la página de ayuda integrada en el sistema
- Contacta al administrador del sistema
- Abre un issue en el repositorio

---

**Nota**: Este es un proyecto de demostración. Para uso en producción, considera implementar características adicionales de seguridad como autenticación de dos factores, auditoría de accesos, y políticas de contraseñas más estrictas.