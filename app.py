from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid
from config import Config

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','webp'}

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    activity_type = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False, default='Admin')

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    author = db.Column(db.String(50), nullable=False, default='Admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password_hash=generate_password_hash('cas2025'))
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    news_list = News.query.order_by(News.date.desc()).limit(4).all()
    return render_template('index.html', news_list=news_list)

@app.route('/news')
def news():
    activity_type = request.args.get('type','').strip()
    date_str = request.args.get('date','').strip()
    q = News.query
    if activity_type:
        q = q.filter(News.activity_type.ilike(f"%{activity_type}%"))
    if date_str:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d').date()
            q = q.filter(News.date == d)
        except ValueError:
            flash('Formato de fecha inválido (AAAA-MM-DD).', 'warning')
    all_news = q.order_by(News.date.desc()).all()
    return render_template('news.html', all_news=all_news, activity_type=activity_type, date_str=date_str)

@app.route('/gallery')
def gallery():
    photos = Photo.query.order_by(Photo.date.desc()).all()
    return render_template('gallery.html', photos=photos)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name','Anónimo')
        email = request.form.get('email','sin-correo@ejemplo.com')
        message = request.form.get('message','')
        if not message.strip():
            flash('Por favor, escribe un mensaje.', 'warning')
            return redirect(url_for('contact'))
        recipients = ['secretaria@dsls.cl','rgalleguillos@dsls.cl','agustinalbertaguilera@gmail.com']
        try:
            msg = Message(subject=f"Contacto CAS - {name}", recipients=recipients,
                          body=f"Nombre: {name}\nEmail: {email}\n\nMensaje:\n{message}")
            mail.send(msg)
            flash('Mensaje enviado correctamente. ¡Gracias!', 'success')
        except Exception as e:
            print('MAIL ERROR:', e)
            flash('No se pudo enviar el mensaje. Revisa la configuración de correo.', 'danger')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            flash('Bienvenido al panel.', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Credenciales inválidas.', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('admin_login'))

def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/admin')
@login_required
def admin_dashboard():
    news_count = News.query.count()
    photo_count = Photo.query.count()
    recent_news = News.query.order_by(News.date.desc()).limit(5).all()
    recent_photos = Photo.query.order_by(Photo.date.desc()).limit(5).all()
    return render_template('admin/dashboard.html', news_count=news_count, photo_count=photo_count,
                           recent_news=recent_news, recent_photos=recent_photos)

@app.route('/admin/news/add', methods=['GET','POST'])
@login_required
def admin_add_news():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date_str = request.form.get('date')
        activity_type = request.form.get('activity_type')
        author = request.form.get('author','Admin')
        if not title or not content or not activity_type:
            flash('Completa los campos obligatorios.', 'warning')
            return redirect(url_for('admin_add_news'))
        try:
            date_val = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        except ValueError:
            flash('Fecha inválida.', 'danger')
            return redirect(url_for('admin_add_news'))
        n = News(title=title, content=content, date=date_val, activity_type=activity_type, author=author)
        db.session.add(n); db.session.commit()
        flash('Noticia creada.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_news.html')

@app.route('/admin/news/<int:news_id>/edit', methods=['GET','POST'])
@login_required
def admin_edit_news(news_id):
    n = News.query.get_or_404(news_id)
    if request.method == 'POST':
        n.title = request.form.get('title')
        n.content = request.form.get('content')
        n.activity_type = request.form.get('activity_type')
        n.author = request.form.get('author','Admin')
        date_str = request.form.get('date')
        try:
            n.date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else n.date
        except ValueError:
            flash('Fecha inválida.', 'danger')
            return redirect(url_for('admin_edit_news', news_id=news_id))
        db.session.commit()
        flash('Noticia actualizada.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_news.html', n=n)

@app.route('/admin/news/<int:news_id>/delete', methods=['POST'])
@login_required
def admin_delete_news(news_id):
    n = News.query.get_or_404(news_id)
    db.session.delete(n); db.session.commit()
    flash('Noticia eliminada.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/photos/add', methods=['GET','POST'])
@login_required
def admin_add_photo():
    if request.method == 'POST':
        file = request.files.get('photo')
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        author = request.form.get('author','Admin')
        if not file or not allowed_file(file.filename):
            flash('Archivo no válido. (png, jpg, jpeg, gif, webp)', 'warning')
            return redirect(url_for('admin_add_photo'))
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.',1)[1].lower()
        new_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(save_path)
        try:
            date_val = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        except ValueError:
            flash('Fecha inválida.', 'danger')
            return redirect(url_for('admin_add_photo'))
        p = Photo(filename=new_name, title=title, description=description, date=date_val, author=author)
        db.session.add(p); db.session.commit()
        flash('Foto subida a la galería.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_photo.html')

@app.route('/admin/photos/<int:photo_id>/edit', methods=['GET','POST'])
@login_required
def admin_edit_photo(photo_id):
    p = Photo.query.get_or_404(photo_id)
    if request.method == 'POST':
        p.title = request.form.get('title')
        p.description = request.form.get('description')
        p.author = request.form.get('author','Admin')
        date_str = request.form.get('date')
        try:
            p.date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else p.date
        except ValueError:
            flash('Fecha inválida.', 'danger')
            return redirect(url_for('admin_edit_photo', photo_id=photo_id))
        db.session.commit()
        flash('Foto actualizada.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_photo.html', p=p)

@app.route('/admin/photos/<int:photo_id>/delete', methods=['POST'])
@login_required
def admin_delete_photo(photo_id):
    p = Photo.query.get_or_404(photo_id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], p.filename))
    except Exception:
        pass
    db.session.delete(p); db.session.commit()
    flash('Foto eliminada.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# === Al final de tu app.py ===

if __name__ == "__main__":
    # Crear base de datos si no existe
    with app.app_context():
        init_db()  # tu función que crea tablas y datos iniciales

    # Correr servidor Flask
    app.run(debug=True)

