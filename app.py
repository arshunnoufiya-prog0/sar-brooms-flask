"""
SAR BROOMS — Flask Website with Admin Panel
"""

import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, abort, send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------
# APP CONFIG
# ---------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
PRODUCTS_PER_PAGE = 12

app = Flask(__name__)
app.config["SECRET_KEY"] = "sar-brooms-change-this-secret-key-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


# ---------------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------------
class Admin(UserMixin, db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), default="per piece")
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    intro = db.Column(db.Text, default="")
    about_story = db.Column(db.Text, default="")
    about_mission = db.Column(db.Text, default="")
    about_vision = db.Column(db.Text, default="")
    about_excellence = db.Column(db.Text, default="")
    contact1_label = db.Column(db.String(80), default="Sales")
    contact1 = db.Column(db.String(40), default="")
    contact2_label = db.Column(db.String(80), default="Support")
    contact2 = db.Column(db.String(40), default="")
    address = db.Column(db.String(255), default="")
    email = db.Column(db.String(120), default="")


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# ---------------------------------------------------------------
# COMPANY HELPERS
# ---------------------------------------------------------------
def get_company():
    company = Company.query.first()
    if not company:
        company = Company(
            intro="SAR BROOMS is a trusted broom manufacturing company.",
            about_story="We started with a mission to deliver quality brooms.",
            about_mission="Deliver durable and affordable products.",
            about_vision="Become a trusted brand.",
            about_excellence="Quality checked products.",
            contact1="+91 90000 00001",
            contact2="+91 90000 00002",
            address="India",
            email="contact@sarbrooms.com"
        )
        db.session.add(company)
        db.session.commit()
    return company


# ---------------------------------------------------------------
# INIT DB (IMPORTANT FIX)
# ---------------------------------------------------------------
def init_db_and_seed():
    with app.app_context():
        db.create_all()

        # Admin
        if not Admin.query.first():
            admin = Admin(username="admin")
            admin.set_password("admin@123")
            db.session.add(admin)

        # Company
        get_company()

        # Products
        if Product.query.count() == 0:
            db.session.add(Product(
                name="Coconut Fiber Broom",
                price=120,
                description="Durable broom"
            ))
            db.session.add(Product(
                name="Soft Broom",
                price=90,
                description="Indoor broom"
            ))

        db.session.commit()


# ---------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", company=get_company())


@app.route("/products")
def products():
    return render_template("products.html", company=get_company())


@app.route("/about")
def about():
    return render_template("about.html", company=get_company())


@app.route("/contact")
def contact():
    return render_template("contact.html", company=get_company())


# ---------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin = Admin.query.filter_by(username=request.form["username"]).first()
        if admin and admin.check_password(request.form["password"]):
            login_user(admin)
            return redirect("/admin")
    return render_template("login.html")


@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/admin")
@login_required
def dashboard():
    return "Admin Dashboard Working"


# ---------------------------------------------------------------
# RUN
# ---------------------------------------------------------------
if __name__ == "__main__":
    init_db_and_seed()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))