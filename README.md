# Simple Shops API

Sebuah REST API sederhana untuk toko online, dibangun menggunakan **Python Flask**. Project ini dibuat sebagai contoh belajar backend development untuk pemula.

## Tentang Project Ini

Simple Shops adalah API e-commerce sederhana yang mencakup fitur-fitur umum sebuah backend:

- CRUD (Create, Read, Update, Delete) untuk produk, kategori, user, dan order
- Autentikasi user dengan JWT (login & register)
- Otorisasi berbasis role (admin, seller, user)
- Relasi database (one-to-many, many-to-many)
- Pagination dan filtering
- Validasi input dengan DTO (Data Transfer Object)
- Dokumentasi API otomatis dengan Swagger

## Tech Stack

| Teknologi | Kegunaan |
|-----------|----------|
| Python 3.9+ | Bahasa pemrograman |
| Flask 3.1 | Web framework |
| Flask-SQLAlchemy 3.1 | ORM (Object Relational Mapper) |
| Flask-Migrate 4.1 | Database migration |
| Flask-JWT-Extended 4.7 | Autentikasi JWT |
| bcrypt 4.2 | Hashing password |
| Marshmallow | Validasi & serialisasi data (DTO) |
| Flasgger 0.9 | Swagger UI / dokumentasi API |
| PostgreSQL | Database |

## Cara Menjalankan

```bash
# 1. Clone repository
git clone <repo-url>
cd simple-shops

# 2. Buat virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
# Copy .env.example menjadi .env, lalu isi dengan konfigurasi database kamu
copy .env.example .env

# 5. Jalankan migration database
flask db upgrade

# 6. (Opsional) Seed data contoh
python -m helper.seed
python -m helper.seed_order

# 7. Jalankan server
flask run
```

Setelah server berjalan, buka `http://localhost:5000/apidocs` untuk melihat dokumentasi Swagger.

## Struktur Project

```
simple-shops/
├── app.py              # Application factory — membuat dan mengkonfigurasi Flask app
├── config.py           # Kelas konfigurasi (baca dari .env)
├── models.py           # Semua model SQLAlchemy (Product, Category, User, Order)
├── routes.py           # Semua route handler (Blueprints)
├── schemas.py          # DTO — validasi input & serialisasi output (Marshmallow)
├── auth.py             # Helper password hashing & RBAC decorator
├── errors.py           # Centralized error handler
├── validation.py       # Validasi manual (legacy, digantikan schemas.py)
├── utils.py            # Shared utilities (instance db)
├── requirements.txt    # Dependencies
├── .env                # Environment variables (tidak di-commit)
│
├── migrations/         # Database migration scripts (Alembic)
├── helper/             # Script seeding database
└── doc/                # Dokumentasi lengkap (lihat di bawah)
```

## Dokumentasi Lengkap

Untuk memahami konsep-konsep yang dipakai dalam project ini, baca dokumentasi berikut:

| Dokumen | Topik |
|---------|-------|
| [Framework Flask](doc/flask.md) | Apa itu Flask dan kenapa kita pakai |
| [Routing & REST API](doc/routing-rest-api.md) | Cara kerja routing dan prinsip REST |
| [ORM & Model](doc/orm-model.md) | Cara definisi model dan query database |
| [Autentikasi & Otorisasi](doc/auth.md) | JWT, login, dan role-based access control |
| [DTO & Validasi](doc/dto.md) | Validasi input dan format output dengan Marshmallow |
| [Database Migration](doc/migration.md) | Cara kelola perubahan skema database |
| [Swagger / Dokumentasi API](doc/swagger.md) | Cara buat dokumentasi API otomatis |
| [Logging](doc/logging.md) | Konsep logging (belum diimplementasi) |
| [Arsitektur](doc/architecture.md) | Pola arsitektur MVC (belum diimplementasi) |

## Status Project

Project ini masih dalam pengembangan. Saat ini masih menggunakan struktur flat (satu file per concern). Ke depannya akan di-refactor ke arsitektur MVC dengan controller, service, dan data access layer yang terpisah.

