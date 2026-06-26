"""
SAR BROOMS — Flask Website with Admin Panel
=============================================
Run locally with:
    python app.py
Then open http://127.0.0.1:5000 in your browser.

See README.md for full setup instructions.
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
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload size

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access the admin panel."
login_manager.login_message_category = "warning"


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
    unit = db.Column(db.String(50), nullable=True, default="per piece")
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)  # filename only
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def image_url(self):
        if self.image:
            return url_for("static", filename=f"uploads/{self.image}")
        return url_for("static", filename="images/placeholder.png")


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    intro = db.Column(db.Text, nullable=False, default="")
    about_story = db.Column(db.Text, nullable=False, default="")
    about_mission = db.Column(db.Text, nullable=False, default="")
    about_vision = db.Column(db.Text, nullable=False, default="")
    about_excellence = db.Column(db.Text, nullable=False, default="")
    contact1_label = db.Column(db.String(80), nullable=False, default="Sales")
    contact1 = db.Column(db.String(40), nullable=False, default="")
    contact2_label = db.Column(db.String(80), nullable=False, default="Orders / Support")
    contact2 = db.Column(db.String(40), nullable=False, default="")
    address = db.Column(db.String(255), nullable=False, default="")
    email = db.Column(db.String(120), nullable=False, default="")


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


@app.context_processor
def inject_company():
    """Makes `company` available in every template automatically (e.g. footer)."""
    return {"company": get_company()}


# ---------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_product_image(file_storage):
    """Saves an uploaded image and returns its stored filename, or None."""
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        flash("Invalid image type. Allowed: png, jpg, jpeg, gif, webp.", "danger")
        return None

    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(filepath)

    # Resize down if huge, to keep things fast (best effort; skip if Pillow missing)
    try:
        from PIL import Image
        img = Image.open(filepath)
        img.thumbnail((1000, 1000))
        img.save(filepath)
    except Exception:
        pass

    return unique_name


def delete_product_image(filename):
    if not filename:
        return
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass


def get_company():
    company = Company.query.first()
    if not company:
        company = Company(
            intro=("SAR BROOMS is a trusted broom manufacturing company dedicated to "
                   "producing high-quality, durable, and affordable brooms for homes "
                   "and businesses."),
            about_story=("SAR BROOMS started with a simple goal: to manufacture brooms "
                          "that genuinely last. What began as a small workshop has grown "
                          "into a trusted name for households and businesses who need "
                          "reliable, everyday cleaning tools."),
            about_mission="To manufacture durable, affordable, and high-quality brooms that make everyday cleaning easier for every home and business.",
            about_vision="To become a trusted household name in broom manufacturing, known for consistent quality and honest pricing.",
            about_excellence="Every broom we make goes through careful selection of raw materials and quality checks before it reaches you, ensuring strength and durability you can rely on.",
            contact1_label="Sales",
            contact1="+91 90000 00001",
            contact2_label="Orders / Support",
            contact2="+91 90000 00002",
            address="SAR Brooms Manufacturing Unit, Industrial Area, Tamil Nadu, India",
            email="contact@sarbrooms.com",
        )
        db.session.add(company)
        db.session.commit()
    return company


# ---------------------------------------------------------------
# ADMIN AUTH DECORATOR (extra explicit guard, Flask-Login already covers this)
# ---------------------------------------------------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------
# PUBLIC ROUTES
# ---------------------------------------------------------------
@app.route("/")
def index():
    company = get_company()
    featured_products = Product.query.order_by(Product.created_at.desc()).limit(6).all()
    return render_template("index.html", company=company, products=featured_products)


@app.route("/products")
def products():
    company = get_company()
    search = request.args.get("q", "", type=str).strip()
    page = request.args.get("page", 1, type=int)

    query = Product.query.order_by(Product.created_at.desc())
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    pagination = query.paginate(page=page, per_page=PRODUCTS_PER_PAGE, error_out=False)

    return render_template(
        "products.html",
        company=company,
        pagination=pagination,
        products=pagination.items,
        search=search,
    )


@app.route("/about")
def about():
    company = get_company()
    return render_template("about.html", company=company)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    company = get_company()
    if request.method == "POST":
        # No backend storage of messages required (no order/payment system per spec);
        # we simply acknowledge the submission.
        name = request.form.get("name", "").strip()
        if name:
            flash(f"Thanks {name}! Your message has been noted. We'll get back to you soon.", "success")
        else:
            flash("Please fill in your name before sending.", "warning")
        return redirect(url_for("contact"))
    return render_template("contact.html", company=company)


# ---------------------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            flash("Welcome back!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# ADMIN ROUTES
# ---------------------------------------------------------------
@app.route("/admin")
@login_required
def dashboard():
    total_products = Product.query.count()
    total_images = Product.query.filter(Product.image.isnot(None)).count()
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_images=total_images,
        recent_products=recent_products,
    )


@app.route("/admin/products")
@login_required
def admin_products():
    search = request.args.get("q", "", type=str).strip()
    page = request.args.get("page", 1, type=int)

    query = Product.query.order_by(Product.created_at.desc())
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    pagination = query.paginate(page=page, per_page=10, error_out=False)
    return render_template(
        "admin_products.html",
        pagination=pagination,
        products=pagination.items,
        search=search,
    )


@app.route("/admin/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "")
        unit = request.form.get("unit", "").strip() or "per piece"
        description = request.form.get("description", "").strip()
        image_file = request.files.get("image")

        if not name or not price:
            flash("Product name and price are required.", "danger")
            return render_template("add_product.html")

        try:
            price_val = float(price)
            if price_val < 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid price.", "danger")
            return render_template("add_product.html")

        image_filename = save_product_image(image_file)

        product = Product(
            name=name,
            price=price_val,
            unit=unit,
            description=description,
            image=image_filename,
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{name}" added successfully.', "success")
        return redirect(url_for("admin_products"))

    return render_template("add_product.html")


@app.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "")
        unit = request.form.get("unit", "").strip() or "per piece"
        description = request.form.get("description", "").strip()
        image_file = request.files.get("image")
        remove_image = request.form.get("remove_image") == "1"

        if not name or not price:
            flash("Product name and price are required.", "danger")
            return render_template("edit_product.html", product=product)

        try:
            price_val = float(price)
            if price_val < 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid price.", "danger")
            return render_template("edit_product.html", product=product)

        product.name = name
        product.price = price_val
        product.unit = unit
        product.description = description

        if remove_image and product.image:
            delete_product_image(product.image)
            product.image = None

        if image_file and image_file.filename:
            new_filename = save_product_image(image_file)
            if new_filename:
                delete_product_image(product.image)
                product.image = new_filename

        db.session.commit()
        flash(f'Product "{name}" updated successfully.', "success")
        return redirect(url_for("admin_products"))

    return render_template("edit_product.html", product=product)


@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    delete_product_image(product.image)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" deleted.', "info")
    return redirect(url_for("admin_products"))


@app.route("/admin/company", methods=["GET", "POST"])
@login_required
def company_settings():
    company = get_company()

    if request.method == "POST":
        company.intro = request.form.get("intro", "").strip()
        company.about_story = request.form.get("about_story", "").strip()
        company.about_mission = request.form.get("about_mission", "").strip()
        company.about_vision = request.form.get("about_vision", "").strip()
        company.about_excellence = request.form.get("about_excellence", "").strip()
        company.contact1_label = request.form.get("contact1_label", "").strip() or "Contact 1"
        company.contact1 = request.form.get("contact1", "").strip()
        company.contact2_label = request.form.get("contact2_label", "").strip() or "Contact 2"
        company.contact2 = request.form.get("contact2", "").strip()
        company.address = request.form.get("address", "").strip()
        company.email = request.form.get("email", "").strip()

        db.session.commit()
        flash("Company information updated successfully.", "success")
        return redirect(url_for("company_settings"))

    return render_template("company_settings.html", company=company)


@app.route("/admin/security", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not current_user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return render_template("change_password.html")

        if new_username and new_username != current_user.username:
            existing = Admin.query.filter_by(username=new_username).first()
            if existing:
                flash("That username is already taken.", "danger")
                return render_template("change_password.html")
            current_user.username = new_username

        if new_password:
            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                return render_template("change_password.html")
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return render_template("change_password.html")
            current_user.set_password(new_password)

        db.session.commit()
        flash("Account settings updated successfully.", "success")
        return redirect(url_for("change_password"))

    return render_template("change_password.html")


# ---------------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


@app.errorhandler(413)
def file_too_large(e):
    flash("That file is too large. Maximum upload size is 5 MB.", "danger")
    return redirect(request.referrer or url_for("index"))


# ---------------------------------------------------------------
# CLI / FIRST-RUN SETUP
# ---------------------------------------------------------------
def init_db_and_seed():
    """Creates tables and seeds a default admin + sample products if empty."""
    with app.app_context():
        db.create_all()

        if not Admin.query.first():
            admin = Admin(username="admin")
            admin.set_password("admin@123")
            db.session.add(admin)
            db.session.commit()
            print("Created default admin -> username: admin | password: admin@123")

        get_company()

        if Product.query.count() == 0:
            sample_products = [
                ("Coconut Fiber Broom", 120, "per piece",
                 "Sturdy outdoor broom made from coconut fiber, great for courtyards and rough sweeping."),
                ("Soft Bristle Floor Broom", 90, "per piece",
                 "Gentle on tiles and floors, ideal for daily indoor use."),
                ("Long Handle Broom", 140, "per piece",
                 "Extra-long handle for easy reach without bending."),
                ("Heavy Duty Industrial Broom", 250, "per piece",
                 "Built for warehouses and factory floors. Extra-wide sweep."),
                ("Mini Hand Broom", 60, "per piece",
                 "Compact broom for tight corners and quick cleanups."),
                ("Grass Broom (Traditional)", 80, "per piece",
                 "Classic handmade grass broom, a household favorite."),
                ("Plastic Bristle Broom", 100, "per piece",
                 "Water-resistant bristles, perfect for wet areas and bathrooms."),
                ("Garden Broom (Wide Head)", 160, "per piece",
                 "Wide head design for fast outdoor and garden cleanup."),
            ]
            for name, price, unit, desc in sample_products:
                db.session.add(Product(name=name, price=price, unit=unit, description=desc))
            db.session.commit()
            print(f"Seeded {len(sample_products)} sample products.")


if __name__ == "__main__":
    init_db_and_seed()
    app.run(debug=True, host="127.0.0.1", port=5000)
