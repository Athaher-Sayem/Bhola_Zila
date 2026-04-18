# 🔵 BHOLA — Django Web Application

A modern, glassmorphism-styled community platform for the BHOLA organization.
Built with Django 4.2, featuring role-based access, email verification, image compression, and a fully responsive dark UI.

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Auth | Custom AbstractBaseUser |
| Images | Pillow (compression built-in) |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Config | python-dotenv |
| Frontend | Vanilla CSS (Glassmorphism), DM Sans + Playfair Display fonts |

---

## ⚡ Quick Start

### 1. Clone / enter the project
```bash
cd bhola_project
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your values (SECRET_KEY, email settings etc.)
```

### 5. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (Admin)
```bash
python manage.py createsuperuser
# Prompts: email, name, student_id, password
```

### 7. Collect static files (production only)
```bash
python manage.py collectstatic
```

### 8. Run the development server
```bash
python manage.py runserver
```
Visit → http://127.0.0.1:8000

---

## 🔐 Role System Setup

### Creating a 2nd Admin (President, VP, etc.)

Go to **Django Admin** → **Pre Admins** → **Add Pre Admin**

Fill in:
| Field | Value |
|-------|-------|
| Name | Exactly as user will register |
| Email | Exactly as user will register |
| Designation | President / Vice President / General Secretary / Press Secretary |

When a user **registers** with a matching name + email, they are **automatically promoted** to 2nd Admin with the designation filled in their profile.

---

## 📁 Project Structure

```
bhola_project/
├── bhola/                  # Project config
│   ├── settings.py
│   └── urls.py
├── accounts/               # Auth + Users + Profiles
│   ├── models.py           # User, Profile, PreAdmin
│   ├── views.py            # signup, login, profile, team, verify
│   ├── forms.py
│   ├── signals.py          # Auto-create profile + 2nd admin check
│   └── urls.py
├── core/                   # Landing page + About
│   ├── views.py
│   └── urls.py
├── events/                 # Events + image upload
│   ├── models.py           # Event, EventImage (auto-compress)
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── notices/                # Notice board
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── gallery/                # Photo gallery (max 20)
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html           # Navbar, messages, footer
│   ├── core/               # home.html, about.html
│   ├── accounts/           # login, signup, profile, team, verify
│   ├── events/             # list, detail, form
│   ├── notices/            # list, form
│   └── gallery/            # gallery, upload
├── static/
│   ├── css/main.css        # All styles (glassmorphism dark theme)
│   └── js/main.js          # Hamburger, alerts, active nav
├── media/                  # Uploaded files (auto-created)
├── requirements.txt
└── .env.example
```

---

## 🌐 URL Map

| URL | View | Access |
|-----|------|--------|
| `/` | Landing page | Public |
| `/about/` | About page | Public |
| `/events/` | Events list | Public |
| `/events/create/` | Post event | Admin + 2nd Admin |
| `/events/<id>/` | Event detail | Public |
| `/notices/` | Notice board | Public |
| `/notices/create/` | Post notice | Admin + 2nd Admin |
| `/gallery/` | Gallery | Public |
| `/gallery/upload/` | Upload photos | Admin only |
| `/accounts/signup/` | Register | Public |
| `/accounts/login/` | Login | Public |
| `/accounts/profile/` | My profile | Logged in |
| `/accounts/team/` | Team page | Logged in |
| `/accounts/verify-members/` | Verify users | Admin + 2nd Admin |
| `/admin/` | Django admin | Superuser |

---

## 👥 User Roles

| Role | Key | Permissions |
|------|-----|------------|
| **Admin** | `admin` | Full control — everything |
| **2nd Admin** | `second_admin` | Verify members, post events, post notices |
| **Member** | `member` | Create/edit own profile, view all content |

---

## 📧 Email Verification

In **development**, email is printed to the console (check terminal output).
In **production**, set `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` in `.env` and fill in SMTP credentials.

---

## 🖼️ Image Handling

- **Events:** Max 5 images per event, each ≤ 10MB. Auto-compressed to 1200×800 JPEG at quality 75.
- **Gallery:** Max 20 photos total. Admin only.
- **Profile photos:** Uploaded to `media/profiles/`.

---

## 🛠️ Useful Management Commands

```bash
# Check for errors
python manage.py check

# Open Django shell
python manage.py shell

# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Promote a user to admin via shell
python manage.py shell
>>> from accounts.models import User
>>> u = User.objects.get(email='user@example.com')
>>> u.role = 'admin'; u.is_staff = True; u.is_superuser = True; u.save()
```

---

## 🚀 Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Set a strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Configure SMTP email
- [ ] Run `python manage.py collectstatic`
- [ ] Set up Gunicorn + Nginx
- [ ] Configure `ALLOWED_HOSTS`

---

## 🎨 Design System

- **Font:** Playfair Display (headings) + DM Sans (body)
- **Theme:** Dark glassmorphism — `#0a0e1a` background
- **Accent:** `#4f8ef7` blue / `#a78bfa` purple / `#f59e0b` gold
- **Glass:** `rgba(255,255,255,0.06)` with `backdrop-filter: blur(20px)`
- **Border:** `rgba(255,255,255,0.12)`
