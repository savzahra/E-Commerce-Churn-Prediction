"""
API Test Suite — E-Commerce Churn Prediction
=============================================
Run:  python test_api.py
      python test_api.py --url http://localhost:8000   # custom base URL
      python test_api.py --verbose                     # show full response bodies
"""

import sys
import io
import csv
import json
import time
import argparse
import textwrap
from dataclasses import dataclass, field
from typing import Any

try:
    import requests
except ImportError:
    print("Install requests first:  pip install requests")
    sys.exit(1)

# ─── Config ──────────────────────────────────────────────────────────────────

DEFAULT_URL = "http://localhost:8000"

SAMPLE_CUSTOMER = {
    "Tenure": 10,
    "PreferredLoginDevice": "Mobile Phone",
    "CityTier": 1,
    "WarehouseToHome": 15,
    "PreferredPaymentMode": "Debit Card",
    "Gender": "Male",
    "HourSpendOnApp": 3,
    "NumberOfDeviceRegistered": 3,
    "PreferedOrderCat": "Laptop & Accessory",
    "SatisfactionScore": 3,
    "MaritalStatus": "Single",
    "NumberOfAddress": 3,
    "Complain": 0,
    "OrderAmountHikeFromlastYear": 15,
    "CouponUsed": 2,
    "OrderCount": 3,
    "DaySinceLastOrder": 5,
    "CashbackAmount": 180,
}

HIGH_RISK_CUSTOMER = {
    "Tenure": 1,
    "PreferredLoginDevice": "Mobile Phone",
    "CityTier": 1,
    "WarehouseToHome": 30,
    "PreferredPaymentMode": "Credit Card",
    "Gender": "Female",
    "HourSpendOnApp": 1,
    "NumberOfDeviceRegistered": 2,
    "PreferedOrderCat": "Mobile Phone",
    "SatisfactionScore": 1,
    "MaritalStatus": "Single",
    "NumberOfAddress": 2,
    "Complain": 1,
    "OrderAmountHikeFromlastYear": 5,
    "CouponUsed": 0,
    "OrderCount": 1,
    "DaySinceLastOrder": 20,
    "CashbackAmount": 50,
}

CSV_COLUMNS = [
    "CustomerID", "Tenure", "PreferredLoginDevice", "CityTier", "WarehouseToHome",
    "PreferredPaymentMode", "Gender", "HourSpendOnApp", "NumberOfDeviceRegistered",
    "PreferedOrderCat", "SatisfactionScore", "MaritalStatus", "NumberOfAddress",
    "Complain", "OrderAmountHikeFromlastYear", "CouponUsed", "OrderCount",
    "DaySinceLastOrder", "CashbackAmount",
]

# ─── Output helpers ───────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"


def _c(text, color): return f"{color}{text}{RESET}"
def ok(msg):   return f"  {_c('✓', GREEN)}  {msg}"
def fail(msg): return f"  {_c('✗', RED)}  {msg}"
def skip(msg): return f"  {_c('○', YELLOW)}  {msg}"
def info(msg): return f"  {_c('→', CYAN)}  {DIM}{msg}{RESET}"


# ─── Test runner ──────────────────────────────────────────────────────────────

@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""
    elapsed: float = 0.0
    response: Any = field(default=None, repr=False)


class TestRunner:
    def __init__(self, base_url: str, verbose: bool = False):
        self.base  = base_url.rstrip("/")
        self.verbose = verbose
        self.results: list[TestResult] = []
        self.session_id: str = ""

    def _req(self, method, path, **kwargs):
        url = self.base + path
        t0  = time.perf_counter()
        r   = requests.request(method, url, timeout=30, **kwargs)
        elapsed = time.perf_counter() - t0
        return r, elapsed

    def run(self, name: str, fn):
        try:
            result = fn()
            result.name = name
            self.results.append(result)
            status = ok(name) if result.passed else fail(name)
            suffix = f"  {DIM}{result.elapsed*1000:.0f}ms{RESET}"
            print(status + suffix)
            if result.detail:
                print(f"      {DIM}{result.detail}{RESET}")
            if self.verbose and result.response is not None:
                try:
                    body = json.dumps(result.response, indent=2)
                    print(textwrap.indent(body[:600], "      "))
                except Exception:
                    pass
        except Exception as exc:
            r = TestResult(name=name, passed=False, detail=str(exc))
            self.results.append(r)
            print(fail(name))
            print(f"      {_c(str(exc), RED)}")

    def summary(self):
        passed = sum(1 for r in self.results if r.passed)
        total  = len(self.results)
        bar    = ("█" * passed) + ("░" * (total - passed))
        color  = GREEN if passed == total else (YELLOW if passed > 0 else RED)
        print()
        print(f"  {_c(bar, color)}  {_c(f'{passed}/{total} passed', BOLD)}")
        if passed < total:
            for r in self.results:
                if not r.passed:
                    print(f"    {_c('✗', RED)} {r.name}: {r.detail}")
        print()
        return passed == total


def _make_csv(rows: list[dict], extra_cols: dict | None = None) -> bytes:
    """Build CSV bytes. extra_cols adds additional columns to every row."""
    buf = io.StringIO()
    cols = CSV_COLUMNS.copy()
    if extra_cols:
        cols += list(extra_cols.keys())
    writer = csv.DictWriter(buf, fieldnames=cols)
    writer.writeheader()
    for row in rows:
        r = dict(row)
        if extra_cols:
            r.update(extra_cols)
        writer.writerow(r)
    return buf.getvalue().encode()


def _make_csv_snake(rows: list[dict]) -> bytes:
    """CSV with snake_case column names (flexible matching test)."""
    mapping = {
        "CustomerID": "customer_id",
        "Tenure": "tenure",
        "PreferredLoginDevice": "preferred_login_device",
        "CityTier": "city_tier",
        "WarehouseToHome": "warehouse_to_home",
        "PreferredPaymentMode": "preferred_payment_mode",
        "Gender": "gender",
        "HourSpendOnApp": "hour_spend_on_app",
        "NumberOfDeviceRegistered": "number_of_device_registered",
        "PreferedOrderCat": "prefered_order_cat",
        "SatisfactionScore": "satisfaction_score",
        "MaritalStatus": "marital_status",
        "NumberOfAddress": "number_of_address",
        "Complain": "complain",
        "OrderAmountHikeFromlastYear": "order_amount_hike_fromlast_year",
        "CouponUsed": "coupon_used",
        "OrderCount": "order_count",
        "DaySinceLastOrder": "day_since_last_order",
        "CashbackAmount": "cashback_amount",
    }
    buf = io.StringIO()
    snake_cols = [mapping[c] for c in CSV_COLUMNS]
    writer = csv.writer(buf)
    writer.writerow(snake_cols)
    for row in rows:
        writer.writerow([row.get(c, "") for c in CSV_COLUMNS])
    return buf.getvalue().encode()


# ─── Individual tests ─────────────────────────────────────────────────────────

def test_health(runner: TestRunner):
    def _():
        r, t = runner._req("GET", "/api/insight/summary")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        assert "total_customers" in data
        return TestResult("", True, f"total_customers={data['total_customers']}", t, data)
    runner.run("GET /api/insight/summary — server health", _)


def test_manual_predict(runner: TestRunner):
    def _():
        r, t = runner._req("POST", "/api/predict/manual", json=SAMPLE_CUSTOMER)
        assert r.status_code == 200, f"HTTP {r.status_code} — {r.text[:200]}"
        data = r.json()
        pred = data["prediction"]
        assert pred["churn_label"] in (0, 1), "churn_label must be 0 or 1"
        assert 0.0 <= pred["churn_probability"] <= 1.0, "probability out of range"
        assert pred["risk_level"] in ("Low", "Medium", "High")
        return TestResult("", True,
            f"label={pred['churn_label']} prob={pred['churn_probability']:.4f} risk={pred['risk_level']}",
            t, pred)
    runner.run("POST /api/predict/manual — single prediction", _)


def test_manual_predict_high_risk(runner: TestRunner):
    def _():
        r, t = runner._req("POST", "/api/predict/manual", json=HIGH_RISK_CUSTOMER)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        pred = r.json()["prediction"]
        detail = f"prob={pred['churn_probability']:.4f} risk={pred['risk_level']}"
        return TestResult("", True, detail, t, pred)
    runner.run("POST /api/predict/manual — high-risk profile", _)


def test_csv_batch(runner: TestRunner):
    def _():
        rows = [
            {"CustomerID": "C001", **SAMPLE_CUSTOMER},
            {"CustomerID": "C002", **HIGH_RISK_CUSTOMER},
            {"CustomerID": "C003", **{**SAMPLE_CUSTOMER, "Tenure": 30, "Complain": 0, "SatisfactionScore": 5}},
        ]
        csv_bytes = _make_csv(rows)
        r, t = runner._req("POST", "/api/predict/csv",
                           files={"file": ("test.csv", csv_bytes, "text/csv")})
        assert r.status_code == 200, f"HTTP {r.status_code} — {r.text[:300]}"
        data = r.json()
        assert data["total"] == 3
        assert len(data["results"]) == 3
        runner.session_id = data["session_id"]
        first = data["results"][0]
        assert first.get("CustomerID") == "C001", f"CustomerID mismatch: {first.get('CustomerID')}"
        assert first["churn_label"] in (0, 1)
        return TestResult("", True,
            f"session={data['session_id'][:8]}… total={data['total']} | C001 risk={data['results'][0]['risk_level']}",
            t, None)
    runner.run("POST /api/predict/csv — batch 3 rows + CustomerID", _)


def test_csv_flexible_columns(runner: TestRunner):
    def _():
        rows = [{"CustomerID": "FLEX01", **SAMPLE_CUSTOMER}]
        csv_bytes = _make_csv_snake(rows)
        r, t = runner._req("POST", "/api/predict/csv",
                           files={"file": ("snake.csv", csv_bytes, "text/csv")})
        assert r.status_code == 200, f"HTTP {r.status_code} — {r.text[:300]}"
        data = r.json()
        assert data["total"] == 1
        cid = data["results"][0].get("CustomerID")
        assert cid == "FLEX01", f"CustomerID not matched: got {cid}"
        return TestResult("", True, f"snake_case columns matched OK | CustomerID={cid}", t, None)
    runner.run("POST /api/predict/csv — flexible snake_case columns", _)


def test_csv_extra_columns(runner: TestRunner):
    def _():
        rows = [{"CustomerID": "E001", **SAMPLE_CUSTOMER}]
        extra = {"irrelevant_col": "foo", "another_extra": 999, "score_v2": 0.5}
        csv_bytes = _make_csv(rows, extra_cols=extra)
        r, t = runner._req("POST", "/api/predict/csv",
                           files={"file": ("extra.csv", csv_bytes, "text/csv")})
        assert r.status_code == 200, f"HTTP {r.status_code} — {r.text[:200]}"
        data = r.json()
        assert data["total"] == 1
        return TestResult("", True, "extra columns ignored correctly", t, None)
    runner.run("POST /api/predict/csv — extra columns ignored", _)


def test_csv_missing_columns(runner: TestRunner):
    def _():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["CustomerID", "Tenure", "CityTier"])   # only 3 cols
        writer.writerow(["C001", 10, 1])
        csv_bytes = buf.getvalue().encode()
        r, t = runner._req("POST", "/api/predict/csv",
                           files={"file": ("missing.csv", csv_bytes, "text/csv")})
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
        detail = r.json().get("detail", {})
        assert isinstance(detail, dict), "detail should be structured object"
        assert "missing" in detail, "detail should list missing columns"
        assert len(detail["missing"]) > 0
        return TestResult("", True,
            f"correctly rejected — {len(detail['missing'])} missing cols reported", t, None)
    runner.run("POST /api/predict/csv — missing columns → 400 error", _)


def test_get_batch_result(runner: TestRunner):
    def _():
        if not runner.session_id:
            return TestResult("", False, "no session_id from batch test", 0)
        r, t = runner._req("GET", f"/api/predict/result/{runner.session_id}")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        assert "results" in data
        assert len(data["results"]) == 3
        return TestResult("", True, f"fetched {len(data['results'])} rows from server", t, None)
    runner.run("GET /api/predict/result/{id} — fetch batch result", _)


def test_download_csv(runner: TestRunner):
    def _():
        if not runner.session_id:
            return TestResult("", False, "no session_id", 0)
        r, t = runner._req("GET", f"/api/predict/download/{runner.session_id}")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        assert "text/csv" in r.headers.get("content-type", "")
        lines = r.text.strip().splitlines()
        assert len(lines) >= 4, f"Expected header + 3 data rows, got {len(lines)} lines"
        assert "CustomerID" in lines[0], "CustomerID should be first column"
        return TestResult("", True,
            f"{len(lines)-1} data rows, columns: {lines[0][:60]}…", t, None)
    runner.run("GET /api/predict/download/{id} — CSV download", _)


def test_template_download(runner: TestRunner):
    def _():
        r, t = runner._req("GET", "/api/predict/template")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        assert "text/csv" in r.headers.get("content-type", "")
        lines = r.text.strip().splitlines()
        header = lines[0].split(",")
        assert "CustomerID" in header, "Template missing CustomerID"
        assert "Tenure" in header, "Template missing Tenure"
        assert len(header) == 19, f"Expected 19 columns (1 ID + 18 features), got {len(header)}"
        return TestResult("", True, f"{len(header)} columns, {len(lines)-1} example rows", t, None)
    runner.run("GET /api/predict/template — template CSV", _)


def test_summary_no_filter(runner: TestRunner):
    def _():
        r, t = runner._req("GET", "/api/insight/summary")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        keys = {"total_customers", "total_churn", "churn_rate", "high_risk_count",
                "medium_risk_count", "low_risk_count"}
        missing_keys = keys - set(data.keys())
        assert not missing_keys, f"Missing keys: {missing_keys}"
        assert data["total_customers"] > 0, "Store should have predictions by now"
        return TestResult("", True,
            f"total={data['total_customers']} churn={data['total_churn']} rate={data['churn_rate']}%",
            t, data)
    runner.run("GET /api/insight/summary — aggregated stats", _)


def test_summary_with_filter(runner: TestRunner):
    def _():
        r_all,  _ = runner._req("GET", "/api/insight/summary")
        r_male, t = runner._req("GET", "/api/insight/summary?gender=Male")
        assert r_male.status_code == 200, f"HTTP {r_male.status_code}"
        all_data  = r_all.json()
        male_data = r_male.json()
        assert male_data["total_customers"] <= all_data["total_customers"], \
            "Filtered count should be ≤ total"
        return TestResult("", True,
            f"all={all_data['total_customers']} | gender=Male: {male_data['total_customers']}",
            t, male_data)
    runner.run("GET /api/insight/summary?gender=Male — filter reduces count", _)


def test_charts(runner: TestRunner):
    def _():
        r, t = runner._req("GET", "/api/insight/charts")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        expected_keys = {"churn_distribution", "churn_by_tenure", "churn_by_category",
                         "churn_by_marital", "prob_distribution", "churn_by_payment"}
        missing_keys = expected_keys - set(data.keys())
        assert not missing_keys, f"Missing chart keys: {missing_keys}"
        donut = data["churn_distribution"]
        assert len(donut["labels"]) == 2
        assert len(donut["values"]) == 2
        return TestResult("", True,
            f"churn={donut['values'][0]} non-churn={donut['values'][1]}", t, None)
    runner.run("GET /api/insight/charts — all 6 chart datasets", _)


def test_charts_with_filter(runner: TestRunner):
    def _():
        r, t = runner._req("GET", "/api/insight/charts?marital_status=Single&city_tier=1")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        return TestResult("", True, "marital_status=Single & city_tier=1 filter applied", t, None)
    runner.run("GET /api/insight/charts — combined filter", _)


def test_invalid_session(runner: TestRunner):
    def _():
        r, t = runner._req("GET", "/api/predict/result/nonexistent-session-id")
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        return TestResult("", True, "correctly returns 404 for unknown session", t, None)
    runner.run("GET /api/predict/result/invalid — 404 for unknown session", _)


def test_pages_render(runner: TestRunner):
    def _():
        pages = ["/", "/predict", "/result"]
        for path in pages:
            r, _ = runner._req("GET", path)
            assert r.status_code == 200, f"{path} returned {r.status_code}"
            assert "<!DOCTYPE html>" in r.text[:200].upper() or "<!doctype html>" in r.text[:200].lower(), \
                f"{path} did not return HTML"
        return TestResult("", True, f"all {len(pages)} pages rendered OK", 0)
    runner.run("GET / /predict /result — HTML pages render", _)


def test_swagger_docs(runner: TestRunner):
    def _():
        r, t = runner._req("GET", "/docs")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        return TestResult("", True, "Swagger UI accessible", t, None)
    runner.run("GET /docs — Swagger UI", _)


def test_reset_data(runner: TestRunner):
    def _():
        r, t = runner._req("DELETE", "/api/insight/clear")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        # Confirm store is actually empty
        r2, _ = runner._req("GET", "/api/insight/summary")
        assert r2.json()["total_customers"] == 0, "Store should be empty after reset"
        return TestResult("", True, "store cleared, summary returns 0", t, None)
    runner.run("DELETE /api/insight/clear — reset all data", _)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="API test suite for ChurnAI")
    parser.add_argument("--url",     default=DEFAULT_URL, help="Base URL of the server")
    parser.add_argument("--verbose", action="store_true",  help="Print response bodies")
    args = parser.parse_args()

    print()
    print(f"  {_c('ChurnAI API Test Suite', BOLD)}")
    print(f"  {DIM}Target: {args.url}{RESET}")
    print(f"  {DIM}{'─' * 50}{RESET}")
    print()

    # Check server reachable
    try:
        requests.get(args.url + "/api/insight/summary", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"  {_c('Cannot connect to', RED)} {args.url}")
        print(f"  Start the server first:  {_c('python -m uvicorn app.main:app --port 8000', CYAN)}")
        sys.exit(1)

    runner = TestRunner(args.url, args.verbose)

    print(f"  {_c('── Infrastructure', DIM)}")
    test_health(runner)
    test_pages_render(runner)
    test_swagger_docs(runner)

    print(f"\n  {_c('── Prediction Endpoints', DIM)}")
    test_manual_predict(runner)
    test_manual_predict_high_risk(runner)
    test_csv_batch(runner)

    print(f"\n  {_c('── Column Matching', DIM)}")
    test_csv_flexible_columns(runner)
    test_csv_extra_columns(runner)
    test_csv_missing_columns(runner)

    print(f"\n  {_c('── Batch Result & Download', DIM)}")
    test_get_batch_result(runner)
    test_download_csv(runner)
    test_template_download(runner)

    print(f"\n  {_c('── Insight & Filter', DIM)}")
    test_summary_no_filter(runner)
    test_summary_with_filter(runner)
    test_charts(runner)
    test_charts_with_filter(runner)

    print(f"\n  {_c('── Edge Cases', DIM)}")
    test_invalid_session(runner)

    print(f"\n  {_c('── Cleanup', DIM)}")
    test_reset_data(runner)

    print(f"  {DIM}{'─' * 50}{RESET}")
    success = runner.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
