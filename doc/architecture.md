# Arsitektur Aplikasi Simple Shops

## Diagram

```mermaid
graph TD
    %% Client Layer
    Client["🌐 Client (Browser / Postman)"]

    %% Flask App Layer
    subgraph App["Flask Application (app.py)"]
        direction TB
        Swagger["Flasgger (Swagger UI)<br>/apidocs"]
        JWT["Flask-JWT-Extended"]
        Migrate["Flask-Migrate (Alembic)"]
    end

    %% Middleware Layer
    subgraph Middleware["middleware/"]
        direction TB
        Auth["auth.py<br>hash_password()<br>check_password()<br>roles_required()"]
        Errors["errors.py<br>register_error_handlers()"]
    end

    %% Controller Layer
    subgraph Controllers["controllers/"]
        direction TB
        ProductCtrl["product_controller.py<br>products_bp (/store)"]
        UserCtrl["user_controller.py<br>users_bp (/users)"]
        OrderCtrl["order_controller.py<br>orders_bp (/orders)"]
        AuthCtrl["auth_controller.py<br>auth_bp (/auth)"]
    end

    %% Schema Layer
    subgraph Schemas["schemas/"]
        direction TB
        ProductSchema["product_schema.py<br>Create / Update / List / Detail"]
        UserSchema["user_schema.py<br>Register / Detail"]
        OrderSchema["order_schema.py<br>List / Detail / Product"]
        AuthSchema["auth_schema.py<br>Login"]
    end

    %% Service Layer
    subgraph Services["services/"]
        direction TB
        ProductSvc["product_service.py"]
        UserSvc["user_service.py"]
        OrderSvc["order_service.py"]
        AuthSvc["auth_service.py"]
    end

    %% Model Layer
    subgraph Models["models/"]
        direction TB
        ProductModel["product.py<br>Product + order_products"]
        CategoryModel["category.py<br>Category"]
        UserModel["user.py<br>User"]
        OrderModel["order.py<br>Order"]
    end

    %% Database
    DB[("PostgreSQL<br>Database")]

    %% Utils
    Utils["utils.py<br>db = SQLAlchemy()"]

    %% Config
    Config["config.py<br>DATABASE_URL, JWT_SECRET_KEY"]

    %% Connections
    Client -->|"HTTP Request"| App
    App --> Middleware
    App --> Controllers

    Middleware -.->|"Dekorator & Error Handler"| Controllers

    Controllers -->|"Validasi Input"| Schemas
    Controllers -->|"Panggil Logika Bisnis"| Services

    Services -->|"Query & Mutasi"| Models
    Models -->|"ORM Mapping"| Utils
    Utils -->|"SQL Query"| DB

    Config -.->|"Konfigurasi"| App
    Migrate -.->|"Migrasi Skema"| DB
```

## Penjelasan Diagram

### Alur Request (dari atas ke bawah)

1. **Client** — Pengguna mengirim HTTP request (GET, POST, PUT, DELETE) ke server Flask. Bisa melalui browser, Postman, atau aplikasi frontend.

2. **Flask Application (`app.py`)** — Entry point aplikasi. Di sini Flask di-inisialisasi bersama extension-nya:
   - **Flasgger** — menghasilkan dokumentasi Swagger UI otomatis di `/apidocs`
   - **Flask-JWT-Extended** — menangani pembuatan dan validasi token JWT
   - **Flask-Migrate** — mengelola migrasi database menggunakan Alembic

3. **Middleware (`middleware/`)** — Lapisan yang menangani concern lintas fitur:
   - **`auth.py`** — berisi fungsi hashing password (`bcrypt`) dan dekorator `roles_required()` yang memproteksi endpoint berdasarkan role user (admin, seller, user)
   - **`errors.py`** — mengubah semua error HTTP (400, 404, 500) menjadi response JSON yang konsisten

4. **Controllers (`controllers/`)** — Lapisan tipis yang menerima request. Tugasnya:
   - Mengambil data dari request body/query parameter
   - Memvalidasi input menggunakan schema
   - Memanggil service yang sesuai
   - Mengembalikan response JSON ke client
   - Setiap controller memiliki satu Blueprint dengan URL prefix-nya masing-masing

5. **Schemas (`schemas/`)** — Lapisan DTO (Data Transfer Object) menggunakan Marshmallow:
   - **Load** — memvalidasi data input (tipe data, required fields, panjang string, range angka)
   - **Dump** — mengubah objek model menjadi JSON response yang bersih (tanpa field sensitif seperti password)

6. **Services (`services/`)** — Lapisan logika bisnis. Di sinilah "kerja nyata" terjadi:
   - Query database (filter, pagination)
   - Validasi bisnis (cek apakah kategori ada, cek duplikasi email)
   - Operasi CRUD (create, read, update, delete)
   - Error handling dan rollback transaksi

7. **Models (`models/`)** — Definisi struktur tabel database menggunakan SQLAlchemy ORM:
   - Setiap model merepresentasikan satu tabel di PostgreSQL
   - Mendefinisikan kolom, foreign key, dan relationship antar tabel
   - Memiliki method `to_dict()` untuk serialisasi sederhana

8. **Utils (`utils.py`)** — Berisi instance `db = SQLAlchemy()` yang digunakan oleh semua model. Diletakkan terpisah untuk menghindari circular import.

9. **PostgreSQL Database** — Tempat penyimpanan data permanen. Diakses melalui ORM (tidak ada raw SQL).

### Hubungan Antar Lapisan

| Dari | Ke | Jenis Hubungan |
|------|-----|---------------|
| Controller → Schema | Validasi input & serialisasi output |
| Controller → Service | Delegasi logika bisnis |
| Service → Model | Query dan mutasi data |
| Model → Utils (db) | Mapping ORM ke tabel database |
| Middleware → Controller | Dekorator proteksi (auth, error handling) |
| Config → App | Menyediakan environment variables |

### Prinsip Desain

- **Separation of Concerns** — setiap lapisan punya tanggung jawab tunggal
- **Thin Controllers** — controller tidak boleh berisi logika bisnis, hanya "terima request → panggil service → kirim response"
- **Fat Services** — semua logika bisnis terpusat di service layer
- **Single Direction** — data mengalir satu arah: Controller → Service → Model → Database


## Referensi

- [Flask Application Factory](https://flask.palletsprojects.com/en/latest/patterns/appfactories/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
