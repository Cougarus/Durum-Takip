
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename
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

# MODELLER
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(50), unique=True, nullable=False)
    sifre = db.Column(db.String(50), nullable=False)
    isim = db.Column(db.String(100))
    unvan = db.Column(db.String(50))
    yetki = db.Column(db.Integer)

class Mesaj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hedef = db.Column(db.String(100))
    icerik = db.Column(db.Text)
    dosya = db.Column(db.String(100))
    zaman = db.Column(db.String(50))
    gonderen = db.Column(db.String(50))

class Ariza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mahal = db.Column(db.String(50))
    tanim = db.Column(db.Text)
    durum = db.Column(db.String(20))
    zaman = db.Column(db.String(50))
    ekleyen = db.Column(db.String(50))

# İlk kullanıcıyı ekle
@app.before_first_request
def setup():
    db.create_all()
    if not Kullanici.query.first():
        db.session.add(Kullanici(kullanici_adi="admin", sifre="admin123", isim="Admin", unvan="Müdür", yetki=3))
        db.session.add(Kullanici(kullanici_adi="ahmet", sifre="ahmet123", isim="Ahmet Yılmaz", unvan="Şef", yetki=2))
        db.session.add(Kullanici(kullanici_adi="zeynep", sifre="zeynep123", isim="Zeynep Arslan", unvan="Uzman", yetki=1))
        db.session.commit()

@app.route('/')
def index():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('mesaj_gonder'))

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

@app.route('/mesaj-gonder', methods=['GET', 'POST'])
def mesaj_gonder():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        hedef = request.form.get('hedef_kullanici')
        icerik = request.form.get('mesaj_icerigi')
        dosya = request.files.get('dosya')
        zaman = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        dosya_adi = ""
        if dosya and dosya.filename != '':
            dosya_adi = secure_filename(dosya.filename)
            dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosya_adi))

        mesaj = Mesaj(hedef=hedef, icerik=icerik, dosya=dosya_adi, zaman=zaman, gonderen=session['kullanici'])
        db.session.add(mesaj)
        db.session.commit()
        flash("Mesaj başarıyla gönderildi.", "success")
        return redirect(url_for('mesaj_gonder'))

    user = Kullanici.query.filter_by(kullanici_adi=session['kullanici']).first()
    return render_template('mesaj_gonder.html', kullanici=session['kullanici'], userinfo=user)

@app.route('/mesaj-takip')
def mesaj_takip():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    mesajlar = Mesaj.query.all()
    return render_template('mesaj_takip.html', mesajlar=mesajlar)

@app.route('/ariza-kayit', methods=['GET', 'POST'])
def ariza_kayit():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    user = Kullanici.query.filter_by(kullanici_adi=session['kullanici']).first()
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
