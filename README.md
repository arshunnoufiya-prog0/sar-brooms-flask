# SAR BROOMS — Website with Admin Panel

A complete website for SAR Brooms, a broom manufacturing company. Built with
Flask (Python), SQLite, and Bootstrap 5. Includes a public-facing site and
a secure admin panel to manage products, prices, images, and company info.

---

## 1. What's Included

- **Home page** — hero banner, intro, "Why Choose Us", featured products
- **Products page** — full catalogue with search and pagination (supports 20+ products)
- **About Us page** — company story, mission, vision, manufacturing excellence
- **Contact page** — 2 contact numbers, email, address, and a contact form
- **Admin Panel** — secure login, dashboard, product management (add/edit/delete
  with image upload), company info editor, and account/security settings

---

## 2. Requirements

- Python 3.9 or newer installed on your computer
  (check with `python3 --version` or `python --version`)

---

## 3. Running It Locally (Step by Step)

### Step 1 — Open a terminal in the project folder

Navigate into the `sar-brooms-flask` folder using your terminal / command prompt.

### Step 2 — Create a virtual environment (recommended)

```bash
python3 -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run the app

```bash
python app.py
```

The first time you run this, it will automatically:
- Create the SQLite database file (`database.db`)
- Create a default admin account
- Add 8 sample products so the site isn't empty

You'll see a message like:
```
Created default admin -> username: admin | password: admin@123
Seeded 8 sample products.
 * Running on http://127.0.0.1:5000
```

### Step 5 — Open the website

Open your browser and go to:

```
http://127.0.0.1:5000
```

To stop the server, go back to the terminal and press `CTRL + C`.

---

## 4. Logging Into the Admin Panel

1. Click **Admin Login** in the top-right of the site (or go to
   `http://127.0.0.1:5000/admin/login`).
2. Default login:
   - **Username:** `admin`
   - **Password:** `admin@123`
3. **Change this password immediately** after your first login — go to
   **Security** in the admin sidebar.

### What you can do as admin:

- **Dashboard** — see total products, total images uploaded, quick actions
- **Products** — add new products (name, price, description, unit, photo),
  edit or delete existing ones, search through them
- **Company Info** — edit the homepage intro, About Us content (story, mission,
  vision, manufacturing excellence), both contact numbers, email, and address
- **Security** — change your admin username and/or password

All changes save immediately to the database and appear on the live site
right away — no restart needed.

---

## 5. Uploading Product Images

When adding or editing a product, use the **Product Photo** field to upload
an image from your computer or phone (when accessed over your network).

- Accepted formats: PNG, JPG, JPEG, GIF, WEBP
- Maximum file size: 5 MB
- Images are automatically resized if very large, and saved into
  `static/uploads/`
- Products without a photo show a placeholder image automatically

---

## 6. Project Structure

```
sar-brooms-flask/
│
├── app.py                  # Main Flask application (routes, models, logic)
├── requirements.txt        # Python dependencies
├── database.db              # SQLite database (created on first run)
│
├── static/
│   ├── css/style.css       # Site styling (orange & gold theme)
│   ├── js/main.js          # Image preview, animations, small interactions
│   ├── images/             # Logo + placeholder image
│   └── uploads/            # Uploaded product photos (created automatically)
│
└── templates/
    ├── base.html            # Shared layout (navbar, footer)
    ├── index.html           # Home page
    ├── products.html        # Products page (search + pagination)
    ├── about.html           # About Us page
    ├── contact.html         # Contact page
    ├── login.html           # Admin login page
    ├── admin_base.html      # Shared admin layout (sidebar)
    ├── dashboard.html       # Admin dashboard
    ├── admin_products.html  # Admin product list/search/delete
    ├── add_product.html     # Add product form
    ├── edit_product.html    # Edit product form
    ├── company_settings.html # Edit company info
    ├── change_password.html  # Change username/password
    ├── 404.html              # Page not found
    └── 500.html              # Server error page
```

---

## 7. Changing the Default Admin Password in Code (Optional)

If you ever delete `database.db` and want a different starting password
instead of `admin@123`, edit this part of `app.py` before first run:

```python
if not Admin.query.first():
    admin = Admin(username="admin")
    admin.set_password("admin@123")   # <-- change this
```

Passwords are always stored as secure hashes (never in plain text) using
Werkzeug's password hashing.

---

## 8. Resetting the Site (Start Fresh)

To wipe all products, company info, and admin accounts and start over:

1. Stop the server (`CTRL + C`)
2. Delete the file `database.db`
3. Run `python app.py` again — it will recreate everything with defaults

⚠️ This permanently deletes all products and changes you've made. Back up
`database.db` first if you want to keep your data.

---

## 9. Deploying Online Later (When You're Ready)

Right now this runs only on your own computer. When you're ready to put it
on the internet with a real link you can share, two beginner-friendly free
options are **PythonAnywhere** and **Render**. Below are quick-start notes —
ask for more detailed step-by-step help when you're ready to do this.

### Option A — PythonAnywhere (simplest for Flask + SQLite)

1. Create a free account at pythonanywhere.com
2. Upload your project folder (or pull from GitHub)
3. Create a virtualenv and `pip install -r requirements.txt`
4. Set up a new "Web App" → Manual Configuration → Flask
5. Point the WSGI file to your `app.py`
6. Reload the web app — your site is live at `yourusername.pythonanywhere.com`

### Option B — Render

1. Push this project to a GitHub repository
2. Create a free account at render.com
3. Create a new **Web Service**, connect your GitHub repo
4. Set the start command to:
   ```
   gunicorn app:app
   ```
   (you'll need to add `gunicorn` to `requirements.txt` for this)
5. Render builds and deploys automatically — you get a live `.onrender.com` URL

### Important note for either option

SQLite works fine for getting started, but on most free hosting plans the
filesystem (including uploaded images and the database) can reset when the
app restarts or redeploys. For a permanent production setup, the next step
would be moving to a persistent database (like PostgreSQL) and persistent
file storage — happy to help set that up when you're ready to go live.

---

## 10. Support

If something doesn't run as expected, check:
- You're using Python 3.9+
- You ran `pip install -r requirements.txt` inside the project folder
- You're running `python app.py` from inside the `sar-brooms-flask` folder
  (not from one level above or below it)
