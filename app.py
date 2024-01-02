import bcrypt
from flask import Flask, redirect, request, session, url_for

from config import SQLALCHEMY_DATABASE_URI
from database import db
from model.user import User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)


def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def check_password(password, hashed_password):
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


with app.app_context():
    db.create_all()

    if not db.session.query(
        User.query.filter_by(email="email@email.com").exists()
    ).scalar():
        db.session.add(
            User(email="email@email.com", hashed_password=hash_password("MyPassword"))
        )
        db.session.commit()

    users = db.session.execute(db.select(User)).scalars()
    app.logger.info(users)


# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b"5c4990efccb1b1f609fda5eb7d92e8741e9779f9be5b7b99207c2f89e7abbc2a"


@app.route("/")
def index():
    if "username" in session:
        return f'Logged in as {session["username"]}'
    return "You are not logged in"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(email=username).first()
        if user is None:
            return redirect(url_for("login"))
        if not check_password(password, user.hashed_password):
            return redirect(url_for("login"))

        session["username"] = request.form["username"]
        return redirect(url_for("index"))
    return """
        <form method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    """


@app.route("/logout")
def logout():
    # remove the username from the session if it's there
    session.pop("username", None)
    return redirect(url_for("index"))
