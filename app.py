
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, Response, send_from_directory, jsonify
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'guvenli_bir_anahtar'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        session['kullanici'] = 'admin'

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

    return render_template_string('\n    <h2>Mesaj Gönder</h2>\n    <form method=\'POST\' enctype=\'multipart/form-data\'>\n      <label>Hedef Kullanıcı ("*" = Tüm Kullanıcılar)</label><br>\n      <input name=\'hedef\' required><br>\n      <label>Mesaj İçeriği</label><br>\n      <textarea name=\'icerik\' required></textarea><br>\n      <label>Görsel Ekle:</label><input type=\'file\' name=\'gorsel\'><br>\n      <button type=\'submit\'>Gönder</button>\n    </form>\n    <a href=\'/mesaj-kontrol\' target=\'_blank\'>Mesaj Takip Sayfası</a>\n')

@app.route("/mesajlar")
def mesajlar_al():
    if 'kullanici' not in session:
        return jsonify([])
    k = session['kullanici']
    yeni_mesajlar = [m for m in mesajlar if m['hedef'] == k or m['hedef'] == '*']
    return jsonify(yeni_mesajlar)

@app.route("/mesaj-kontrol")
def mesaj_kontrol():
    return render_template_string('\n    <script>\n      setInterval(() => {\n        fetch(\'/mesajlar\')\n          .then(res => res.json())\n          .then(data => {\n            if (data.length > 0) {\n              let msg = data[data.length - 1];\n              let metin = "Yeni Mesaj: " + msg.icerik;\n              if (msg.gorsel) {\n                metin += "\\nGörsel: /uploads/" + msg.gorsel;\n              }\n              alert(metin);\n              var audio = new Audio("https://www.soundjay.com/buttons/sounds/beep-07.mp3");\n              audio.play();\n            }\n          });\n      }, 10000);\n    </script>\n')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
