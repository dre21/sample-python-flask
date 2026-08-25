# Database Migration

## Apa Itu Migration?

Migration adalah sistem untuk melacak dan mengelola perubahan skema database secara bertahap. Setiap kali kamu mengubah model (tambah kolom, buat tabel baru, dll), migration akan membuat "script" yang mencatat perubahan tersebut.

Analoginya: migration itu seperti **Git untuk database**. Setiap perubahan skema tercatat, bisa dijalankan maju (upgrade) atau mundur (downgrade).

## Kenapa Butuh Migration?

**Tanpa migration:**
- Kamu ubah model di Python → database tidak otomatis ikut berubah
- Harus ALTER TABLE manual di database
- Tim lain tidak tahu perubahan apa yang kamu buat
- Tidak bisa rollback kalau ada masalah

**Dengan migration:**
- Ubah model → jalankan `flask db migrate` → script otomatis dibuat
- `flask db upgrade` → perubahan diterapkan ke database
- `flask db downgrade` → rollback ke versi sebelumnya
- Semua perubahan tercatat dan bisa di-share ke tim

## Tools yang Dipakai

- **Flask-Migrate** — Wrapper Flask untuk Alembic
- **Alembic** — Library migration yang bekerja dengan SQLAlchemy

## Alur Kerja Migration

```
1. Ubah model di models.py (tambah kolom, tabel baru, dll)
         ↓
2. flask db migrate -m "deskripsi perubahan"
   → Alembic bandingkan model vs database saat ini
   → Buat file migration di migrations/versions/
         ↓
3. Review file migration yang dihasilkan
         ↓
4. flask db upgrade
   → Jalankan migration, ubah database
```

## Command yang Dipakai

```bash
# Generate migration baru (setelah ubah model)
flask db migrate -m "add status to orders"

# Terapkan migration ke database
flask db upgrade

# Rollback satu langkah
flask db downgrade

# Lihat migration history
flask db history

# Lihat migration saat ini
flask db current
```

## Contoh Migration Script

Ini contoh migration yang menambahkan kolom `status` ke tabel `orders`:

```python
# migrations/versions/81ba850b3f42_add_status_to_orders.py

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '81ba850b3f42'
down_revision = '799f44d4a7e3'  # Migration sebelumnya

def upgrade():
    """Perubahan maju — tambahkan kolom."""
    op.add_column('orders', sa.Column('status', sa.String(length=20), nullable=True))

def downgrade():
    """Perubahan mundur — hapus kolom (rollback)."""
    op.drop_column('orders', 'status')
```

Penjelasan:
- `revision` — ID unik migration ini
- `down_revision` — ID migration sebelumnya (membentuk chain)
- `upgrade()` — Apa yang dilakukan saat maju
- `downgrade()` — Apa yang dilakukan saat rollback

## Operasi Umum di Migration

| Operasi | Code |
|---------|------|
| Tambah kolom | `op.add_column('table', sa.Column('name', sa.String(100)))` |
| Hapus kolom | `op.drop_column('table', 'column_name')` |
| Buat tabel | `op.create_table('table', sa.Column(...), ...)` |
| Hapus tabel | `op.drop_table('table')` |
| Tambah foreign key | `op.create_foreign_key(...)` |
| Tambah index | `op.create_index(...)` |

## Migration di Project Ini

Urutan migration yang sudah ada:

```
1. ae02c647efd4 — Initial tables (products, users)
2. eea9716b8411 — Add category model and FK to products
3. e6d9856f2e02 — Add role to users
4. 799f44d4a7e3 — Add order model and order_products junction table
5. 81ba850b3f42 — Add status to orders
```

## Struktur Folder

```
migrations/
├── alembic.ini         # Konfigurasi Alembic
├── env.py              # Setup environment migration (auto-detect model)
├── script.py.mako      # Template untuk file migration baru
├── versions/           # Semua migration script
│   ├── ae02c647efd4_initial_tables.py
│   ├── eea9716b8411_add_category_model_and_fk_to_products.py
│   ├── e6d9856f2e02_add_role_to_users.py
│   ├── 799f44d4a7e3_add_order_model_and_order_products_.py
│   └── 81ba850b3f42_add_status_to_orders.py
└── README
```

## Tips Penting

1. **Selalu review migration** sebelum `upgrade` — kadang auto-generate tidak sempurna
2. **Jangan edit migration yang sudah di-upgrade** — buat migration baru saja
3. **Pesan migration harus deskriptif** — `"add status to orders"` ✅, `"update"` ❌
4. **Commit migration ke Git** — supaya tim lain bisa `flask db upgrade` juga
5. **Satu perubahan, satu migration** — jangan gabung banyak perubahan dalam satu file

### ⚠️ Gotcha: Foreign Key Naming di PostgreSQL

Saat menjalankan `flask db downgrade` di PostgreSQL, kamu mungkin menemukan error seperti:

```
sqlalchemy.exc.CompilerError: Can't emit DROP CONSTRAINT for constraint ForeignKeyConstraint(...); 
it has no name
```

**Masalahnya:** Alembic perlu nama constraint yang eksplisit untuk bisa DROP. Kalau constraint tidak punya nama (None), downgrade gagal.

**Solusinya:** Definisikan **naming convention** di metadata SQLAlchemy, sehingga semua constraint (FK, PK, unique, index) otomatis punya nama yang konsisten:

```python
# app/utils.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
```

Dengan naming convention ini, foreign key akan otomatis punya nama seperti `fk_products_category_id_categories`, dan downgrade tidak akan error lagi.

> 💡 **Pelajaran:** Selalu setup naming convention di awal project. Kalau sudah terlanjur tanpa naming convention, kamu harus re-generate migration dari awal atau manual edit migration file-nya.

## Kapan Harus Membuat Migration?

| Perubahan | Butuh Migration? |
|-----------|:---:|
| Tambah model/tabel baru | ✅ |
| Tambah/hapus kolom | ✅ |
| Ubah tipe kolom | ✅ |
| Tambah/hapus relasi (foreign key) | ✅ |
| Ubah logika di method model (to_dict) | ❌ |
| Ubah route/controller | ❌ |
| Ubah validasi (schema) | ❌ |

## File Terkait di Project Ini

- `migrations/` — Folder berisi semua migration
- `migrations/env.py` — Konfigurasi environment Alembic
- `app/models/` — Model yang di-track oleh migration
- `app/__init__.py` — Tempat Flask-Migrate diinisialisasi

## Referensi

- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
