# ChurnAI — Overview & Dokumentasi Proyek

> Aplikasi web prediksi churn pelanggan e-commerce berbasis LightGBM.
> Stack: FastAPI · Jinja2 · Chart.js · Vanilla JS

---

## Daftar Isi

1. [Status Proyek](#1-status-proyek)
2. [Struktur Proyek](#2-struktur-proyek)
3. [Penjelasan Tiap File](#3-penjelasan-tiap-file)
4. [Cara Menjalankan](#4-cara-menjalankan)
5. [Cara Generate Data](#5-cara-generate-data)
6. [Cara Test API](#6-cara-test-api)
7. [Hasil Test API](#7-hasil-test-api)
8. [Fitur Dashboard](#8-fitur-dashboard)
9. [Panduan UI Designer](#9-panduan-ui-designer)
10. [Kontak & Pembagian Tugas](#10-kontak--pembagian-tugas)

---

## 1. Status Proyek

| Bagian | Status | Dikerjakan oleh |
|---|---|---|
| Backend (API, logika, ML pipeline) | ✅ Selesai | Backend Dev |
| Database / Penyimpanan Data | ✅ Selesai (in-memory) | Backend Dev |
| Endpoint prediksi & insight | ✅ Selesai & sudah diuji | Backend Dev |
| Frontend — Struktur & Integrasi | ✅ Selesai | Backend Dev |
| Frontend — Tampilan Visual & UI | ✅ Selesai (dark theme) | Backend Dev |
| Deployment | ✅ Selesai (Railway) | Backend Dev |

### Apa yang Sudah Selesai

- **Upload CSV** → sistem membaca file, memproses setiap baris, dan mengembalikan hasil prediksi
- **Prediksi Manual** → mengisi form 18 kolom, sistem langsung mengeluarkan hasil
- **Dashboard Insight** → menampilkan ringkasan data dan bisa difilter
- **Download Hasil** → hasil prediksi bisa diunduh kembali dalam format CSV
- **Swagger / API Docs** → dokumentasi API tersedia di `/docs`
- **Test Suite** → 18/18 passed, tidak ada bug pada sisi backend
- **Model LightGBM** → F1=0.984, Recall=0.968, ROC-AUC=0.9996

---

## 2. Struktur Proyek

```
DigitalSkola-ECommerce/
│
├── app/                          ← Backend (Python / FastAPI)
│   ├── main.py
│   ├── routers/
│   │   ├── predict.py
│   │   └── insight.py
│   ├── services/
│   │   ├── pipeline.py
│   │   └── insight_service.py
│   └── schemas/
│       └── customer.py
│
├── model/                        ← File model ML
│   ├── model_lightgbm.pkl
│   └── preprocessor.pkl
│
├── static/
│   ├── css/
│   │   └── dashboard.css         ← Design system dark theme
│   └── js/
│       ├── charts.js
│       ├── upload.js
│       └── manual.js
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── predict.html
│   └── result.html
│
├── test_api.py                   ← Test suite 18 kasus
├── requirements.txt
├── Dockerfile
└── Procfile
```

---

## 3. Penjelasan Tiap File

### Backend — `app/`

#### `app/main.py`
**Entry point aplikasi FastAPI.**

- Membuat instance `FastAPI` dengan judul, deskripsi, dan versi
- Saat server start, memuat model ML ke memori (via `lifespan`)
- Mount folder `static/` agar CSS dan JS bisa diakses browser
- Mendaftarkan dua router: `predict` dan `insight`
- Mendefinisikan 3 route halaman HTML:
  - `GET /` → Dashboard
  - `GET /predict` → Halaman Prediksi
  - `GET /result` → Halaman Hasil Batch

```
Server start
  └─ load_models()          ← model + preprocessor masuk RAM
       └─ siap terima request
```

---

#### `app/routers/predict.py`
**Semua endpoint yang berhubungan dengan prediksi.**

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/predict/manual` | POST | Prediksi 1 pelanggan dari JSON |
| `/api/predict/csv` | POST | Prediksi batch dari file CSV |
| `/api/predict/result/{session_id}` | GET | Ambil hasil batch dari server |
| `/api/predict/download/{session_id}` | GET | Unduh hasil batch sebagai CSV |
| `/api/predict/template` | GET | Unduh template CSV kosong |

Fitur penting:
- **Flexible column matching** — kolom CSV bisa ditulis dengan format apapun (snake_case, spasi, huruf besar-kecil)
- **Session storage** — hasil prediksi batch disimpan sementara di memori dengan UUID unik
- **Validasi kolom** — jika ada kolom yang kurang, API langsung return error 400 dan daftar kolom yang hilang

---

#### `app/routers/insight.py`
**Endpoint untuk data dashboard dan filter.**

| Endpoint | Method | Query Params | Fungsi |
|---|---|---|---|
| `/api/insight/summary` | GET | gender, city_tier, marital_status, tenure_min, tenure_max | Ringkasan statistik |
| `/api/insight/charts` | GET | (sama) | Data untuk semua chart |
| `/api/insight/clear` | DELETE | — | Reset semua data prediksi |

---

#### `app/services/pipeline.py`
**Inti logika inferensi machine learning.**

```
Input data (dict / DataFrame)
  │
  ├─ _fix_categoricals()     ← koreksi nilai tidak konsisten
  │    Phone → Mobile Phone
  │    CC → Credit Card
  │    COD → Cash on Delivery
  │
  ├─ df[18 kolom]            ← pastikan urutan kolom benar
  │
  ├─ preprocessor.transform() ← StandardScaler + OneHotEncoder
  │    output: 30 fitur
  │
  └─ model.predict_proba()   ← LightGBM
       └─ { churn_label, churn_probability, risk_level }
```

Klasifikasi risk level:
- **Low** → probabilitas < 30%
- **Medium** → probabilitas 30%–70%
- **High** → probabilitas ≥ 70%

Flag `MODEL_ENABLED`:
- `True` → jalankan model asli (mode production)
- `False` → kembalikan mock output (mode testing tanpa model)

---

#### `app/services/insight_service.py`
**Mesin analitik in-memory untuk data dashboard.**

- Setiap prediksi yang masuk disimpan ke `_prediction_store` (list di RAM)
- Endpoint summary dan charts membaca dari store ini
- Store bisa di-reset via endpoint DELETE
- **Tidak ada database** — data hilang saat server di-restart

Yang dihitung:
- Total pelanggan, total churn, churn rate, jumlah per risk level
- Distribusi churn per tenure group, kategori produk, marital status, payment mode
- Histogram distribusi probabilitas (10 bucket)
- Semua bisa difilter oleh gender, city tier, marital status, dan range tenure

---

#### `app/schemas/customer.py`
**Definisi bentuk data menggunakan Pydantic.**

`CustomerInput` — 18 fitur wajib:
```
Tenure, CityTier, WarehouseToHome, HourSpendOnApp,
NumberOfDeviceRegistered, SatisfactionScore, NumberOfAddress,
Complain, OrderAmountHikeFromlastYear, CouponUsed,
OrderCount, DaySinceLastOrder, CashbackAmount,
PreferredLoginDevice, PreferredPaymentMode, Gender,
PreferedOrderCat, MaritalStatus
```

`PredictionResult` — output prediksi:
```
churn_label        : 0 (tidak churn) atau 1 (churn)
churn_probability  : float antara 0.0 – 1.0
risk_level         : "Low" / "Medium" / "High"
```

---

### Model ML — `model/`

#### `model/model_lightgbm.pkl`

| Metric | Nilai |
|---|---|
| Precision | 1.000 |
| Recall | 0.968 |
| F1-Score | 0.984 |
| ROC-AUC | 0.9996 |

Best params: `num_leaves=31, n_estimators=300, max_depth=10, learning_rate=0.1`

#### `model/preprocessor.pkl`
`ColumnTransformer` yang sudah di-fit dari training data.
- `StandardScaler` → 13 fitur numerik
- `OneHotEncoder` → 5 fitur kategorikal
- Output: 30 fitur siap masuk model

---

### Frontend — `static/js/`

#### `static/js/charts.js`
- Memanggil `/api/insight/summary` → update 4 angka metric
- Memanggil `/api/insight/charts` → render 6 chart Chart.js
- Mengelola filter dan reset dashboard

#### `static/js/upload.js`
- Drag-and-drop dan file picker → validasi format `.csv`
- Kirim `FormData` ke `POST /api/predict/csv`
- Render tabel preview 10 baris pertama + quick stat

#### `static/js/manual.js`
- Kumpulkan nilai form → kirim ke `POST /api/predict/manual`
- Render gauge chart semi-circle via Chart.js
- Generate insight teks berdasarkan nilai fitur

---

### Design System — `static/css/dashboard.css`

| Variable | Nilai | Kegunaan |
|---|---|---|
| `--bg` | `#0a0a0a` | Background halaman |
| `--surface` | `#111111` | Background card |
| `--surface-2` | `#1a1a1a` | Background input, tabel header |
| `--border` | `#2a2a2a` | Border semua elemen |
| `--accent` | `#50c878` | Warna utama (emerald green) |
| `--high` | `#e05252` | Badge High Risk / Churn |
| `--medium` | `#f59e0b` | Badge Medium Risk |
| `--low` | `#50c878` | Badge Low Risk |

---

## 4. Cara Menjalankan

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan server
uvicorn app.main:app --reload

# 3. Akses aplikasi
# Dashboard : http://localhost:8000
# Predict   : http://localhost:8000/predict
# Results   : http://localhost:8000/result
# API Docs  : http://localhost:8000/docs

# 4. Jalankan test (pastikan server sudah berjalan)
python test_api.py
```

---

## 5. Cara Generate Data

File `data_generator.py` digunakan untuk membuat data pelanggan dummy dalam format CSV.

### Cara Pakai

```bash
python data_generator.py
```

Output: file `churn_1k.csv` berisi 1.000 baris data pelanggan acak.

### Ubah Jumlah Data

Buka `data_generator.py`, ubah nilai `n` di baris 6:

```python
n = 1_000  # ganti angka ini, misal 5000 untuk 5k baris
```

### Data yang Digenerate

| Kolom | Tipe | Contoh Nilai |
|---|---|---|
| CustomerID | String | C000001, C000002, ... |
| Tenure | Integer 1–60 | 10 (bulan) |
| PreferredLoginDevice | Kategorikal | Mobile Phone (70%), Computer (25%), Tablet (5%) |
| CityTier | Integer 1–3 | 1 (40%), 2 (35%), 3 (25%) |
| WarehouseToHome | Integer 5–50 | 15 (km) |
| PreferredPaymentMode | Kategorikal | Debit Card, Credit Card, UPI, COD, E wallet |
| Gender | Kategorikal | Male / Female |
| HourSpendOnApp | Integer 1–5 | 3 (jam/hari) |
| NumberOfDeviceRegistered | Integer 1–6 | 3 |
| PreferedOrderCat | Kategorikal | Laptop & Accessory, Mobile Phone, Fashion, Grocery, Others |
| SatisfactionScore | Integer 1–5 | 3 |
| MaritalStatus | Kategorikal | Single (45%), Married (45%), Divorced (10%) |
| NumberOfAddress | Integer 1–7 | 3 |
| Complain | Integer 0/1 | 0 (80%), 1 (20%) |
| OrderAmountHikeFromlastYear | Integer 0–30 | 15 (%) |
| CouponUsed | Integer 0–10 | 2 |
| OrderCount | Integer 1–15 | 3 |
| DaySinceLastOrder | Integer 0–30 | 5 |
| CashbackAmount | Integer 50–500 | 180 |

> File hasil generate (`churn_1k.csv`) bisa langsung diupload ke halaman `/predict` untuk test prediksi batch.

---

## 6. Cara Test API

File `test_api.py` berisi 18 test case otomatis yang mengecek semua endpoint API.

### Syarat

Server harus **sudah berjalan** sebelum test dijalankan:
```bash
uvicorn app.main:app --reload
```

### Perintah Dasar

```bash
# Test ke server lokal (default)
python test_api.py

# Test ke URL custom (misal server Railway)
python test_api.py --url https://nama-app.up.railway.app

# Mode verbose — tampilkan response body tiap test
python test_api.py --verbose
```

### Apa yang Diuji

| Kategori | Jumlah Test | Yang Dicek |
|---|---|---|
| Infrastructure | 3 | Server hidup, halaman HTML render, Swagger `/docs` accessible |
| Prediction Endpoints | 3 | Prediksi manual normal, prediksi high-risk, batch CSV 3 baris |
| Column Matching | 3 | CSV snake_case, kolom ekstra diabaikan, kolom kurang → error 400 |
| Batch Result & Download | 3 | Fetch hasil by session, download CSV, download template |
| Insight & Filter | 4 | Summary tanpa filter, summary dengan filter gender, charts 6 dataset, charts dengan filter |
| Edge Cases | 1 | Session ID tidak valid → 404 |
| Cleanup | 1 | Reset semua data → store kembali 0 |

### Contoh Output

```
  ChurnAI API Test Suite
  Target: http://localhost:8000
  ──────────────────────────────────────────────────

  ── Infrastructure
  ✓  GET /api/insight/summary — server health  12ms
  ✓  GET / /predict /result — HTML pages render  45ms
  ✓  GET /docs — Swagger UI  8ms

  ── Prediction Endpoints
  ✓  POST /api/predict/manual — single prediction  23ms
  ✓  POST /api/predict/manual — high-risk profile  18ms
  ✓  POST /api/predict/csv — batch 3 rows + CustomerID  31ms
  ...

  ██████████████████  18/18 passed
```

### Kalau Ada Test yang Gagal

Output akan menampilkan tanda `✗` dan keterangan errornya:
```
  ✗  POST /api/predict/manual — single prediction
     HTTP 500 — Pipeline error: ...
```

Cek error di terminal server (tempat uvicorn berjalan) untuk detail lengkapnya.

---

## 7. Hasil Test API

Dijalankan dengan model LightGBM aktif (`MODEL_ENABLED = True`).

```
██████████████████  18/18 passed
```

### Infrastructure

| # | Test | Status | Detail |
|---|---|---|---|
| 1 | `GET /api/insight/summary` — server health | ✅ Pass | `total_customers=0` |
| 2 | `GET /` `/predict` `/result` — HTML render | ✅ Pass | 3 halaman OK |
| 3 | `GET /docs` — Swagger UI | ✅ Pass | Accessible |

### Prediction Endpoints

| # | Test | Status | Detail |
|---|---|---|---|
| 4 | `POST /api/predict/manual` — single prediction | ✅ Pass | `label=0 prob=0.0013 risk=Low` |
| 5 | `POST /api/predict/manual` — high-risk profile | ✅ Pass | `prob=0.0437 risk=Low` |
| 6 | `POST /api/predict/csv` — batch 3 baris + CustomerID | ✅ Pass | `total=3 session_id=...` |

### Column Matching

| # | Test | Status | Detail |
|---|---|---|---|
| 7 | CSV dengan nama kolom snake_case | ✅ Pass | Kolom dicocokkan otomatis |
| 8 | CSV dengan kolom ekstra yang tidak dikenal | ✅ Pass | Kolom ekstra diabaikan |
| 9 | CSV dengan kolom yang kurang | ✅ Pass | Return 400 + daftar kolom hilang |

### Batch Result & Download

| # | Test | Status | Detail |
|---|---|---|---|
| 10 | `GET /api/predict/result/{session_id}` | ✅ Pass | Fetch 3 baris |
| 11 | `GET /api/predict/download/{session_id}` | ✅ Pass | CSV 3 baris |
| 12 | `GET /api/predict/template` | ✅ Pass | 19 kolom, 2 contoh baris |

### Insight & Filter

| # | Test | Status | Detail |
|---|---|---|---|
| 13 | `GET /api/insight/summary` — tanpa filter | ✅ Pass | `total=7 churn=0 rate=0.0%` |
| 14 | `GET /api/insight/summary?gender=Male` | ✅ Pass | `all=7 → gender=Male: 5` |
| 15 | `GET /api/insight/charts` — semua 6 dataset | ✅ Pass | `churn=0 non-churn=7` |
| 16 | `GET /api/insight/charts?marital_status=Single&city_tier=1` | ✅ Pass | Filter terapkan |

### Edge Cases & Cleanup

| # | Test | Status | Detail |
|---|---|---|---|
| 17 | `GET /api/predict/result/invalid` — session tidak ada | ✅ Pass | Return `404` |
| 18 | `DELETE /api/insight/clear` — reset semua data | ✅ Pass | Store kembali ke 0 |

---

## 8. Fitur Dashboard

### Halaman 1 — Dashboard (`/`)

#### Filter Global

| Filter | Pilihan |
|---|---|
| Gender | Male / Female / Semua |
| City Tier | Tier 1 / Tier 2 / Tier 3 / Semua |
| Marital Status | Single / Married / Divorced / Semua |
| Tenure Min/Max | Input angka |

#### 4 Summary Card

| Card | ID | Isi |
|---|---|---|
| Total Pelanggan | `metricTotal` | Jumlah seluruh pelanggan yang diprediksi |
| Total Churn | `metricChurn` | Jumlah pelanggan yang diprediksi churn |
| Churn Rate | `metricChurnRate` | Persentase churn dari total |
| High Risk | `metricHighRisk` | Jumlah pelanggan dengan probabilitas ≥ 70% |

#### 6 Visualisasi Chart

| Chart | Tipe | ID Canvas |
|---|---|---|
| Distribusi Churn | Donut | `chartDonut` |
| Distribusi Probabilitas | Histogram | `chartProbDist` |
| Churn by Tenure Group | Stacked Bar | `chartTenure` |
| Churn by Kategori Produk | Horizontal Bar | `chartCategory` |
| Churn by Marital Status | Grouped Bar | `chartMarital` |
| Churn by Payment Mode | Bar | `chartPayment` |

---

### Halaman 2 — Predict (`/predict`)

**Tab Upload CSV:**
- Drop zone untuk upload file `.csv`
- Tombol download template CSV
- Tabel preview 10 baris pertama + 4 quick stat card
- Tombol Lihat Semua → pindah ke halaman Result

**Tab Input Manual:**
- Form 18 kolom lengkap
- Panel hasil real-time: gauge chart + risk badge + insight teks
- Tombol "Isi Contoh" untuk data demo

---

### Halaman 3 — Results (`/result`)

- 4 metric card (Total, Churn, Rate, High Risk)
- 2 chart (donut distribusi + bar risk level)
- Tabel sortable (klik header # / Tenure / Probabilitas)
- Pencarian teks di semua kolom
- Filter by risk level dan churn label
- Pagination 20 baris per halaman
- Tombol download CSV

---

## 9. Panduan UI Designer

### File yang Boleh Diubah

#### ✅ `static/css/dashboard.css` — Bebas diubah sepenuhnya

CSS variables berikut **wajib tetap ada** di `:root {}` karena dipakai JavaScript:
```css
:root {
  --sidebar-w: 224px;
  --navbar-h: 56px;
  --high: ...;
  --medium: ...;
  --low: ...;
}
```

Class berikut harus tetap ada (boleh diubah tampilannya):
- `.risk-badge.High`, `.risk-badge.Medium`, `.risk-badge.Low`
- `.label-badge.churn`, `.label-badge.no-churn`
- `.prob-bar-wrapper`, `.prob-bar-bg`, `.prob-bar-fill`, `.prob-value`
- `.page-btn`, `.page-btn.active`
- `.toast`, `.toast.success`, `.toast.error`, `.toast.info`
- `.loading-overlay`, `.spinner`

#### ✅ Template HTML — Boleh diubah dengan batasan

| File | Boleh | Jangan |
|---|---|---|
| `base.html` | Tampilan sidebar, warna, ikon, logo | Ubah href link navigasi |
| `dashboard.html` | Tampilan card, layout | Ubah `id="..."` di komentar TODO |
| `predict.html` | Tampilan form, tab, tombol | Ubah `name="..."` dan `id="..."` pada input |
| `result.html` | Tampilan tabel, card | Hapus tag `{% block scripts %}` |

### File yang TIDAK Boleh Diubah

| File | Alasan |
|---|---|
| `static/js/charts.js` | Logika fetch data dan render chart |
| `static/js/upload.js` | Logika upload CSV dan kirim ke API |
| `static/js/manual.js` | Logika form prediksi manual dan gauge chart |
| Semua file di `app/` | Backend — API, logika bisnis, koneksi data |

---

### Referensi ID Penting (Jangan Dihapus dari HTML)

**Dashboard:**

| ID | Fungsi |
|---|---|
| `metricTotal` | Angka total pelanggan |
| `metricChurn` | Angka total churn |
| `metricChurnRate` | Persentase churn rate |
| `metricHighRisk` | Jumlah high risk |
| `filterGender` | Dropdown filter gender |
| `filterCityTier` | Dropdown filter kota |
| `filterMarital` | Dropdown filter status |
| `filterTenureMin` | Input tenure minimum |
| `filterTenureMax` | Input tenure maximum |
| `emptyState` | Container empty state |
| `chartSection` | Container semua chart |
| `chartDonut` | Canvas chart donut |
| `chartProbDist` | Canvas chart histogram |
| `chartTenure` | Canvas chart tenure |
| `chartCategory` | Canvas chart kategori |
| `chartMarital` | Canvas chart marital |
| `chartPayment` | Canvas chart payment |

**Predict:**

| ID | Fungsi |
|---|---|
| `uploadZone` | Area drag-drop |
| `csvFile` | Input file hidden |
| `btnPredict` | Tombol jalankan prediksi |
| `csvResultSection` | Container hasil CSV |
| `manualForm` | Form prediksi manual |
| `manualResultCard` | Container hasil manual |
| `gaugeChart` | Canvas gauge chart |

**Results:**

| ID | Fungsi |
|---|---|
| `resultBody` | Tbody tabel diisi JS |
| `pagination` | Container pagination |
| `searchInput` | Input pencarian |
| `riskFilter` | Dropdown filter risk |
| `churnFilter` | Dropdown filter label |
| `btnDownloadResult` | Tombol download |

---

### Tips untuk Designer

**Test tampilan:**
1. Jalankan server: `uvicorn app.main:app --reload`
2. Edit file CSS atau HTML → simpan → refresh browser

**Isi data chart untuk test:**
1. Buka `/predict` → tab Upload CSV → Download Template
2. Upload file template → Jalankan Prediksi
3. Buka `/` — chart sudah ada datanya

**Kalau ada error / layar putih:**
- Buka DevTools browser (klik kanan → Inspect → Console)
- Screenshot errornya dan kirim ke backend dev

---

## 10. Kontak & Pembagian Tugas

| Bagian | PIC |
|---|---|
| Backend, API, ML pipeline, deployment | Backend Dev |
| CSS, HTML visual, layout, responsiveness | UI Designer |

Pertanyaan cara kerja data atau API → Backend Dev.
Pertanyaan tampilan dan layout → UI Designer.
