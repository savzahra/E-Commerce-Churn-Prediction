import io
import csv
import re
import uuid

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.customer import CustomerInput
from app.services import pipeline, insight_service

router = APIRouter(prefix="/api/predict", tags=["predict"])

_batch_results: dict[str, list[dict]] = {}

INPUT_COLUMNS = [
    "Tenure", "PreferredLoginDevice", "CityTier", "WarehouseToHome",
    "PreferredPaymentMode", "Gender", "HourSpendOnApp", "NumberOfDeviceRegistered",
    "PreferedOrderCat", "SatisfactionScore", "MaritalStatus", "NumberOfAddress",
    "Complain", "OrderAmountHikeFromlastYear", "CouponUsed", "OrderCount",
    "DaySinceLastOrder", "CashbackAmount",
]


def _normalize(name: str) -> str:
    """Lowercase + strip spaces, underscores, hyphens for fuzzy column matching."""
    return re.sub(r'[\s_\-]', '', name.strip().lower())


def _match_columns(df_cols: list[str], required: list[str]) -> tuple[dict[str, str], list[str]]:
    """
    Try to match each required column against df_cols using normalized names.
    Returns (rename_map, missing_required).
    rename_map: {original_df_col -> required_col_name}
    """
    norm_to_orig = {_normalize(c): c for c in df_cols}
    rename_map: dict[str, str] = {}
    missing: list[str] = []

    for req in required:
        if req in df_cols:                          # exact match — highest priority
            rename_map[req] = req
        elif _normalize(req) in norm_to_orig:       # normalized match
            rename_map[norm_to_orig[_normalize(req)]] = req
        else:
            missing.append(req)

    return rename_map, missing


@router.post("/manual", summary="Prediksi single customer (input manual)")
async def predict_manual(customer: CustomerInput):
    try:
        result = pipeline.predict_single(customer.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    record = customer.model_dump()
    record.update(result)
    insight_service.add_predictions([record])

    return {
        "input": customer.model_dump(),
        "prediction": result,
    }


@router.post("/csv", summary="Prediksi batch dari CSV upload")
async def predict_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File harus berformat CSV")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca CSV: {str(e)}")

    # Flexible column matching — CSV may have extra columns; all 18 required must exist
    rename_map, missing_cols = _match_columns(list(df.columns), INPUT_COLUMNS)
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Kolom wajib tidak ditemukan dalam file CSV.",
                "missing": missing_cols,
                "hint": "Pastikan 18 kolom template tersedia. Kolom ekstra akan diabaikan.",
            }
        )

    # Rename matched columns to canonical names, keep extras silently
    df = df.rename(columns=rename_map)

    # Also try to match CustomerID with the same normalizer (it's pass-through, not in INPUT_COLUMNS)
    if "CustomerID" not in df.columns:
        norm_map = {_normalize(c): c for c in df.columns}
        if _normalize("CustomerID") in norm_map:
            df = df.rename(columns={norm_map[_normalize("CustomerID")]: "CustomerID"})

    has_customer_id = "CustomerID" in df.columns
    customer_ids = df["CustomerID"].tolist() if has_customer_id else [None] * len(df)

    try:
        predictions = pipeline.predict_batch(df[INPUT_COLUMNS])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    records = []
    for i, (pred, row, cid) in enumerate(zip(predictions, df[INPUT_COLUMNS].to_dict("records"), customer_ids)):
        record = {"row_index": i + 1}
        if cid is not None:
            record["CustomerID"] = cid
        record.update(row)
        record.update(pred)
        records.append(record)

    insight_service.add_predictions([{**r} for r in records])

    session_id = str(uuid.uuid4())
    _batch_results[session_id] = records

    return {"session_id": session_id, "total": len(records), "results": records}


@router.get("/result/{session_id}", summary="Ambil hasil batch prediksi")
async def get_batch_result(session_id: str):
    if session_id not in _batch_results:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")
    return {"results": _batch_results[session_id]}


@router.get("/download/{session_id}", summary="Download hasil prediksi sebagai CSV")
async def download_result(session_id: str):
    if session_id not in _batch_results:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")

    records = _batch_results[session_id]
    output = io.StringIO()
    if records:
        writer = csv.DictWriter(output, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=churn_predictions_{session_id[:8]}.csv"},
    )


@router.get("/template", summary="Download template CSV")
async def download_template():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["CustomerID"] + INPUT_COLUMNS)
    writer.writerow([
        "C001", 10, "Mobile Phone", 1, 15, "Debit Card", "Male", 3, 3,
        "Laptop & Accessory", 3, "Single", 3, 0, 15, 2, 3, 5, 180,
    ])
    writer.writerow([
        "C002", 2, "Computer", 3, 30, "Credit Card", "Female", 2, 2,
        "Mobile Phone", 2, "Married", 2, 1, 10, 1, 2, 10, 150,
    ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=template_churn.csv"},
    )
