# SIGRAMS — Sistema de Gestión de Marcas y Señales Ganaderas

Sistema web de la Dirección de Ganadería de Catamarca: registro de productores,
marcas y señales, trámites (solicitudes), carnets, historial de cambios y
consulta de solo lectura para organismos externos (rol Inspector).

## Requisitos
- Python 3.12
- PostgreSQL 15 con PostGIS 3.4
- Librerías del sistema para GeoDjango (GDAL, GEOS, PROJ)

En Ubuntu:
```
sudo apt install gdal-bin libgdal-dev libgeos-dev libproj-dev postgresql postgis
```

## Instalación
1. Crear la base y activar PostGIS:
```sql
   CREATE DATABASE sigrams_db;
   \c sigrams_db
   CREATE EXTENSION postgis;
```
   Se recomienda un usuario propio con permisos solo sobre esa base.
2. Entorno virtual e instalación de dependencias:
```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```
3. Copiar `.env.example` como `.env` y completar todos los valores.
   Generar la `SECRET_KEY` con:
```
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
4. Crear las tablas y el primer administrador:
```
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
```
5. Producción: ejecutar con Gunicorn detrás de Nginx y HTTPS.
```
   gunicorn siggrams.wsgi:application --bind 127.0.0.1:8000
```

## Roles y alta de usuarios
- **Administrador**: acceso total, aprueba cuentas, ve reportes de ingresos.
- **Empleado**: gestiona productores, marcas, solicitudes y carnets.
- **Inspector**: solo consulta (datos del productor, marca, señales, mapas).
- Las cuentas nuevas se registran en estado *pendiente*. Un administrador las
  aprueba en "Cuentas Pendientes", elige el rol y el sistema genera un código
  de activación (se muestra al administrador y se envía por mail).

## Qué debe configurar quien despliega
- [ ] Base de datos propia, con clave nueva
- [ ] `SECRET_KEY` nueva y `DEBUG=False`
- [ ] Dominio en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`
- [ ] Claves de reCAPTCHA del dominio real. **Además**, la clave pública
      está escrita en `templates/app_sigrams/login.html` y `register.html`
      (atributo `data-sitekey`): hay que reemplazarla ahí también
- [ ] Cuenta de correo (SMTP) institucional, con SPF y DKIM en el dominio
- [ ] HTTPS con certificado válido; `BEHIND_PROXY=True` solo si el proxy
      envía `X-Forwarded-Proto`
- [ ] Firewall: abrir solo 80/443, SSH restringido, PostgreSQL sin acceso externo
- [ ] Nginx: `client_max_body_size 12M`
- [ ] Caché compartido (Redis o similar) para el límite de intentos de login
      si se usan varios procesos
- [ ] Copias de seguridad de la base y de la carpeta `media/`

## Archivos subidos (`media/`)
Contiene fotos de marcas, carnets y documentos con datos personales. Con
`DEBUG=False` Django no los sirve; si se sirven directo desde Nginx, quedan
accesibles sin iniciar sesión. Definir si se protegen con autenticación.

## Datos personales
El sistema guarda DNI, CUIT, domicilio y contacto de productores (Ley 25.326
de Protección de Datos Personales). No publicar la base ni el repositorio.