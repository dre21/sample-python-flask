# DTO & Validasi

## Apa Itu DTO?

DTO (Data Transfer Object) adalah "penjaga gerbang" antara client dan server. Tugasnya:

1. **Validasi input** — Memastikan data yang masuk sesuai format yang diharapkan
2. **Serialisasi output** — Mengontrol data apa saja yang dikirim ke client

Analoginya: DTO itu seperti petugas keamanan bandara. Data yang masuk (request) harus lewat pemeriksaan dulu. Data yang keluar (response) juga difilter supaya tidak bocor informasi sensitif.

## Kenapa Butuh DTO?

**Tanpa DTO:**
```python
@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    # Tidak ada validasi! Client bisa kirim apa saja:
    # {"price": "bukan angka", "name": ""}  ← lolos ke database
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
```

**Dengan DTO:**
```python
@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    try:
        validated = product_create_schema.load(data)  # Validasi di sini
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400  # Tolak kalau invalid
    
    product = Product(**validated)  # Data sudah bersih dan aman
```

## Marshmallow

Di project ini kita pakai library **Marshmallow** untuk membuat DTO. Marshmallow menyediakan:
- Definisi field dengan tipe data
- Validasi otomatis (required, min/max, format email, dll)
- Serialisasi (object → dict/JSON)
- Deserialisasi (dict/JSON → validated data)

## Definisi Schema

### Schema untuk Input (Request Validation)

```python
from marshmallow import Schema, fields, validate

class ProductCreateSchema(Schema):
    """DTO untuk membuat produk baru. Semua field required harus ada."""
    
    name        = fields.Str(required=True, validate=validate.Length(min=5, max=100))
    sku         = fields.Str(required=True, validate=validate.Length(min=5, max=50))
    description = fields.Str(load_default=None)
    price       = fields.Float(required=True, validate=validate.Range(min=0))
    stock_qty   = fields.Int(load_default=0, validate=validate.Range(min=0))
    is_active   = fields.Bool(load_default=True)
    category_id = fields.Int(load_default=None)
```

Penjelasan:
- `required=True` — Field wajib ada di request
- `load_default=None` — Kalau tidak ada, pakai None sebagai default
- `validate=validate.Length(min=5)` — Minimal 5 karakter
- `validate=validate.Range(min=0)` — Tidak boleh negatif

### Schema untuk Partial Update

```python
class ProductUpdateSchema(Schema):
    """DTO untuk update produk. Semua field optional — hanya field yang dikirim yang di-update."""
    
    name        = fields.Str(validate=validate.Length(min=5, max=100))
    sku         = fields.Str(validate=validate.Length(min=5, max=50))
    description = fields.Str()
    price       = fields.Float(validate=validate.Range(min=0))
    stock_qty   = fields.Int(validate=validate.Range(min=0))
    is_active   = fields.Bool()
    category_id = fields.Int()
```

Bedanya dengan Create: tidak ada `required=True`. Kalau field tidak dikirim, tidak masalah.

### Schema untuk Output (Response Serialization)

```python
class ProductListSchema(Schema):
    """DTO untuk response list produk — hanya field yang perlu ditampilkan."""
    
    id        = fields.Int(dump_only=True)
    name      = fields.Str()
    sku       = fields.Str()
    price     = fields.Float()
    stock_qty = fields.Int()
    category  = fields.Method("get_category_name")
    is_active = fields.Bool()
    
    def get_category_name(self, obj):
        """Resolve nama kategori dari relasi."""
        return obj.category.name if obj.category else None


class ProductDetailSchema(ProductListSchema):
    """DTO detail produk — inherit dari list, tambahkan field ekstra."""
    
    description = fields.Str()
    created_at  = fields.DateTime(format="iso")
```

Penjelasan:
- `dump_only=True` — Field ini hanya muncul di output, tidak diterima di input
- `fields.Method("get_category_name")` — Custom logic untuk mengambil data dari relasi
- Inheritance — `ProductDetailSchema` mewarisi semua field dari `ProductListSchema`

## Cara Pakai

### Validasi Input (load)

```python
from marshmallow import ValidationError
from schemas import ProductCreateSchema

product_create_schema = ProductCreateSchema()

@products_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    try:
        validated = product_create_schema.load(data)
        # validated adalah dict yang sudah bersih dan valid
    except ValidationError as err:
        # err.messages berisi detail error per field
        return jsonify({"errors": err.messages}), 400
    
    product = Product(**validated)
    db.session.add(product)
    db.session.commit()
```

Contoh error response:
```json
{
  "errors": {
    "name": ["Shorter than minimum length 5."],
    "price": ["Missing data for required field."]
  }
}
```

### Serialisasi Output (dump)

```python
from schemas import ProductDetailSchema, ProductListSchema

product_detail_schema = ProductDetailSchema()
product_list_schema   = ProductListSchema(many=True)  # many=True untuk list

@products_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product_detail_schema.dump(product)), 200

@products_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify(product_list_schema.dump(products)), 200  # Serialize list
```

## Validator yang Tersedia

| Validator | Fungsi | Contoh |
|-----------|--------|--------|
| `validate.Length(min, max)` | Panjang string | `min=5, max=100` |
| `validate.Range(min, max)` | Range angka | `min=0` |
| `validate.OneOf([...])` | Harus salah satu dari list | `["user", "seller", "admin"]` |
| `fields.Email()` | Format email valid | otomatis |
| `required=True` | Field wajib ada | — |

## Pola Pemisahan Input vs Output

```
Request (input):     ProductCreateSchema.load(data)   → validated dict
                     ProductUpdateSchema.load(data)   → validated dict (partial)

Response (output):   ProductListSchema.dump(product)  → JSON (ringkas)
                     ProductDetailSchema.dump(product) → JSON (lengkap)
```

Kenapa pisah?
- **Input schema** menentukan apa yang client boleh kirim
- **Output schema** menentukan apa yang client boleh lihat
- Contoh: password_hash tidak pernah ada di output schema

## Contoh Schema Lain di Project Ini

```python
class UserRegisterSchema(Schema):
    username      = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    email         = fields.Email(required=True)
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    role          = fields.Str(required=True, validate=validate.OneOf(["user", "seller", "admin"]))

class UserDetailSchema(Schema):
    """Output schema — perhatikan password_hash TIDAK ada di sini."""
    id         = fields.Int(dump_only=True)
    username   = fields.Str()
    role       = fields.Str()
    email      = fields.Email()
    created_at = fields.DateTime(format="iso")

class LoginSchema(Schema):
    email    = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))
```

## File Terkait di Project Ini

- `schemas.py` — Semua definisi schema (DTO)
- `routes.py` — Tempat schema dipakai untuk validasi dan serialisasi
- `validation.py` — Validasi manual lama (sebelum pakai Marshmallow, masih ada sebagai referensi)

## Referensi

- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [Marshmallow Validators](https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html)
