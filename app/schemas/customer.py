from pydantic import BaseModel, Field
from typing import Optional


class CustomerInput(BaseModel):
    Tenure: float = Field(..., ge=0, description="Lama bergabung (bulan)")
    PreferredLoginDevice: str = Field(..., description="Mobile Phone / Computer")
    CityTier: int = Field(..., ge=1, le=3, description="Tingkatan kota 1-3")
    WarehouseToHome: float = Field(..., ge=0, description="Jarak gudang ke rumah (km)")
    PreferredPaymentMode: str = Field(..., description="Debit Card / Credit Card / UPI / E wallet / Cash on Delivery")
    Gender: str = Field(..., description="Male / Female")
    HourSpendOnApp: float = Field(..., ge=0, description="Jam penggunaan aplikasi per hari")
    NumberOfDeviceRegistered: int = Field(..., ge=1, description="Jumlah perangkat terdaftar")
    PreferedOrderCat: str = Field(..., description="Laptop & Accessory / Mobile Phone / Fashion / Grocery / Others")
    SatisfactionScore: int = Field(..., ge=1, le=5, description="Skor kepuasan 1-5")
    MaritalStatus: str = Field(..., description="Single / Married / Divorced")
    NumberOfAddress: int = Field(..., ge=1, description="Jumlah alamat tersimpan")
    Complain: int = Field(..., ge=0, le=1, description="Pernah komplain (0/1)")
    OrderAmountHikeFromlastYear: float = Field(..., ge=0, description="% kenaikan order dari tahun lalu")
    CouponUsed: float = Field(..., ge=0, description="Jumlah kupon digunakan")
    OrderCount: float = Field(..., ge=0, description="Jumlah order bulan lalu")
    DaySinceLastOrder: float = Field(..., ge=0, description="Hari sejak order terakhir")
    CashbackAmount: float = Field(..., ge=0, description="Rata-rata cashback (Rp)")

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class PredictionResult(BaseModel):
    churn_label: int
    churn_probability: float
    risk_level: str


class CustomerPrediction(BaseModel):
    input: CustomerInput
    prediction: PredictionResult


class BatchPredictionItem(BaseModel):
    row_index: int
    Tenure: Optional[float] = None
    Gender: Optional[str] = None
    MaritalStatus: Optional[str] = None
    CityTier: Optional[int] = None
    churn_label: int
    churn_probability: float
    risk_level: str
