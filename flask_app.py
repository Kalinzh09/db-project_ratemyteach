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
        username = request.form["username"]
        password = request.form["password"]
        email = request.form.get("email")  # E-Mail jetzt Pflicht

        if not email:
            error = "Bitte gib eine gültige E-Mail-Adresse ein."
        else:
            ok = register_user(username, password, email)
            if ok:
                return redirect(url_for("login"))
            error = "Benutzername existiert bereits oder E-Mail ist ungültig."

    return render_template("auth.html",
        title="Registrieren",
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
