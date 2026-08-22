# Arsitektur Aplikasi

> ⚠️ **Status: Belum diimplementasi** — Project saat ini masih menggunakan struktur flat. Dokumen ini menjelaskan konsep arsitektur dan rencana refactoring ke MVC.

## Apa Itu Arsitektur Software?

Arsitektur adalah cara kamu **mengorganisir kode** dalam sebuah project. Ini menentukan:
- File apa saja yang ada
- Tanggung jawab masing-masing file
- Bagaimana file-file tersebut berinteraksi

Analoginya: arsitektur itu seperti denah rumah. Kamar tidur, dapur, dan kamar mandi punya fungsi masing-masing dan diletakkan di tempat yang masuk akal.

## Kenapa Arsitektur Penting?

Saat project masih kecil (100-500 baris), taruh semua di satu file juga oke. Tapi saat project membesar:

| Masalah | Tanpa arsitektur | Dengan arsitektur |
|---------|------------------|-------------------|
| Cari kode | Scroll 2000 baris | Buka file yang tepat |
| Ubah logic | Takut rusak yang lain | Perubahan terisolasi |
| Kerja tim | Sering conflict | Masing-masing area kerja |
| Testing | Susah di-test terpisah | Tiap layer bisa di-test sendiri |

## Struktur Saat Ini (Flat)

```
simple-shops/
├── app.py          # Setup Flask, register blueprint
├── config.py       # Konfigurasi
├── models.py       # SEMUA model (Product, User, Order, Category)
├── routes.py       # SEMUA route handler
├── schemas.py      # SEMUA DTO/validation
├── auth.py         # Helper auth
├── errors.py       # Error handlers
└── utils.py        # Shared utilities
```

**Kelebihan:**
- Simpel, mudah dipahami untuk pemula
- Cepat untuk prototype
- Tidak perlu mikir banyak soal struktur

**Kekurangan:**
- `routes.py` semakin panjang seiring fitur bertambah
- Business logic bercampur dengan HTTP handling
- Sulit di-test secara terpisah

## Arsitektur MVC (Target Refactoring)

MVC = **Model - View - Controller**

Dalam konteks REST API (tanpa frontend), biasanya jadi:
- **Model** → Data layer (database)
- **Controller** → Request handler (menerima request, kirim response)
- **Service** → Business logic (aturan bisnis)

```
Request masuk
     ↓
[Controller] — Terima request, validasi input, panggil service
     ↓
[Service] — Jalankan business logic, panggil model
     ↓
[Model] — Baca/tulis database
     ↓
[Service] — Proses hasil dari model
     ↓
[Controller] — Format response, kirim ke client
```

### Tanggung Jawab Setiap Layer

| Layer | Tanggung Jawab | Contoh |
|-------|---------------|--------|
| **Controller** | Handle HTTP, validasi input, format response | Parse JSON, return 404 |
| **Service** | Business logic, aturan bisnis | "Seller tidak bisa buat order" |
| **Model** | Akses database, definisi tabel | Query, insert, update |
| **DTO** | Validasi & transformasi data | Marshmallow schemas |

### Aturan Utama

1. **Controller TIDAK boleh akses database langsung** — Harus lewat service
2. **Service TIDAK boleh tahu tentang HTTP** — Tidak import request/jsonify
3. **Model TIDAK boleh berisi business logic** — Hanya definisi data

## Rencana Struktur Baru

```
simple-shops/
├── app.py                  # Application factory
├── config.py               # Konfigurasi
│
├── controllers/            # HTTP handlers (tipis — hanya terima & kirim)
│   ├── __init__.py
│   ├── product_controller.py
│   ├── user_controller.py
│   ├── order_controller.py
│   └── auth_controller.py
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── product_service.py
│   ├── user_service.py
│   └── order_service.py
│
├── models/                 # Database models
│   ├── __init__.py
│   ├── product.py
│   ├── user.py
│   ├── order.py
│   └── category.py
│
├── dto/                    # Request/response schemas
│   ├── __init__.py
│   ├── product_dto.py
│   ├── user_dto.py
│   └── order_dto.py
│
├── middleware/             # Auth, logging, error handling
│   ├── __init__.py
│   ├── auth.py
│   ├── error_handler.py
│   └── logger.py
│
├── migrations/
└── helper/
```

## Contoh Perbandingan: Sebelum vs Sesudah

### Sebelum (Flat — Semua di routes.py)

```python
# routes.py — controller + service + database akses, semua campur
@products_bp.route('/products', methods=['POST'])
@roles_required('seller')
def create_product():
    data = request.get_json()
    
    # Validasi (DTO layer)
    validated = product_create_schema.load(data)
    
    # Business logic + database (harusnya di service)
    if validated.get('category_id'):
        category = Category.query.get(validated['category_id'])
        if category is None:
            return jsonify({"error": "Category not found"}), 404
    
    product = Product(**validated)
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product_detail_schema.dump(product)), 201
```

### Sesudah (MVC — Terpisah)

```python
# controllers/product_controller.py — hanya handle HTTP
@products_bp.route('/products', methods=['POST'])
@roles_required('seller')
def create_product():
    data = request.get_json()
    
    try:
        validated = product_create_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    product = product_service.create_product(validated)  # Delegate ke service
    return jsonify(product_detail_schema.dump(product)), 201
```

```python
# services/product_service.py — business logic
from models.product import Product
from models.category import Category
from utils import db

class ProductService:
    def create_product(self, data):
        # Validasi business rule
        if data.get('category_id'):
            category = Category.query.get(data['category_id'])
            if category is None:
                raise ValueError(f"Category {data['category_id']} not found")
        
        # Buat dan simpan product
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return product

product_service = ProductService()
```

## Kapan Harus Refactor?

**Tetap flat kalau:**
- Project masih kecil (< 10 endpoint)
- Kamu sedang belajar dasar-dasarnya
- Belum ada business logic yang kompleks

**Refactor ke MVC kalau:**
- `routes.py` sudah > 500 baris
- Business logic mulai rumit (banyak if-else, validasi custom)
- Tim mulai kerja bareng di codebase yang sama
- Mau mulai tulis unit test

## Referensi

- [Flask Application Factory](https://flask.palletsprojects.com/en/latest/patterns/appfactories/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
