
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "gizli_anahtar"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(50), unique=True, nullable=False)
    sifre = db.Column(db.String(50), nullable=False)
    isim = db.Column(db.String(50))
    unvan = db.Column(db.String(50))
    yetki = db.Column(db.Integer)

@app.route('/')
def ana_sayfa():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi, sifre=sifre).first()
        if kullanici:
            session['kullanici'] = kullanici.kullanici_adi
            return redirect(url_for('ariza_kayit'))
        else:
            return render_template("login.html", hata="Hatalı giriş.")
    return render_template("login.html")

@app.route('/setup-admin')
def setup_admin():
    if not Kullanici.query.filter_by(kullanici_adi='admin').first():
        admin = Kullanici(kullanici_adi='admin', sifre='admin', isim='Admin', unvan='Müdür', yetki=3)
        db.session.add(admin)
        db.session.commit()
        return "Admin oluşturuldu."
    return "Zaten admin var."

@app.route('/ariza-kayit')
def ariza_kayit():
    if 'kullanici' in session:
        return render_template("ariza_kayit.html", kullanici=session['kullanici'])
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
