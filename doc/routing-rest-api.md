# Routing & REST API

## Apa Itu Routing?

Routing adalah proses mengarahkan HTTP request ke fungsi yang tepat berdasarkan URL dan HTTP method-nya.

Contoh sederhana:
- `GET /store/products` → panggil fungsi `get_products()`
- `POST /store/products` → panggil fungsi `create_product()`
- `GET /store/products/5` → panggil fungsi `get_product(5)`

Jadi routing itu seperti "resepsionis" yang mengarahkan tamu (request) ke ruangan (fungsi) yang benar.

## Apa Itu REST API?

REST (Representational State Transfer) adalah **konvensi** dalam mendesain API. Bukan library, bukan framework — hanya "aturan main" yang disepakati bersama supaya API konsisten dan mudah dipahami.

### Prinsip Utama REST:

1. **Resource-based** — API didesain berdasarkan "sumber daya" (products, users, orders)
2. **HTTP Methods** — Gunakan method HTTP yang sesuai untuk tiap aksi
3. **Stateless** — Setiap request berdiri sendiri, server tidak menyimpan state client
4. **Uniform Interface** — URL konsisten dan bisa ditebak

### HTTP Methods & Artinya:

| Method | Arti | Contoh |
|--------|------|--------|
| GET | Ambil data | `GET /products` → ambil semua produk |
| POST | Buat data baru | `POST /products` → buat produk baru |
| PUT | Update data (keseluruhan) | `PUT /products/1` → update produk id 1 |
| PATCH | Update data (sebagian) | `PATCH /products/1` → update beberapa field |
| DELETE | Hapus data | `DELETE /products/1` → hapus produk id 1 |

### Status Code:

| Code | Arti | Kapan Dipakai |
|------|------|---------------|
| 200 | OK | Request berhasil |
| 201 | Created | Data baru berhasil dibuat |
| 400 | Bad Request | Input dari client salah |
| 401 | Unauthorized | Belum login / token tidak valid |
| 403 | Forbidden | Sudah login tapi tidak punya akses |
| 404 | Not Found | Resource tidak ditemukan |
| 500 | Internal Server Error | Ada error di server |

## Routing di Flask

### Definisi Route Dasar

```python
from flask import Blueprint, jsonify

products_bp = Blueprint('products', __name__, url_prefix='/store')

@products_bp.route('/products', methods=['GET'])
def get_products():
    # Logic ambil semua produk
    return jsonify({"products": [...]}), 200
```

Penjelasan:
- `@products_bp.route('/products', methods=['GET'])` — Dekorator yang mendaftarkan fungsi sebagai handler untuk URL `/store/products` dengan method GET
- `url_prefix='/store'` — Semua route di blueprint ini otomatis diawali `/store`

### Route dengan Parameter

```python
@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product.to_dict()), 200
```

`<int:product_id>` artinya Flask akan menangkap bagian URL tersebut sebagai integer dan meneruskannya sebagai parameter fungsi.

### Membaca Data dari Request

```python
from flask import request

@products_bp.route('/products', methods=['POST'])
def create_product():
    # Baca JSON body
    data = request.get_json()
    
    # Baca query parameter: GET /products?page=2&per_page=10
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
```

### Pagination

Untuk list yang panjang, kita tidak mau kirim semua data sekaligus. Gunakan pagination:

```python
@products_bp.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Product.query.paginate(page=page, per_page=per_page)

    return jsonify({
        "products": [p.to_dict() for p in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages
    }), 200
```

### Filtering

Client bisa filter data menggunakan query parameter:

```python
# GET /store/products?name=widget&max_price=50
query = Product.query

if 'name' in request.args:
    name = request.args.get('name')
    query = query.filter(Product.name.icontains(name))

if 'max_price' in request.args:
    max_price = request.args.get('max_price', type=float)
    query = query.filter(Product.price <= max_price)
```

## Endpoint di Project Ini

| Method | URL | Fungsi | Auth? |
|--------|-----|--------|-------|
| GET | `/store/products` | List semua produk | Tidak |
| POST | `/store/products` | Buat produk baru | Seller |
| GET | `/store/products/<id>` | Detail produk | Tidak |
| PUT | `/store/products/<id>` | Update produk | Seller |
| DELETE | `/store/products/<id>` | Hapus produk | Admin |
| GET | `/store/categories/<id>` | Detail kategori | Ya |
| POST | `/users/register` | Register user | Tidak |
| GET | `/users/<id>` | Detail user | Tidak |
| POST | `/auth/login` | Login | Tidak |
| POST | `/auth/refresh` | Refresh token | Ya |
| GET | `/orders` | List order | User |
| GET | `/orders/<id>` | Detail order | User |

## Tips Desain REST API

1. **Gunakan noun, bukan verb** di URL: `/products` ✅, `/getProducts` ❌
2. **Plural untuk collection**: `/products` (bukan `/product`)
3. **HTTP method menentukan aksi**, bukan URL
4. **Konsisten** — kalau satu resource pakai `/resource/<id>`, semua resource juga begitu
5. **Return status code yang tepat** — jangan selalu 200

## File Terkait di Project Ini

- `routes.py` — Semua route handler
- `app.py` — Tempat blueprint didaftarkan

## Referensi

- [REST API Best Practices](https://restfulapi.net/)
- [Flask Routing Documentation](https://flask.palletsprojects.com/en/latest/quickstart/#routing)
