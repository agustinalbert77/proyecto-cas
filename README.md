# Sitio Web CAS - Colegio Alemán de La Serena

Proyecto completo en **Flask** con:
- Página principal, noticias (con filtro), galería con modales y contacto.
- Panel admin separado con login seguro y CRUD de noticias y fotos.
- Envío real de correo vía SMTP (Gmail) desde el formulario de contacto.
- Estilos responsive inspirados en IB (azul/blanco) y Colegio Alemán (rojo/amarillo/negro).
- Base de datos SQLite.

## Requisitos
- Python 3.10+
- Pip

## Instalación (local)
```
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir: http://127.0.0.1:5000/

## Credenciales Admin
- Usuario: `admin`
- Contraseña: `cas2025`

## Configuración de correo (SMTP)
En `config.py` se dejó preparado Gmail con:
- `MAIL_USERNAME = 'agustinalbertaguilera@gmail.com'`
- `MAIL_PASSWORD = '*** contraseña de aplicación ***'`

> Para mover secretos a variables de entorno:
```
# Windows (PowerShell)
setx SECRET_KEY "clave_secreta_cas"
setx MAIL_USERNAME "tu@gmail.com"
setx MAIL_PASSWORD "tu_contraseña_app"

# Mac/Linux (bash)
export SECRET_KEY="clave_secreta_cas"
export MAIL_USERNAME="tu@gmail.com"
export MAIL_PASSWORD="tu_contraseña_app"
```

## Estructura
```
app.py
config.py
templates/
  base.html, index.html, news.html, gallery.html, contact.html
  admin/
    login.html, dashboard.html, add_news.html, edit_news.html, add_photo.html, edit_photo.html
static/
  css/styles.css
  js/scripts.js
  uploads/gallery_photos/
```

## Despliegue en Render
1) Subir el repo a GitHub.
2) En Render → New → Web Service → conecta tu repo.
3) Build Command: `pip install -r requirements.txt`
4) Start Command: `gunicorn app:app`
5) Variables de entorno: `SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`.
