# Yukarıdaki canvas'taki kod zaten güncel ve tek parça hâlde.
# Flask uygulaması tüm özellikleri içeriyor:
# - Giriş/kullanıcı oturumu
# - Mesaj gönderme (hedef, içerik, görsel)
# - Mesaj kontrol (sesli ve görsel uyarı)
# - Yüklenen dosyaları sunma

# Devamında ihtiyacın olan tek şey:
# 1. Giriş ekranı ve kullanıcı yönetimi
# 2. Arıza kaydı ekranı
# 3. Rapor ve yetki sisteminin tam entegresi

# Eğer bu kodu aşağıdaki şekilde tam anlamıyla test etmek istiyorsan:

from flask import Flask, render_template_string, request, redirect, url_for, session, flash, Response, send_from_directory, jsonify
from datetime import datetime
import csv
from io import StringIO
import os

app = Flask(__name__)
app.secret_key = 'guvenli_bir_anahtar'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Geçici veri yapıları
kayitlar = []
mesajlar = []
kullanicilar = {
    "admin": {
        "sifre": "admin",
        "unvan": "Admin",
        "yetki": 5,
        "sifre_degistir": False,
        "bolgeler": [],
        "telsiz": None,
        "bisiklet": None,
        "kontrol_noktalari": [],
        "personel_ekleyebilir": True,
        "bolge_ekleyebilir": True
    }
}

@app.route("/")
def home():
    return redirect(url_for("mesaj_gonder"))

@app.route("/mesaj-gonder", methods=["GET", "POST"])
def mesaj_gonder():
    if 'kullanici' not in session:
        session['kullanici'] = 'admin'  # demo amaçlı varsayılan giriş

    if request.method == "POST":
        hedef = request.form.get("hedef")
        icerik = request.form.get("icerik")
        dosya = request.files.get("gorsel")
        gorsel = None
        if dosya and dosya.filename:
            zaman_dosya = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + dosya.filename
            dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], zaman_dosya))
            gorsel = zaman_dosya
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mesajlar.append({"gonderen": session['kullanici'], "hedef": hedef, "icerik": icerik, "zaman": zaman, "gorsel": gorsel})
        return redirect(url_for("mesaj_gonder"))

    return render_template_string("""
    <h2>Mesaj Gönder</h2>
    <form method="POST" enctype="multipart/form-data">
      <label>Hedef Kullanıcı ("*" = Tüm Kullanıcılar)</label><br>
      <input name="hedef" required><br>
      <label>Mesaj İçeriği</label><br>
      <textarea name="icerik" required></textarea><br>
      <label>Görsel Ekle:</label><input type="file" name="gorsel"><br>
      <button type="submit">Gönder</button>
    </form>
    <a href="/mesaj-kontrol" target="_blank">Mesaj Takip Sayfasını Aç</a>
    """)

@app.route("/mesajlar")
def mesajlar_al():
    if 'kullanici' not in session:
        return jsonify([])
    k = session['kullanici']
    yeni_mesajlar = [m for m in mesajlar if m['hedef'] == k or m['hedef'] == '*']
    return jsonify(yeni_mesajlar)

@app.route("/mesaj-kontrol")
def mesaj_kontrol():
    return render_template_string("""
    <script>
      setInterval(() => {
        fetch('/mesajlar')
          .then(res => res.json())
          .then(data => {
            if (data.length > 0) {
              let msg = data[data.length - 1];
              let metin = "Yeni Mesaj: " + msg.icerik;
              if (msg.gorsel) {
                metin += "\\nGörsel: /uploads/" + msg.gorsel;
              }
              alert(metin);
              var audio = new Audio("https://www.soundjay.com/buttons/sounds/beep-07.mp3");
              audio.play();
            }
          });
      }, 10000);
    </script>
    """)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
