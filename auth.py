import logging
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db_read, db_write

logger = logging.getLogger(__name__)
login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def get_by_id(user_id):
        row = db_read(
            "SELECT * FROM schueler WHERE id = %s",
            (user_id,),
            single=True
        )
        if row:
            return User(row["id"], row["username"], row["email"], row["password"])
        return None

    @staticmethod
    def get_by_username(username):
        row = db_read(
            "SELECT * FROM schueler WHERE username = %s",
            (username,),
            single=True
        )
        if row:
            return User(row["id"], row["username"], row["email"], row["password"])
        return None


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get_by_id(int(user_id))
    except ValueError:
        return None


def register_user(username, password, email):
    """
    Registriert einen neuen Schüler in der DB-Tabelle `schueler`.
    E-Mail ist **Pflicht**.
    """
    if not email:
        logger.warning("register_user(): Keine E-Mail angegeben")
        return False

    if User.get_by_username(username):
        logger.warning("register_user(): Username '%s' existiert bereits", username)
        return False

    hashed_pw = generate_password_hash(password)

    try:
        db_write(
            "INSERT INTO schueler (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_pw)
        )
        logger.info("register_user(): Benutzer '%s' erfolgreich angelegt", username)
        return True
    except Exception as e:
        logger.exception("Fehler beim Anlegen von Benutzer '%s': %s", username, e)
        return False


def authenticate(username, password):
    user = User.get_by_username(username)
    if user and check_password_hash(user.password, password):
        return user
    return None
