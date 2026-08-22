# Logging

> ⚠️ **Status: Belum diimplementasi** — Dokumen ini menjelaskan konsep logging dan rencana implementasi di project ini.

## Apa Itu Logging?

Logging adalah proses mencatat event/kejadian yang terjadi di aplikasi. Bayangkan seperti **CCTV untuk kode** — kamu bisa lihat apa yang terjadi, kapan, dan di mana.

## Kenapa Butuh Logging?

Bayangkan server kamu error jam 3 pagi. Tanpa logging:
- "Apa yang terjadi?" → Tidak tahu
- "Kapan mulai error?" → Tidak tahu
- "Request mana yang gagal?" → Tidak tahu

Dengan logging:
```
[2024-03-15 03:12:45] ERROR - Failed to create order: IntegrityError on user_id=42
[2024-03-15 03:12:45] INFO  - Request: POST /orders from IP 192.168.1.100
```

Sekarang kamu bisa debug tanpa harus mereproduksi error-nya.

## Level Logging

Python punya 5 level logging, dari paling ringan ke paling serius:

| Level | Kapan Dipakai | Contoh |
|-------|---------------|--------|
| `DEBUG` | Detail teknis untuk debugging | `"Query returned 42 rows"` |
| `INFO` | Event normal yang penting | `"User john logged in"` |
| `WARNING` | Sesuatu yang perlu diperhatikan | `"Disk usage at 85%"` |
| `ERROR` | Ada yang gagal, tapi app masih jalan | `"Failed to send email"` |
| `CRITICAL` | App tidak bisa berjalan | `"Database connection lost"` |

Di production, biasanya level diset ke `INFO` (jadi DEBUG tidak muncul). Saat debugging, bisa diturunkan ke `DEBUG`.

## Logging di Python

Python sudah punya module `logging` built-in:

```python
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Cara pakai
logger.info("User %s logged in", username)
logger.error("Failed to create order: %s", str(error))
logger.warning("Slow query detected: %dms", duration)
```

## Rencana Implementasi

### Yang Akan Di-log:

1. **Request masuk** — Method, URL, IP address
2. **Response keluar** — Status code, waktu proses
3. **Auth events** — Login berhasil/gagal, token expired
4. **Database errors** — Query gagal, constraint violation
5. **Business events** — Order dibuat, produk diupdate

### Contoh Implementasi (Rencana)

```python
# Middleware untuk log setiap request
@app.before_request
def log_request():
    logger.info("Request: %s %s from %s", 
                request.method, request.path, request.remote_addr)

@app.after_request
def log_response(response):
    logger.info("Response: %s %s → %d", 
                request.method, request.path, response.status_code)
    return response
```

```python
# Di route handler
@products_bp.route('/products', methods=['POST'])
def create_product():
    try:
        product = Product(**validated)
        db.session.add(product)
        db.session.commit()
        logger.info("Product created: id=%d, name=%s", product.id, product.name)
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to create product: %s", str(e))
        return jsonify({"error": "Error creating product"}), 500
```

### Format Log yang Baik

```
# Format yang informatif
2024-03-15 10:30:45 - routes - INFO - Product created: id=5, name=Widget
2024-03-15 10:31:02 - auth - WARNING - Failed login attempt for email=john@test.com
2024-03-15 10:31:15 - routes - ERROR - Failed to create order: IntegrityError

# Format yang buruk
2024-03-15 - error happened
2024-03-15 - something went wrong
```

## Perbedaan `print()` vs `logging`

| | `print()` | `logging` |
|---|---|---|
| Output | stdout saja | File, console, external service |
| Level | Tidak ada | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| Format | Manual | Otomatis (timestamp, level, module) |
| Production | Harus dihapus | Tetap ada, tinggal atur level |
| Kontrol | Tidak bisa dimatikan per modul | Bisa filter per level dan per modul |

Di project ini saat ini masih pakai `print()` di beberapa tempat. Ke depannya akan diganti dengan proper logging.

## Tips Logging

1. **Jangan log data sensitif** — Password, token, credit card number ❌
2. **Log konteks yang cukup** — Siapa (user_id), apa (action), hasilnya apa
3. **Gunakan level yang tepat** — Error bukan INFO, sukses bukan WARNING
4. **Structured logging** — Kalau bisa, pakai format JSON untuk mudah di-parse
5. **Jangan over-log** — Log yang terlalu banyak sama buruknya dengan tidak ada log

## Referensi

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Flask Logging](https://flask.palletsprojects.com/en/latest/logging/)
- [12-Factor App: Logs](https://12factor.net/logs)
