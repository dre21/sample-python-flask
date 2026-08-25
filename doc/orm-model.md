# ORM & Model

## Apa Itu ORM?

ORM (Object Relational Mapper) adalah library yang menjembatani antara kode Python dan database. Dengan ORM, kamu tidak perlu menulis SQL langsung — cukup bekerja dengan class dan object Python.

**Tanpa ORM (raw SQL):**
```sql
SELECT * FROM products WHERE price < 50;
```

**Dengan ORM (Flask-SQLAlchemy):**
```python
products = Product.query.filter(Product.price < 50).all()
```

Keduanya menghasilkan hal yang sama, tapi versi ORM lebih "Python-native" dan lebih aman dari SQL injection.

## Kenapa Pakai ORM?

1. **Tidak perlu hafal SQL** — Cukup tulis Python
2. **Aman dari SQL injection** — ORM otomatis sanitize input
3. **Portabel** — Bisa ganti database (PostgreSQL → SQLite) tanpa ubah kode
4. **Relationship otomatis** — Hubungan antar tabel mudah didefinisikan
5. **Migration** — Perubahan skema bisa di-track (lihat [migration.md](migration.md))

## Definisi Model

Model adalah class Python yang merepresentasikan satu tabel di database. Setiap property/column di class = satu kolom di tabel.

### ⚠️ Catatan: Legacy vs Modern Syntax

Project ini menggunakan **legacy syntax** (`db.Column`). Ini disengaja karena:

1. **Banyak tutorial dan referensi** di internet masih pakai syntax ini — lebih mudah dicari solusinya saat stuck
2. **Lebih eksplisit** — tipe data tertulis jelas di `db.Column(db.Integer, ...)`
3. **Masih fully supported** — SQLAlchemy dan Flask-SQLAlchemy tetap mendukung syntax ini

Legacy syntax **tidak deprecated** dan tetap bisa dipakai di production. Tapi kalau kamu mulai project baru, disarankan pakai modern syntax (lihat bagian bawah).

### Contoh Model — Legacy Syntax (Dipakai di Project Ini)

```python
from app.utils import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'  # Nama tabel di database

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    sku         = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    price       = db.Column(db.Float, nullable=False)
    stock_qty   = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.now)
```

### Contoh Model — Modern Syntax (Recommended untuk Project Baru)

Sejak SQLAlchemy 2.0 dan Flask-SQLAlchemy 3.1, ada syntax baru yang lebih "Pythonic" menggunakan **type annotation** (`Mapped` dan `mapped_column`):

```python
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.utils import db

class Product(db.Model):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    sku: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    price: Mapped[float] = mapped_column(Float)
    stock_qty: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime | None] = mapped_column(default=datetime.now)
```

### Perbandingan Legacy vs Modern

| Aspek | Legacy (`db.Column`) | Modern (`Mapped` + `mapped_column`) |
|-------|---------------------|--------------------------------------|
| Nullable | `nullable=False` eksplisit | Otomatis dari type hint (`str` = NOT NULL, `str \| None` = nullable) |
| Tipe data | `db.Integer`, `db.String` | Python type hint: `int`, `str` |
| IDE support | Minimal | Autocomplete & type checking lebih baik |
| Readability | Verbose tapi jelas | Lebih ringkas, pakai Python standard |
| Kompatibilitas | Semua versi SQLAlchemy | SQLAlchemy 2.0+ |

### Tipe-tipe Column

| Tipe | Python | Contoh |
|------|--------|--------|
| `db.Integer` | int | id, stock_qty |
| `db.String(n)` | str (max n char) | name, sku |
| `db.Text` | str (panjang tak terbatas) | description |
| `db.Float` | float | price |
| `db.Boolean` | bool | is_active |
| `db.DateTime` | datetime | created_at |

### Opsi Column

| Opsi | Arti |
|------|------|
| `primary_key=True` | Kolom ini adalah primary key |
| `nullable=False` | Tidak boleh kosong (NOT NULL) |
| `unique=True` | Nilainya harus unik di seluruh tabel |
| `default=value` | Nilai default jika tidak diisi |
| `server_default='value'` | Default yang diset di level database |

## Relasi (Relationship)

### One-to-Many

Satu Category punya banyak Product:

**Legacy syntax (dipakai di project ini):**
```python
class Category(db.Model):
    __tablename__ = 'categories'
    
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Sisi "one" — definisikan relationship
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'
    
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    
    # Sisi "many" — definisikan foreign key
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
```

**Modern syntax (recommended untuk project baru):**
```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Category(db.Model):
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # Sisi "one" — pakai back_populates (lebih eksplisit dari backref)
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(db.Model):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # Sisi "many" — foreign key
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'))
    
    # Relationship back ke Category
    category: Mapped["Category | None"] = relationship(back_populates="products")
```

> **Catatan:** Modern syntax pakai `back_populates` (dua arah eksplisit) sebagai pengganti `backref` (satu arah implisit). Keduanya masih bisa dipakai.

Cara pakai (sama untuk legacy maupun modern):
```python
# Ambil semua produk dalam satu kategori
category = Category.query.get(1)
products = category.products  # List of Product objects

# Ambil kategori dari sebuah produk
product = Product.query.get(1)
category_name = product.category.name  # "Electronics"
```

### Many-to-Many

Satu Order bisa berisi banyak Product, dan satu Product bisa ada di banyak Order:

**Legacy syntax (dipakai di project ini):**
```python
# Tabel asosiasi (junction table)
order_products = db.Table(
    'order_products',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id      = db.Column(db.Integer, primary_key=True)
    total   = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Many-to-many relationship
    products = db.relationship('Product', secondary=order_products, backref='orders')
```

**Modern syntax:**
```python
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Tabel asosiasi
order_products = db.Table(
    'order_products',
    sa.Column('order_id', sa.ForeignKey('orders.id'), primary_key=True),
    sa.Column('product_id', sa.ForeignKey('products.id'), primary_key=True),
)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    total: Mapped[float]
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id'))
    
    # Many-to-many relationship
    products: Mapped[list["Product"]] = relationship(secondary=order_products, back_populates="orders")
```

Cara pakai (sama untuk legacy maupun modern):
```python
order = Order.query.get(1)
for product in order.products:
    print(product.name)
```

## Query Database

### Query Dasar — Legacy Syntax (Dipakai di Project Ini)

Project ini menggunakan `Model.query` yang merupakan **legacy query interface** dari Flask-SQLAlchemy. Masih fully supported tapi di dokumentasi resmi sudah ditandai sebagai "legacy".

```python
# Ambil semua
products = Product.query.all()

# Ambil berdasarkan ID
product = Product.query.get(1)

# Ambil satu (atau 404)
product = Product.query.get_or_404(1)

# Filter
cheap_products = Product.query.filter(Product.price < 50).all()

# Filter by exact match
electronics = Product.query.filter_by(category_id=1).all()

# First result only
product = Product.query.filter_by(sku='WDG-001').first()
```

### Query Dasar — Modern Syntax (Recommended)

Syntax modern menggunakan `db.session.execute()` dengan `db.select()`. Ini adalah cara yang direkomendasikan di SQLAlchemy 2.0+ dan Flask-SQLAlchemy 3.1+.

```python
# Ambil semua
products = db.session.execute(db.select(Product)).scalars().all()

# Ambil berdasarkan ID
product = db.session.get(Product, 1)

# Ambil satu (atau 404)
product = db.one_or_404(db.select(Product).filter_by(id=1))

# Filter
cheap_products = db.session.execute(
    db.select(Product).filter(Product.price < 50)
).scalars().all()

# Filter by exact match
electronics = db.session.execute(
    db.select(Product).filter_by(category_id=1)
).scalars().all()

# First result only
product = db.session.execute(
    db.select(Product).filter_by(sku='WDG-001')
).scalar_one_or_none()
```

### Perbandingan Query

| Operasi | Legacy (`Model.query`) | Modern (`db.session.execute`) |
|---------|----------------------|-------------------------------|
| Semua data | `Product.query.all()` | `db.session.execute(db.select(Product)).scalars().all()` |
| By ID | `Product.query.get(1)` | `db.session.get(Product, 1)` |
| Filter | `Product.query.filter(...)` | `db.session.execute(db.select(Product).filter(...)).scalars()` |
| First | `.first()` | `.scalar_one_or_none()` |
| 404 | `.get_or_404(id)` | `db.one_or_404(db.select(...))` |

Modern syntax lebih verbose, tapi:
- Lebih konsisten dengan SQLAlchemy core
- Mendukung fitur baru SQLAlchemy 2.0 (seperti typing yang lebih baik)
- Merupakan satu-satunya cara yang didokumentasikan untuk project baru

### Operasi CRUD

```python
# CREATE
new_product = Product(name="Widget", sku="WDG-001", price=19.99)
db.session.add(new_product)
db.session.commit()

# UPDATE
product = Product.query.get(1)
product.price = 24.99
db.session.commit()

# DELETE
product = Product.query.get(1)
db.session.delete(product)
db.session.commit()
```

### Pagination

```python
# Ambil halaman ke-2, 10 item per halaman
pagination = Product.query.paginate(page=2, per_page=10, error_out=False)

pagination.items    # List produk di halaman ini
pagination.total    # Total semua produk
pagination.pages    # Total halaman
pagination.page     # Halaman saat ini
```

## Method `to_dict()`

Setiap model punya method untuk mengkonversi object ke dictionary (supaya bisa di-return sebagai JSON):

```python
class User(db.Model):
    # ... columns ...
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        # PENTING: Jangan include password_hash!
```

> **Catatan:** Di project ini, serialisasi sudah ditangani oleh DTO/Schema (lihat [dto.md](dto.md)). Method `to_dict()` tetap ada sebagai fallback.

## Instance `db` dan Circular Import

Instance SQLAlchemy (`db`) didefinisikan di file terpisah (`app/utils.py`) untuk menghindari circular import:

```python
# app/utils.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
```

Semua file lain import `db` dari `app.utils`:
```python
# app/models/product.py
from app.utils import db

class Product(db.Model):
    ...
```

## File Terkait di Project Ini

- `app/models/` — Semua definisi model (Product, Category, User, Order)
- `app/utils.py` — Instance `db` (SQLAlchemy)
- `app/services/` — Tempat query database dipanggil

## Referensi

- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.readthedocs.io/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
