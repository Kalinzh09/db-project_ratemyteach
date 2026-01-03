from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging
import hashlib

# --------------------
# Setup
# --------------------
 

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

login_manager.init_app(app)
login_manager.login_view = "login"


# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401


# --------------------
# Auth
# --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = authenticate(request.form["username"], request.form["password"])
        if user:
            login_user(user)
            return redirect(url_for("lehrer_liste"))
        error = "Benutzername oder Passwort ist falsch."

    return render_template("auth.html",
        title="Einloggen",
        action=url_for("login"),
        button_label="Login",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        ok = register_user(request.form["username"], request.form["password"])
        if ok:
            return redirect(url_for("login"))
        error = "Benutzername existiert bereits."

    return render_template("auth.html",
        title="Registrieren neue funktion",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Schon registriert?",
        footer_link_url=url_for("login"),
        footer_link_label="Login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# --------------------
# Lehrerbewertung
# --------------------
@app.route("/")
@login_required
def lehrer_liste():
    lehrer = db_read("""
        SELECT l.id, l.vorname, l.name, l.fach,
               ROUND(AVG(b.sterne),1) AS avg_sterne
        FROM lehrer l
        LEFT JOIN bewertung b ON l.id = b.lehrer_id
        GROUP BY l.id
    """)
    return render_template("lehrer_liste.html", lehrer=lehrer)


@app.route("/lehrer/<int:lehrer_id>", methods=["GET", "POST"])
@login_required
def lehrer_detail(lehrer_id):
    if request.method == "POST":
        sterne = request.form["sterne"]
        kommentar = request.form.get("kommentar")

        db_write("""
            INSERT INTO bewertung (sterne, kommentar, schueler_id, lehrer_id)
            VALUES (%s, %s, %s, %s)
        """, (sterne, kommentar, current_user.id, lehrer_id))

        return redirect(url_for("lehrer_detail", lehrer_id=lehrer_id))

    lehrer = db_read("SELECT * FROM lehrer WHERE id=%s", (lehrer_id,), single=True)
    bewertungen = db_read("""
        SELECT b.sterne, b.kommentar, b.datum, s.username
        FROM bewertung b
        JOIN schueler s ON b.schueler_id = s.id
        WHERE b.lehrer_id=%s
        ORDER BY b.datum DESC
    """, (lehrer_id,))

    return render_template("lehrer_detail.html",
        lehrer=lehrer,
        bewertungen=bewertungen)


if __name__ == "__main__":
    app.run()
