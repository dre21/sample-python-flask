# Framework Flask

## Apa Itu Web Framework?

Ketika kamu membuat backend, kamu butuh menangani banyak hal: menerima HTTP request, parsing URL, membaca body request, mengirim response, dll. Web framework adalah library yang sudah menyediakan semua fungsi dasar ini, jadi kamu tinggal fokus menulis logika bisnis.

Analoginya: framework itu seperti kerangka rumah yang sudah jadi. Kamu tinggal isi furnitur dan dekorasi (logika bisnis), tanpa perlu bangun fondasi dari nol.

## Kenapa Flask?

Ada banyak framework Python untuk backend: Django, FastAPI, Flask, dll. Kita pilih **Flask** karena:

1. **Minimalis** — Flask tidak memaksa kamu pakai struktur tertentu. Kamu bebas mengatur sendiri.
2. **Mudah dipahami** — Kode Flask sangat eksplisit, tidak ada "magic" tersembunyi.
3. **Cocok untuk belajar** — Kamu bisa lihat langsung bagaimana setiap bagian bekerja.
4. **Ekosistem besar** — Banyak library extension (SQLAlchemy, JWT, Migrate, dll).

## Konsep Dasar Flask

### 1. Application Factory

Di project ini, kita membuat Flask app menggunakan pola **application factory** — sebuah fungsi yang membuat dan mengkonfigurasi app:

```python
# app/__init__.py
from flask import Flask

def init_app():
    app = Flask(__name__)
    
    # Konfigurasi
    app.config.from_object(Config)
    
    # Setup extensions (db, jwt, swagger, dll)
    db.init_app(app)
    
    # Register routes
    app.register_blueprint(products_bp)
    
    return app
```

Kenapa pakai factory?
- Lebih mudah untuk testing (bisa buat app dengan konfigurasi berbeda)
- Menghindari circular import
- Konfigurasi lebih terorganisir

### 2. Configuration

Konfigurasi disimpan dalam sebuah class yang membaca environment variables:

```python
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Baca file .env

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
```

Kenapa pakai environment variable?
- **Keamanan** — password dan secret key tidak boleh ditulis langsung di kode
- **Fleksibilitas** — bisa beda konfigurasi untuk development, testing, dan production
- File `.env` tidak di-commit ke Git (ada di `.gitignore`)

### 3. Blueprint

Blueprint adalah cara Flask mengelompokkan route yang berhubungan. Bayangkan seperti "modul" yang bisa didaftarkan ke app:

```python
# app/controllers/product_controller.py
from flask import Blueprint

products_bp = Blueprint('products', __name__, url_prefix='/store')

@products_bp.route('/products', methods=['GET'])
def get_products():
    ...
```

```python
# app/__init__.py — mendaftarkan blueprint
app.register_blueprint(products_bp)
```

Hasilnya, semua route di `products_bp` akan punya prefix `/store`, jadi endpoint-nya menjadi `/store/products`.

### 4. Request & Response

Flask menyediakan object `request` untuk membaca data masuk, dan `jsonify()` untuk mengirim response JSON:

```python
from flask import request, jsonify

@products_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()       # Baca JSON dari request body
    name = data.get('name')
    
    # ... proses data ...
    
    return jsonify({"message": "Created"}), 201  # Kirim JSON response
```

### 5. Extension

Flask punya banyak extension yang tinggal "colok":

| Extension | Fungsi |
|-----------|--------|
| Flask-SQLAlchemy | ORM untuk database |
| Flask-Migrate | Migration database |
| Flask-JWT-Extended | Autentikasi JWT |
| Flasgger | Swagger documentation |

Setiap extension biasanya di-inisialisasi di `app.py` menggunakan pola `extension.init_app(app)`.

## Cara Flask Bekerja (Simplified)

```
Client mengirim HTTP request
        ↓
Flask menerima request
        ↓
Flask mencocokkan URL → route handler yang sesuai
        ↓
Route handler memproses request (baca db, validasi, dll)
        ↓
Route handler return response (JSON + status code)
        ↓
Flask mengirim HTTP response ke client
```

## File Terkait di Project Ini

- `app/__init__.py` — Application factory, inisialisasi semua extension
- `app/config.py` — Kelas konfigurasi
- `app/controllers/` — Semua route handler menggunakan Blueprint
- `run.py` — Entry point (dijalankan oleh `flask run` atau gunicorn)

## Referensi

- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
