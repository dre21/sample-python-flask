# Logging

> **Status: Sudah diimplementasi** — Dokumen ini menjelaskan konsep logging dan implementasinya di project ini.

## Apa Itu Logging?

Logging adalah proses mencatat event/kejadian yang terjadi di aplikasi. Bayangkan seperti **CCTV untuk kode** — kamu bisa lihat apa yang terjadi, kapan, dan di mana.

## Kenapa Butuh Logging?

Bayangkan server kamu error jam 3 pagi. Tanpa logging:
- "Apa yang terjadi?" → Tidak tahu
- "Kapan mulai error?" → Tidak tahu
- "Request mana yang gagal?" → Tidak tahu

Dengan logging:
```
2024-03-15 03:12:45 | ERROR    | app.services.order_service | Failed to create order: IntegrityError on user_id=42
2024-03-15 03:12:45 | INFO     | app.controllers.order_controller | POST /orders — user_id=42
```

Sekarang kamu bisa debug tanpa harus mereproduksi error-nya.

## Level Logging

Python punya 5 level logging, dari paling ringan ke paling serius:

| Level | Kapan Dipakai | Contoh |
|-------|---------------|--------|
| `DEBUG` | Detail teknis untuk debugging | `"Applied filters: {'name': 'widget'}"` |
| `INFO` | Event normal yang penting | `"Product created — id=5, name='Widget'"` |
| `WARNING` | Sesuatu yang tidak seharusnya terjadi, tapi app masih jalan | `"Create product failed — category_id=99 not found"` |
| `ERROR` | Ada yang gagal di sistem kita | `"Error creating product: IntegrityError"` |
| `CRITICAL` | App tidak bisa berjalan | `"Database connection lost"` |

## Implementasi di Project Ini

### Konfigurasi (`app/config.py`)

```python
class Config:
    # FLASK_ENV controls which log level is used
    FLASK_ENV = os.getenv('FLASK_ENV', 'local')

    # Optional: override log level directly (takes priority over FLASK_ENV)
    LOG_LEVEL = os.getenv('LOG_LEVEL', None)

    # Log format — timestamp, level, logger name, message
    LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    # Map environment names to log levels
    LOG_LEVEL_MAP = {
        'local': 'DEBUG',
        'development': 'INFO',
        'production': 'WARNING',
    }

    @classmethod
    def get_log_level(cls):
        """Priority: LOG_LEVEL env var > FLASK_ENV mapping > default DEBUG"""
        if cls.LOG_LEVEL:
            return cls.LOG_LEVEL.upper()
        return cls.LOG_LEVEL_MAP.get(cls.FLASK_ENV, 'DEBUG')
```

### Environment dan Log Level

| `.env` setting | Level | Apa yang terlihat | Kapan dipakai |
|---|---|---|---|
| `FLASK_ENV=local` | **DEBUG** | Semua — filter, raw args, item counts | Development di laptop sendiri |
| `FLASK_ENV=development` | **INFO** | Request summary, query results, startup | Server development (staging) |
| `FLASK_ENV=production` | **WARNING** | Hanya warning dan error | Server production |

### Setup di `.env`

```bash
# Laptop sendiri — lihat semua detail
FLASK_ENV=local

# Server development — cukup info saja
FLASK_ENV=development

# Server production — quiet, hanya masalah
FLASK_ENV=production

# Atau override langsung:
LOG_LEVEL=DEBUG
```

### Inisialisasi (`app/__init__.py`)

```python
import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging(app):
    log_level = Config.get_log_level()
    formatter = logging.Formatter(Config.LOG_FORMAT, datefmt=Config.LOG_DATE_FORMAT)

    # Console handler — output ke terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # File handler — rotasi harian, simpan 7 hari terakhir
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',       # Rotasi setiap tengah malam
        interval=1,            # Setiap 1 hari
        backupCount=7,         # Simpan 7 hari terakhir
        encoding='utf-8',
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.suffix = '%Y-%m-%d'

    # Set root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
```

### File Log yang Dihasilkan

```
logs/
├── app.log              ← log hari ini (aktif)
├── app.log.2026-08-26   ← kemarin (otomatis dibuat saat rotasi)
├── app.log.2026-08-25   ← 2 hari lalu
└── ...                  ← sampai 7 hari, lalu auto-delete
```

- Folder `logs/` dibuat otomatis saat app pertama kali start
- Sudah ditambahkan ke `.gitignore` — tidak masuk ke Git

## Contoh Penggunaan: Get All Products

### Di Controller (`app/controllers/product_controller.py`)

```python
import logging

logger = logging.getLogger(__name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    # ... parse request args ...

    logger.info("GET /store/products — page=%d, per_page=%d", page, per_page)
    logger.debug("Request args: %s", request.args.to_dict())

    pagination = product_service.get_products(filters, page, per_page)

    logger.debug("Returning %d items to client", len(pagination.items))

    return jsonify({...}), 200
```

### Di Service (`app/services/product_service.py`)

```python
import logging

logger = logging.getLogger(__name__)

def get_products(filters, page, per_page):
    logger.info("Fetching products — page=%d, per_page=%d", page, per_page)
    logger.debug("Applied filters: %s", filters)

    query = Product.query

    if filters.get('name'):
        query = query.filter(Product.name.icontains(filters['name']))
        logger.debug("Filter by name: '%s'", filters['name'])

    # ... more filters ...

    result = query.paginate(page=page, per_page=per_page, error_out=False)
    logger.info("Found %d products (page %d of %d)", result.total, result.page, result.pages)

    return result
```

### Contoh Penggunaan WARNING dan ERROR

```python
def create_product(validated_data):
    # WARNING — client memberikan data yang salah (bukan crash)
    if category is None:
        logger.warning("Create product failed — category_id=%d not found",
                       validated_data['category_id'])

    try:
        product = Product(**validated_data)
        db.session.commit()
        logger.info("Product created — id=%d, name='%s'", product.id, product.name)
    except Exception as e:
        db.session.rollback()
        # ERROR — ada yang gagal di sistem kita, exc_info=True untuk traceback lengkap
        logger.error("Error creating product: %s", e, exc_info=True)
```

## Output Per Environment

### `FLASK_ENV=local` (DEBUG) — Laptop Development

```
2026-08-27 10:30:01 | INFO     | app.controllers.product_controller | GET /store/products — page=2, per_page=10
2026-08-27 10:30:01 | DEBUG    | app.controllers.product_controller | Request args: {'name': 'widget', 'page': '2'}
2026-08-27 10:30:01 | INFO     | app.services.product_service | Fetching products — page=2, per_page=10
2026-08-27 10:30:01 | DEBUG    | app.services.product_service | Applied filters: {'name': 'widget', 'category_id': None, 'max_price': None}
2026-08-27 10:30:01 | DEBUG    | app.services.product_service | Filter by name: 'widget'
2026-08-27 10:30:01 | INFO     | app.services.product_service | Found 3 products (page 2 of 1)
2026-08-27 10:30:01 | DEBUG    | app.controllers.product_controller | Returning 3 items to client
```

### `FLASK_ENV=development` (INFO) — Server Development

```
2026-08-27 10:30:01 | INFO     | app.controllers.product_controller | GET /store/products — page=2, per_page=10
2026-08-27 10:30:01 | INFO     | app.services.product_service | Fetching products — page=2, per_page=10
2026-08-27 10:30:01 | INFO     | app.services.product_service | Found 3 products (page 2 of 1)
```

### `FLASK_ENV=production` (WARNING) — Server Production

```
(kosong — request berhasil, tidak ada warning/error)
```

Tapi kalau ada masalah di production:
```
2026-08-27 10:30:01 | WARNING  | app.services.product_service | Create product failed — category_id=99 not found
2026-08-27 10:31:15 | ERROR    | app.services.product_service | Error creating product: IntegrityError
Traceback (most recent call last):
  File ".../product_service.py", line 78, in create_product
    db.session.commit()
  ...
```

## File Handler: Blocking Operation

> **Penting untuk dipahami:** `TimedRotatingFileHandler` adalah **blocking operation**.

Ketika kode memanggil `logger.info(...)`, proses penulisan ke file terjadi **secara sinkron** — thread request menunggu sampai log ditulis ke disk sebelum melanjutkan.

### Apakah ini masalah?

| Skenario | Impact |
|---|---|
| Project ini (learning, low traffic) | **Tidak masalah** — file write hanya ~5-50 mikrodetik |
| Medium traffic (ratusan request/detik) | Masih OK — OS melakukan buffering |
| High traffic (ribuan request/detik) | Bisa jadi bottleneck |

Dibandingkan database query (1–50ms), file write (5–50μs) itu sangat cepat. Untuk Simple Shops, ini **tidak perlu dikhawatirkan**.

### Improvement: Non-Blocking dengan QueueHandler

Kalau suatu saat traffic tinggi, bisa pakai `QueueHandler` — log masuk ke antrian di memory, lalu background thread yang menulis ke file:

```python
import logging
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from queue import Queue

# Queue sebagai buffer antara kode dan file
log_queue = Queue()

# Handler ini instant (non-blocking) — hanya taruh di queue
queue_handler = QueueHandler(log_queue)

# Background thread membaca queue dan menulis ke file
file_handler = TimedRotatingFileHandler('logs/app.log', when='midnight', backupCount=7)
listener = QueueListener(log_queue, file_handler)
listener.start()  # Mulai background writer thread

# Root logger pakai queue_handler, bukan file_handler langsung
root_logger = logging.getLogger()
root_logger.addHandler(queue_handler)
```

**Kapan upgrade ke QueueHandler:**
- Traffic > 1000 request/detik
- Response time sangat kritis (single-digit milliseconds)
- Disk I/O lambat (network-attached storage)

Untuk saat ini, `TimedRotatingFileHandler` sudah lebih dari cukup.

## Perbedaan `print()` vs `logging`

| | `print()` | `logging` |
|---|---|---|
| Output | stdout saja | Console + file + external service |
| Level | Tidak ada | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| Format | Manual | Otomatis (timestamp, level, module) |
| Rotasi file | Tidak bisa | Bisa (harian, berdasar ukuran, dll) |
| Production | Harus dihapus | Tetap ada, tinggal atur level |
| Kontrol | Tidak bisa dimatikan per modul | Bisa filter per level dan per modul |
| Performa | Selalu dieksekusi | Bisa skip berdasar level |

## Tips Logging

1. **Jangan log data sensitif** — Password, token, credit card number
2. **Log konteks yang cukup** — Siapa (user_id), apa (action), hasilnya apa
3. **Gunakan level yang tepat** — Error bukan INFO, sukses bukan WARNING
4. **Pakai `exc_info=True`** — Untuk exception, supaya traceback ikut ke-log
5. **Jangan over-log** — Log yang terlalu banyak sama buruknya dengan tidak ada log
6. **Pakai `%s` formatting** — Bukan f-string, supaya string tidak dibuild kalau level dimatikan

```python
# Bagus — string hanya dibuild kalau level DEBUG aktif
logger.debug("Filters: %s", filters)

# Kurang bagus — f-string SELALU dibuild, meskipun DEBUG dimatikan
logger.debug(f"Filters: {filters}")
```

## Pattern untuk Module Baru

Setiap kali buat file Python baru, tambahkan di atas:

```python
import logging

logger = logging.getLogger(__name__)
```

`__name__` otomatis berisi nama module (contoh: `app.services.order_service`), jadi kamu selalu tahu log itu dari mana.

## Referensi

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Python Logging Handlers](https://docs.python.org/3/library/logging.handlers.html)
- [Flask Logging](https://flask.palletsprojects.com/en/latest/logging/)
- [12-Factor App: Logs](https://12factor.net/logs)
