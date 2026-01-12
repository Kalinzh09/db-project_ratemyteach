from flask import Flask, redirect, render_template, request, url_for, abort
from dotenv import load_dotenv
import os
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging
from functools import wraps

# --------------------
# Setup
# --------------------

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

login_manager.init_app(app)
login_manager.login_view = "login"

# --------------------
# Admin-Helpers
# --------------------

def is_admin(user):
    row = db_read(
        "SELECT id FROM admin WHERE username=%s",
        (user.username,),
        single=True
    )
    return row is not None


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not is_admin(current_user):
            abort(403)
        return func(*args, **kwargs)
    return wrapper


# für Templates verfügbar machen
app.jinja_env.globals.update(is_admin=is_admin)

# --------------------
# Auth-Routen
# --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = authenticate(
            request.form.get("username"),
            request.form.get("password"),
        )
        if user:
            login_user(user)
            return redirect(url_for("lehrer_liste"))
        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="Einloggen",
        action=url_for("login"),
        button_label="Login",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        ok = register_user(
            request.form.get("username"),
            request.form.get("password"),
            request.form.get("email")
        )
        if ok:
            return redirect(url_for("login"))
        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Registrieren",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Schon registriert?",
        footer_link_url=url_for("login"),
        footer_link_label="Login"
    )


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
        sterne = request.form.get("sterne")
        kommentar = request.form.get("kommentar")

        if sterne:
            existing = db_read(
                "SELECT id FROM bewertung WHERE schueler_id=%s AND lehrer_id=%s",
                (current_user.id, lehrer_id),
                single=True
            )

            if existing:
                db_write(
                    "UPDATE bewertung SET sterne=%s, kommentar=%s, datum=NOW() WHERE id=%s",
                    (sterne, kommentar, existing["id"])
                )
            else:
                db_write(
                    """INSERT INTO bewertung
                       (sterne, kommentar, schueler_id, lehrer_id, datum)
                       VALUES (%s, %s, %s, %s, NOW())""",
                    (sterne, kommentar, current_user.id, lehrer_id)
                )

        return redirect(url_for("lehrer_detail", lehrer_id=lehrer_id))

    lehrer = db_read(
        "SELECT * FROM lehrer WHERE id=%s",
        (lehrer_id,),
        single=True
    )

    bewertungen = db_read("""
        SELECT b.sterne, b.kommentar, b.datum, s.username
        FROM bewertung b
        JOIN schueler s ON b.schueler_id = s.id
        WHERE b.lehrer_id=%s
        ORDER BY b.datum DESC
    """, (lehrer_id,))

    return render_template(
        "lehrer_detail.html",
        lehrer=lehrer,
        bewertungen=bewertungen
    )

# --------------------
# Admin-Routen
# --------------------

@app.route("/admin/lehrer/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_lehrer():
    if request.method == "POST":
        email = request.form.get("email")
        vorname = request.form.get("vorname")
        name = request.form.get("name")
        fach = request.form.get("fach")

        if email and vorname and name and fach:
            db_write(
                "INSERT INTO lehrer (email, vorname, name, fach) VALUES (%s, %s, %s, %s)",
                (email, vorname, name, fach)
            )
            return redirect(url_for("lehrer_liste"))

    return render_template("add_lehrer.html")


@app.route("/admin/lehrer/delete/<int:lehrer_id>", methods=["POST"])
@login_required
@admin_required
def delete_lehrer(lehrer_id):
    db_write("DELETE FROM bewertung WHERE lehrer_id=%s", (lehrer_id,))
    db_write("DELETE FROM lehrer WHERE id=%s", (lehrer_id,))
    return redirect(url_for("lehrer_liste"))

# --------------------
# Dashboard (User)
# --------------------

@app.route("/dashboard")
@login_required
def dashboard():
    bewertungen = db_read(
        """
        SELECT 
        b.id,
        b.sterne,
        b.kommentar,
        b.datum,
        l.id AS lehrer_id,
        l.vorname,
        l.name,
        l.fach

        FROM bewertung b
        JOIN lehrer l ON b.lehrer_id = l.id
        WHERE b.schueler_id = %s
        ORDER BY b.datum DESC
        """,
        (current_user.id,)
    )

    return render_template("dashboard.html", bewertungen=bewertungen)


@app.route("/dashboard/edit/<int:bewertung_id>", methods=["GET", "POST"])
@login_required
def edit_bewertung(bewertung_id):
    bewertung = db_read(
        """
        SELECT * FROM bewertung
        WHERE id=%s AND schueler_id=%s
        """,
        (bewertung_id, current_user.id),
        single=True
    )

    if not bewertung:
        abort(403)

    if request.method == "POST":
        sterne = request.form.get("sterne")
        kommentar = request.form.get("kommentar")

        db_write(
            """
            UPDATE bewertung
            SET sterne=%s, kommentar=%s, datum=NOW()
            WHERE id=%s
            """,
            (sterne, kommentar, bewertung_id)
        )

        return redirect(url_for("dashboard"))

    return render_template("edit_bewertung.html", bewertung=bewertung)


@app.route("/dashboard/delete/<int:bewertung_id>", methods=["POST"])
@login_required
def delete_bewertung(bewertung_id):
    db_write(
        """
        DELETE FROM bewertung
        WHERE id=%s AND schueler_id=%s
        """,
        (bewertung_id, current_user.id)
    )

    return redirect(url_for("dashboard"))


# --------------------

if __name__ == "__main__":
    app.run()
