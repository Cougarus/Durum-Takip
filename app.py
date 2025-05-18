from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(50), unique=True, nullable=False)
    sifre = db.Column(db.String(50), nullable=False)
    isim = db.Column(db.String(100))
    unvan = db.Column(db.String(50))
    yetki = db.Column(db.Integer)

class Ariza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mahal = db.Column(db.String(50))
    tanim = db.Column(db.Text)
    durum = db.Column(db.String(20))
    zaman = db.Column(db.String(50))
    ekleyen = db.Column(db.String(50))

@app.before_first_request
def create_admin():
    if not Kullanici.query.filter_by(kullanici_adi='admin').first():
        admin = Kullanici(kullanici_adi='admin', sifre='admin', isim='Admin', unvan='Müdür', yetki=3)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('ariza_kayit'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici = request.form.get('kullanici')
        sifre = request.form.get('sifre')
        user = Kullanici.query.filter_by(kullanici_adi=kullanici, sifre=sifre).first()
        if user:
            session['kullanici'] = user.kullanici_adi
            flash("Giriş başarılı.", "success")
            return redirect(url_for('index'))
        else:
            flash("Hatalı kullanıcı adı veya şifre", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Çıkış yapıldı.", "success")
    return redirect(url_for('login'))

@app.route('/ariza-kayit', methods=['GET', 'POST'])
def ariza_kayit():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    user = Kullanici.query.filter_by(kullanici_adi=session['kullanici']).first()
    if not user:
        flash("Kullanıcı bulunamadı!", "danger")
        return redirect(url_for('logout'))
    if user.yetki < 2:
        flash("Bu sayfaya erişim yetkiniz yok!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        mahal = request.form.get('mahal_kodu')
        tanim = request.form.get('ariza_tanimi')
        durum = request.form.get('durum')
        zaman = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        acik_kayit = Ariza.query.filter_by(mahal=mahal, durum='Açık').first()
        if acik_kayit:
            flash("Bu mahal kodunda açık kayıt zaten var!", "danger")
        else:
            ariza = Ariza(mahal=mahal, tanim=tanim, durum=durum, zaman=zaman, ekleyen=session['kullanici'])
            db.session.add(ariza)
            db.session.commit()
            flash("Arıza kaydı başarıyla eklendi.", "success")
            return redirect(url_for('ariza_kayit'))

    return render_template('ariza_kayit.html')

@app.route('/ariza-listesi')
def ariza_listesi():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    arizalar = Ariza.query.all()
    return render_template('ariza_listesi.html', arizalar=arizalar)

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)