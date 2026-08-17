from collections import defaultdict
from typing import Any

# In-memory store: list of prediction records
# Each record: dict with all input fields + churn_label, churn_probability, risk_level
_prediction_store: list[dict] = []


def add_predictions(records: list[dict]) -> None:
    _prediction_store.extend(records)


def clear_store() -> None:
    _prediction_store.clear()


def get_all_predictions() -> list[dict]:
    return list(_prediction_store)


def get_summary(gender=None, city_tier=None, marital_status=None,
                tenure_min=None, tenure_max=None) -> dict:
    records = _filtered(gender, city_tier, marital_status, tenure_min, tenure_max)

    if not records:
        return {
            "total_customers": 0,
            "total_churn": 0,
            "churn_rate": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
        }

    total = len(records)
    total_churn = sum(1 for r in records if r["churn_label"] == 1)
    high_risk   = sum(1 for r in records if r["risk_level"] == "High")
    medium_risk = sum(1 for r in records if r["risk_level"] == "Medium")
    low_risk    = sum(1 for r in records if r["risk_level"] == "Low")

    return {
        "total_customers": total,
        "total_churn": total_churn,
        "churn_rate": round(total_churn / total * 100, 2) if total else 0.0,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
    }


def _filtered(gender=None, city_tier=None, marital_status=None,
              tenure_min=None, tenure_max=None) -> list[dict]:
    result = _prediction_store
    if gender:
        result = [r for r in result if str(r.get("Gender", "")).lower() == gender.lower()]
    if city_tier:
        result = [r for r in result if str(r.get("CityTier", "")) == str(city_tier)]
    if marital_status:
        result = [r for r in result if str(r.get("MaritalStatus", "")).lower() == marital_status.lower()]
    if tenure_min is not None:
        result = [r for r in result if float(r.get("Tenure", 0)) >= tenure_min]
    if tenure_max is not None:
        result = [r for r in result if float(r.get("Tenure", 0)) <= tenure_max]
    return result


def get_chart_data(gender=None, city_tier=None, marital_status=None,
                   tenure_min=None, tenure_max=None) -> dict[str, Any]:
    records = _filtered(gender, city_tier, marital_status, tenure_min, tenure_max)

    if not records:
        return _empty_chart_data()

    # 1. Donut: Churn distribution
    churn_count = sum(1 for r in records if r["churn_label"] == 1)
    non_churn_count = len(records) - churn_count
    churn_distribution = {"labels": ["Churn", "Non-Churn"], "values": [churn_count, non_churn_count]}

    # 2. Bar: Churn by tenure group
    tenure_buckets = {"0-6 bulan": [0, 0], "7-12 bulan": [0, 0], "13-24 bulan": [0, 0], "24+ bulan": [0, 0]}
    for r in records:
        t = float(r.get("Tenure", 0))
        if t <= 6:
            key = "0-6 bulan"
        elif t <= 12:
            key = "7-12 bulan"
        elif t <= 24:
            key = "13-24 bulan"
        else:
            key = "24+ bulan"
        tenure_buckets[key][1] += 1
        if r["churn_label"] == 1:
            tenure_buckets[key][0] += 1
    churn_by_tenure = {
        "labels": list(tenure_buckets.keys()),
        "churn": [v[0] for v in tenure_buckets.values()],
        "total": [v[1] for v in tenure_buckets.values()],
    }

    # 3. Bar: Churn by product category
    cat_counts: dict[str, list] = defaultdict(lambda: [0, 0])
    for r in records:
        cat = r.get("PreferedOrderCat", "Unknown")
        cat_counts[cat][1] += 1
        if r["churn_label"] == 1:
            cat_counts[cat][0] += 1
    churn_by_category = {
        "labels": list(cat_counts.keys()),
        "churn": [v[0] for v in cat_counts.values()],
        "total": [v[1] for v in cat_counts.values()],
    }

    # 4. Bar: Churn by marital status
    marital_counts: dict[str, list] = defaultdict(lambda: [0, 0])
    for r in records:
        ms = r.get("MaritalStatus", "Unknown")
        marital_counts[ms][1] += 1
        if r["churn_label"] == 1:
            marital_counts[ms][0] += 1
    churn_by_marital = {
        "labels": list(marital_counts.keys()),
        "churn": [v[0] for v in marital_counts.values()],
        "total": [v[1] for v in marital_counts.values()],
    }

    # 5. Histogram: Probability distribution (10 buckets 0-1)
    buckets = [0] * 10
    for r in records:
        idx = min(int(r["churn_probability"] * 10), 9)
        buckets[idx] += 1
    prob_labels = [f"{i/10:.1f}-{(i+1)/10:.1f}" for i in range(10)]
    prob_distribution = {"labels": prob_labels, "values": buckets}

    # 6. Bar: Churn by payment mode
    payment_counts: dict[str, list] = defaultdict(lambda: [0, 0])
    for r in records:
        pm = r.get("PreferredPaymentMode", "Unknown")
        payment_counts[pm][1] += 1
        if r["churn_label"] == 1:
            payment_counts[pm][0] += 1
    churn_by_payment = {
        "labels": list(payment_counts.keys()),
        "churn": [v[0] for v in payment_counts.values()],
        "total": [v[1] for v in payment_counts.values()],
    }

    return {
        "churn_distribution": churn_distribution,
        "churn_by_tenure": churn_by_tenure,
        "churn_by_category": churn_by_category,
        "churn_by_marital": churn_by_marital,
        "prob_distribution": prob_distribution,
        "churn_by_payment": churn_by_payment,
    }


def _empty_chart_data() -> dict:
    return {
        "churn_distribution": {"labels": ["Churn", "Non-Churn"], "values": [0, 0]},
        "churn_by_tenure": {"labels": ["0-6 bulan", "7-12 bulan", "13-24 bulan", "24+ bulan"], "churn": [0, 0, 0, 0], "total": [0, 0, 0, 0]},
        "churn_by_category": {"labels": [], "churn": [], "total": []},
        "churn_by_marital": {"labels": [], "churn": [], "total": []},
        "prob_distribution": {"labels": [f"{i/10:.1f}-{(i+1)/10:.1f}" for i in range(10)], "values": [0] * 10},
        "churn_by_payment": {"labels": [], "churn": [], "total": []},
    }
