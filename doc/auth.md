# Autentikasi & Otorisasi

## Perbedaan Autentikasi vs Otorisasi

| | Autentikasi (Authentication) | Otorisasi (Authorization) |
|---|---|---|
| Pertanyaan | "Siapa kamu?" | "Boleh nggak kamu akses ini?" |
| Kapan | Saat login | Setelah login, saat akses resource |
| Contoh | Verifikasi email + password | Cek apakah user punya role admin |

Analoginya:
- **Autentikasi** = Menunjukkan KTP ke satpam (membuktikan identitas)
- **Otorisasi** = Satpam cek apakah kamu boleh masuk ruangan tertentu (cek izin akses)

## JWT (JSON Web Token)

### Apa Itu JWT?

JWT adalah sebuah "token" yang diberikan server ke client setelah login berhasil. Token ini berisi informasi user (id, role) dalam format yang bisa diverifikasi tanpa perlu query database lagi.

### Alur JWT:

**1. Login — Mendapatkan Token**

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database

    C->>S: POST /auth/login {email, password}
    S->>DB: User.query.filter_by(email=email).first()
    DB-->>S: User object (atau None)

    alt User tidak ditemukan
        S-->>C: 401 {message: "Invalid email or password"}
        Note over S,C: ⚠️ Sengaja return 401 (bukan 404) dan pesan sama<br/>untuk user not found maupun wrong password.<br/>Alasan: supaya attacker tidak bisa tahu<br/>apakah email terdaftar atau tidak.
    else User ditemukan
        S->>S: check_password(password, user.password_hash) — bcrypt.checkpw()
        alt Password tidak cocok
            S-->>C: 401 {message: "Invalid email or password"}
        else Password cocok
            S->>S: create_access_token(identity=user.id, claims={role})
            S->>S: create_refresh_token(identity=user.id, claims={role})
            S-->>C: 200 {access_token, refresh_token, user}
            Note over C: Simpan token di localStorage/cookie
        end
    end
```

**2. Akses Protected Resource — Menggunakan Token**

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database

    C->>S: GET /orders (Header: Bearer <access_token>)
    S->>S: verify_jwt_in_request() — decode & verifikasi signature

    alt Token tidak ada / format salah
        S-->>C: 401 {msg: "Missing Authorization Header"}
    else Token expired
        S-->>C: 401 {msg: "Token has expired"}
    else Token valid
        S->>S: get_jwt() — baca claims (role, identity)
        S->>S: Cek role: claims["role"] in allowed_roles?
        alt Role tidak sesuai
            S-->>C: 403 {error: "Forbidden", message: "Required role(s): user"}
        else Role sesuai
            S->>DB: Query data (Order.query.all())
            DB-->>S: Data
            S-->>C: 200 {orders: [...]}
        end
    end
```

### Struktur JWT

JWT terdiri dari 3 bagian yang dipisahkan titik:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbmRyZSIsInJvbGUiOiJzZWxsZXIifQ.9kZ9m7lWwv3...
└─────── header ──────┘ └────────────── payload ──────────────────────┘ └─ signature ─┘
```

| Part | Isi | Signed? |
|------|-----|---------|
| **Header** | Algoritma (`HS256`) dan tipe token (`JWT`) | yes |
| **Payload** | Claims: `sub` (user id), `role`, `exp` (expiry), `iat` (issued at) | yes |
| **Signature** | `HMAC-SHA256(header + "." + payload, SECRET_KEY)` | the key |

Setiap bagian di-encode dengan Base64URL. Artinya kamu bisa **membaca isi token** (header & payload) tanpa secret key — tapi tidak bisa **memalsukan** token tanpa secret key.

> 💡 Coba decode JWT kamu di [jwt.io](https://jwt.io/) — paste token, dan kamu bisa lihat isinya langsung.

### Implementasi di Project Ini

**Login (membuat token):**

```python
from flask_jwt_extended import create_access_token, create_refresh_token

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    # Verifikasi password
    if user is None or not check_password(data['password'], user.password_hash):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Buat token — identity adalah user ID, claims berisi role
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200
```

**Proteksi route (verifikasi token):**

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@products_bp.route('/categories/<int:id>', methods=['GET'])
@jwt_required()  # Decorator ini mewajibkan valid JWT
def get_category(id):
    current_user_id = get_jwt_identity()  # Ambil user ID dari token
    ...
```

Client harus kirim token di header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Access Token vs Refresh Token

| | Access Token | Refresh Token |
|---|---|---|
| Fungsi | Akses resource | Minta access token baru |
| Masa berlaku | Pendek (1 jam) | Panjang (30 hari) |
| Dikirim ke | Semua endpoint | Hanya `/auth/refresh` |

Kenapa 2 token?
- Access token sengaja berumur pendek supaya kalau dicuri, cuma valid sebentar
- Refresh token dipakai untuk minta access token baru tanpa harus login ulang

**Alur refresh token:**

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    C->>S: GET /orders (Bearer <access_token>)
    S-->>C: 401 Unauthorized (token expired)

    C->>S: POST /auth/refresh (Bearer <refresh_token>)
    S->>S: Verifikasi refresh token
    S-->>C: 200 OK {access_token: "new_token"}

    C->>S: GET /orders (Bearer <new_access_token>)
    S-->>C: 200 OK {orders: [...]}
```

```python
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Harus pakai refresh token
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_access_token}), 200
```

## Password Hashing

Password **TIDAK BOLEH** disimpan sebagai plain text di database. Kita pakai **bcrypt** untuk meng-hash password:

```python
import bcrypt

def hash_password(plain_password):
    """Hash password sebelum disimpan ke database."""
    return bcrypt.hashpw(
        plain_password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')

def check_password(plain_password, hashed_password):
    """Verifikasi password saat login."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
```

Kenapa hashing?
- Jika database bocor, password tetap aman (tidak bisa dibaca)
- Bcrypt sengaja lambat untuk mencegah brute force attack
- Salt (random data) membuat hash yang berbeda untuk password yang sama

## RBAC (Role-Based Access Control)

### Apa Itu RBAC?

RBAC adalah sistem otorisasi di mana akses ditentukan berdasarkan **role** user. Di project ini ada 3 role:

| Role | Akses |
|------|-------|
| `user` | Lihat order sendiri |
| `seller` | CRUD produk |
| `admin` | Hapus produk, akses penuh |

### Implementasi: `roles_required` Decorator

```python
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def roles_required(*allowed_roles):
    """
    Decorator untuk membatasi akses berdasarkan role.
    
    Cara kerja:
    1. Verifikasi JWT valid
    2. Baca role dari JWT claims
    3. Cek apakah role ada di list yang diizinkan
    4. Tolak dengan 403 jika tidak sesuai
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "user")
            
            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Required role(s): {', '.join(allowed_roles)}"
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
```

### Cara Pakai

```python
@products_bp.route('/products', methods=['POST'])
@roles_required('seller')          # Hanya seller yang bisa create product
def create_product():
    ...

@products_bp.route('/products/<int:id>', methods=['DELETE'])
@roles_required('admin')           # Hanya admin yang bisa delete
def delete_product(id):
    ...

@orders_bp.route('/orders', methods=['GET'])
@roles_required('user')            # Minimal role user
def get_orders():
    ...
```

### Di Mana Role Disimpan?

1. **Di database** — Kolom `role` di tabel `users`
2. **Di JWT token** — Sebagai `additional_claims` saat login
3. **Di setiap request** — Dibaca dari JWT oleh decorator

```python
# Saat login, role dimasukkan ke token
access_token = create_access_token(
    identity=str(user.id),
    additional_claims={"role": user.role}  # ← role masuk ke token
)
```

## Alur Lengkap

```mermaid
flowchart TD
    A[Client kirim request] --> B{Endpoint butuh auth?}
    B -->|Tidak| C[Proses request langsung]
    B -->|Ya| D{Ada JWT di header?}
    D -->|Tidak| E[401 Unauthorized]
    D -->|Ya| F{Token valid & belum expired?}
    F -->|Tidak| G{Token expired?}
    G -->|Ya| H[Client pakai refresh token]
    G -->|Tidak/Invalid| E
    H --> I{Refresh token valid?}
    I -->|Ya| J[Server kirim access token baru]
    I -->|Tidak| K[401 — Harus login ulang]
    F -->|Ya| L{Role sesuai?}
    L -->|Ya| C
    L -->|Tidak| M[403 Forbidden]
    C --> N[Return response]
```

### Contoh Step-by-Step

```
1. Register:
   Client → POST /users/register {username, email, password, role}
   Server → Hash password, simpan ke DB → 201 Created

2. Login:
   Client → POST /auth/login {email, password}
   Server → Verifikasi → Return access_token + refresh_token

3. Akses Protected Route:
   Client → GET /orders (Header: Authorization: Bearer <token>)
   Server → Verifikasi token → Cek role → Proses request → 200 OK
  
4. Jika token expired:
   Client → POST /auth/refresh (Header: Authorization: Bearer <refresh_token>)
   Server → Return new access_token
```

## File Terkait di Project Ini

- `auth.py` — `hash_password()`, `check_password()`, `roles_required()` decorator
- `routes.py` — Login/register endpoint, penggunaan decorator di route
- `config.py` — JWT configuration (secret key, expiration time)
- `models.py` — User model dengan kolom `role` dan `password_hash`

## Referensi

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [JWT.io](https://jwt.io/) — Decoder dan penjelasan JWT
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
