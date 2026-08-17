# E-Commerce-Churn-Prediction (Churn AI)
A machine learning model to predict customer churn in an e-commerce business. The project covers data preprocessing, EDA, feature engineering, model comparison, hyperparameter tuning, and performance evaluation to support customer retention strategies.

---

Aplikasi web prediksi churn pelanggan e-commerce berbasis machine learning. Dibangun sebagai proyek akhir bootcamp DigitalSkola.

**Model:** LightGBM — F1-Score 96.83% · ROC-AUC 99.96%

---

## Tech Stack

| Layer | Tools |
|---|---|
| Backend | FastAPI + Uvicorn |
| Frontend | HTML + Jinja2 + Vanilla JS |
| Charts | Chart.js 4.4.0 |
| ML | LightGBM + scikit-learn |
| Deployment | Vercel |

---

## Fitur

- **Prediksi Manual** — input 18 fitur satu pelanggan, output langsung dengan gauge chart
- **Prediksi Batch** — upload CSV ratusan pelanggan sekaligus, download hasil
- **Dashboard Insight** — 6 visualisasi interaktif dengan filter gender, city tier, marital status, tenure
- **Risk Level** — setiap prediksi dikategorikan Low / Medium / High Risk

---

## Cara Menjalankan

### 1. Clone Repository

```bash
git clone <repo-url>
cd DigitalSkola-ECommerce
```

### 2. Buat Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Pastikan File Model Ada

Struktur folder `model/` harus berisi:

```
model/
├── model_lightgbm.pkl
└── preprocessor.pkl
```

> Jika file model belum ada, jalankan notebook training terlebih dahulu atau minta file `.pkl` dari anggota tim.

### 5. Jalankan Server

```bash
uvicorn app.main:app --reload
```

Server berjalan di `http://localhost:8000`.

### 6. Akses Aplikasi

| URL | Halaman |
|---|---|
| `http://localhost:8000` | Dashboard insight |
| `http://localhost:8000/predict` | Halaman prediksi |
| `http://localhost:8000/result` | Hasil prediksi batch |
| `http://localhost:8000/docs` | Swagger API docs |

---

## Menjalankan Tests

Pastikan server **sudah berjalan** sebelum menjalankan test.

```bash
python test_api.py
```

Ekspektasi output: **18/18 passed**.

---

## Cara Pakai

### Prediksi Batch (CSV)

1. Buka `/predict` → tab **Upload CSV**
2. Download template CSV via tombol **Download Template**
3. Isi data pelanggan di template, simpan sebagai `.csv`
4. Upload file → klik **Jalankan Prediksi**
5. Lihat preview hasil, atau klik **Lihat Semua** untuk tabel lengkap
6. Download hasil via tombol **Download CSV**

### Prediksi Manual

1. Buka `/predict` → tab **Input Manual**
2. Isi 18 kolom data pelanggan (atau klik **Isi Contoh** untuk demo)
3. Klik **Prediksi** → hasil muncul di panel kanan

---

## Struktur Proyek

```
DigitalSkola-ECommerce/
├── app/
│   ├── main.py                  ← FastAPI entry point
│   ├── routers/
│   │   ├── predict.py           ← Endpoint prediksi
│   │   └── insight.py           ← Endpoint dashboard
│   ├── services/
│   │   ├── pipeline.py          ← Inference pipeline ML
│   │   └── insight_service.py   ← Analitik in-memory
│   └── schemas/
│       └── customer.py          ← Pydantic models
├── model/
│   ├── model_lightgbm.pkl       ← Model terlatih
│   └── preprocessor.pkl         ← ColumnTransformer
├── static/
│   ├── css/dashboard.css
│   └── js/
│       ├── charts.js
│       ├── upload.js
│       └── manual.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── predict.html
│   └── result.html
├── test_api.py
├── requirements.txt
└── vercel.json
```

Dokumentasi lengkap per file → lihat [overview.md](overview.md).

---

## Kolom Input Model

18 fitur yang digunakan untuk prediksi:

| Fitur | Tipe |
|---|---|
| Tenure | Numerik (bulan) |
| CityTier | Numerik (1/2/3) |
| WarehouseToHome | Numerik (km) |
| HourSpendOnApp | Numerik |
| NumberOfDeviceRegistered | Numerik |
| SatisfactionScore | Numerik (1–5) |
| NumberOfAddress | Numerik |
| Complain | Numerik (0/1) |
| OrderAmountHikeFromlastYear | Numerik (%) |
| CouponUsed | Numerik |
| OrderCount | Numerik |
| DaySinceLastOrder | Numerik |
| CashbackAmount | Numerik |
| PreferredLoginDevice | Kategorikal |
| PreferredPaymentMode | Kategorikal |
| Gender | Kategorikal |
| PreferedOrderCat | Kategorikal |
| MaritalStatus | Kategorikal |

---

## Tim

Proyek akhir bootcamp DigitalSkola — dikerjakan bersama:

- **ML Modeling & Evaluation** — Savitri Rizquna
- **Backend & ML Pipeline** — Rekan Tim
- **UI Design & Frontend** — Rekan Tim
