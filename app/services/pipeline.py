import pandas as pd
import joblib
from pathlib import Path

# Set to True  → load real model and run LightGBM inference
# Set to False → return mock output (untuk testing tanpa model)
MODEL_ENABLED = True

_MODELS_DIR = Path(__file__).parent.parent.parent / "model"

_preprocessor = None
_model = None

# Koreksi nilai kategorikal yang tidak konsisten dari data mentah
_LOGIN_DEVICE_MAP = {"Phone": "Mobile Phone"}
_PAYMENT_MAP = {"CC": "Credit Card", "COD": "Cash on Delivery"}
_ORDER_CAT_MAP = {"Mobile": "Mobile Phone"}

# Urutan kolom yang diharapkan ColumnTransformer
_NUMERICAL_COLS = [
    "Tenure", "CityTier", "WarehouseToHome", "HourSpendOnApp",
    "NumberOfDeviceRegistered", "SatisfactionScore", "NumberOfAddress",
    "Complain", "OrderAmountHikeFromlastYear", "CouponUsed",
    "OrderCount", "DaySinceLastOrder", "CashbackAmount",
]
_CATEGORICAL_COLS = [
    "PreferredLoginDevice", "PreferredPaymentMode", "Gender",
    "PreferedOrderCat", "MaritalStatus",
]
_ALL_COLS = _NUMERICAL_COLS + _CATEGORICAL_COLS


def load_models():
    if not MODEL_ENABLED:
        return
    global _preprocessor, _model
    _preprocessor = joblib.load(_MODELS_DIR / "preprocessor.pkl")
    _model = joblib.load(_MODELS_DIR / "model_lightgbm.pkl")


def _fix_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "PreferredLoginDevice" in df.columns:
        df["PreferredLoginDevice"] = df["PreferredLoginDevice"].replace(_LOGIN_DEVICE_MAP)
    if "PreferredPaymentMode" in df.columns:
        df["PreferredPaymentMode"] = df["PreferredPaymentMode"].replace(_PAYMENT_MAP)
    if "PreferedOrderCat" in df.columns:
        df["PreferedOrderCat"] = df["PreferedOrderCat"].replace(_ORDER_CAT_MAP)
    return df


def _get_risk_level(prob: float) -> str:
    if prob < 0.3:
        return "Low"
    elif prob < 0.7:
        return "Medium"
    return "High"


def run_pipeline(df: pd.DataFrame) -> list[dict]:
    """
    Pipeline inferensi: raw input → fix cats → preprocess → LightGBM predict.
    Input : raw DataFrame dengan 18 kolom fitur asli.
    Output: list dict { churn_label, churn_probability, risk_level }.
    """
    if not MODEL_ENABLED:
        return [
            {"churn_label": 0, "churn_probability": 0.0, "risk_level": "Low"}
            for _ in range(len(df))
        ]

    df = _fix_categoricals(df)
    df = df[_ALL_COLS]

    feature_names = _preprocessor.get_feature_names_out()
    X = pd.DataFrame(_preprocessor.transform(df), columns=feature_names)

    probas = _model.predict_proba(X)[:, 1]
    labels = _model.predict(X)

    return [
        {
            "churn_label": int(label),
            "churn_probability": round(float(prob), 4),
            "risk_level": _get_risk_level(float(prob)),
        }
        for label, prob in zip(labels, probas)
    ]


def predict_single(data: dict) -> dict:
    return run_pipeline(pd.DataFrame([data]))[0]


def predict_batch(df: pd.DataFrame) -> list[dict]:
    return run_pipeline(df)
