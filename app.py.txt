from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'guvenli_bir_anahtar'  # oturum yönetimi için gerekli

# Geçici veri yapıları
kayitlar = []
kullanicilar = {
    "admin": "admin"
}

# Giriş ve ana sayfa HTML şablonları
template_login = """
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8">
    <title>Giriş Yap</title>
    <style>
      body { font-family: Arial; padding: 20px; }
      form { max-width: 300px; margin: auto; }
      input { display: block; width: 100%; margin-bottom: 10px; padding: 8px; }
      button { padding: 8px 16px; width: 100%; }
      .error { color: red; }
    </style>
  </head>
  <body>
    <h2>Durum Takip - Giriş</h2>
    <form method="POST">
      <input type="text" name="kullanici" placeholder="Kullanıcı Adı" required>
      <input type="password" name="sifre" placeholder="Şifre" required>
      <button type="submit">Giriş Yap</button>
      {% if hata %}<p class="error">{{ hata }}</p>{% endif %}
    </form>
  </body>
</html>
"""

template_index = """
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Durum Takip</title>
    <style>
      body { font-family: Arial; padding: 20px; }
      table { width: 100%; border-collapse: collapse; margin-top: 20px; }
      th, td { padding: 8px; border: 1px solid #ccc; text-align: center; }
      .evet { background-color: #c6efce; }
      .hayir { background-color: #c00000; color: white; }
      .askida { background-color: #ffeb9c; }
    </style>
  </head>
  <body>
    <h2>Durum Girişi</h2>
    <form method="POST">
      <label>Ad Soyad:</label>
      <input type="text" name="ad" required>
      <label>Durum:</label>
      <select name="durum">
        <option value="evet">Evet</option>
        <option value="hayir">Hayır</option>
        <option value="askida">Askıda</option>
      </select>
      <button type="submit">Kaydet</button>
    </form>

    {% if kayitlar %}
    <h3>Kayıtlar</h3>
    <table>
      <tr><th>Ad</th><th>Durum</th><th>Saat</th></tr>
      {% for k in kayitlar %}
        <tr class="{{ k.durum }}">
          <td>{{ k.ad }}</td>
          <td>{{ k.durum }}</td>
          <td>{{ k.saat }}</td>
        </tr>
      {% endfor %}
    </table>
    {% endif %}
    <br>
    <form method="post" action="/logout">
        <button type="submit">Çıkış Yap</button>
    </form>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        kullanici = request.form.get("kullanici")
        sifre = request.form.get("sifre")
        if kullanici in kullanicilar and kullanicilar[kullanici] == sifre:
            session['kullanici'] = kullanici
            return redirect(url_for("index"))
        else:
            return render_template_string(template_login, hata="Geçersiz kullanıcı adı veya şifre.")
    return render_template_string(template_login, hata=None)

@app.route("/giris", methods=["GET", "POST"])
def index():
    if 'kullanici' not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        ad = request.form.get("ad")
        durum = request.form.get("durum")
        saat = datetime.now().strftime("%H:%M:%S")
        kayitlar.append({"ad": ad, "durum": durum, "saat": saat})
        return redirect(url_for("index"))
    return render_template_string(template_index, kayitlar=kayitlar)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('kullanici', None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
