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
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
# Copy .env.example menjadi .env, lalu isi dengan konfigurasi database kamu
cp .env.example .env

# 5. Jalankan migration database
flask db upgrade

# 6. (Opsional) Seed data contoh
python -m app.helper.seed
python -m app.helper.seed_order

# 7. Jalankan server
flask run
```

Setelah server berjalan, buka `http://localhost:5000/apidocs` untuk melihat dokumentasi Swagger.

## Struktur Project

```
simple-shops/
├── run.py              # Entry point — dijalankan oleh flask run / gunicorn
├── requirements.txt    # Dependencies
├── Procfile            # Konfigurasi deployment (gunicorn)
├── .env                # Environment variables (tidak di-commit)
├── .env.example        # Template untuk .env
│
├── app/                # Semua source code aplikasi
│   ├── __init__.py     # Application factory (init_app)
│   ├── config.py       # Kelas konfigurasi (baca dari .env)
│   ├── utils.py        # Shared utilities (instance db)
│   │
│   ├── models/         # SQLAlchemy models — satu file per resource
│   │   ├── product.py  # Product model + order_products association table
│   │   ├── category.py # Category model
│   │   ├── user.py     # User model
│   │   └── order.py    # Order model
│   │
│   ├── controllers/    # Route handlers (thin — parse request, call service, return response)
│   │   ├── product_controller.py   # /store/products, /store/categories
│   │   ├── user_controller.py      # /users
│   │   ├── order_controller.py     # /orders
│   │   └── auth_controller.py      # /auth
│   │
│   ├── services/       # Business logic — DB queries, validasi, transformasi
│   │   ├── product_service.py
│   │   ├── user_service.py
│   │   ├── order_service.py
│   │   └── auth_service.py
│   │
│   ├── schemas/        # DTO (Marshmallow) — validasi request & serialisasi response
│   │   ├── product_schema.py
│   │   ├── user_schema.py
│   │   ├── order_schema.py
│   │   └── auth_schema.py
│   │
│   ├── middleware/     # Cross-cutting concerns
│   │   ├── auth.py     # hash_password, check_password, roles_required decorator
│   │   └── errors.py   # Global JSON error handlers
│   │
│   └── helper/         # Database seeding scripts
│       ├── seed.py     # Seed categories, products, users, orders
│       └── seed_order.py # Seed orders saja
│
├── tests/              # Unit & integration tests
│   ├── conftest.py     # Shared fixtures (in-memory SQLite)
│   ├── test_product.py
│   ├── test_user.py
│   └── test_order.py
│
├── migrations/         # Alembic / Flask-Migrate database migrations
│
└── doc/                # Dokumentasi lengkap
```

## Perintah Development

```bash
# Jalankan server development
flask run

# Database migration
flask db migrate -m "deskripsi perubahan"   # Buat migration baru
flask db upgrade                            # Terapkan migration ke database

# Seed database dengan data contoh
python -m app.helper.seed            # Seed categories, products, users, orders
python -m app.helper.seed_order      # Seed orders saja (butuh data user & product)

# Jalankan tests
python -m pytest tests/ -v
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
| [Arsitektur](doc/architecture.md) | Pola arsitektur MVC / layered |

## Status Project

Project ini menggunakan arsitektur **MVC / layered** dengan pemisahan yang jelas:

| Layer | Tanggung Jawab |
|-------|----------------|
| **Controllers** | Parse request, panggil service, return JSON response |
| **Services** | Business logic, DB queries, error handling |
| **Models** | Struktur data — kolom, relasi, `to_dict()` |
| **Schemas** | Validasi input (load) dan serialisasi output (dump) |
| **Middleware** | Auth decorators, password hashing, global error handlers |
