import pandas as pd
import numpy as np

np.random.seed(42)

n = 1_000  # Ubah disini aja

df = pd.DataFrame({
    "CustomerID": [f"C{i:06d}" for i in range(1, n + 1)],
    
    "Tenure": np.random.randint(1, 61, n),

    "PreferredLoginDevice": np.random.choice(
        ["Mobile Phone", "Computer", "Tablet"],
        n,
        p=[0.7, 0.25, 0.05]
    ),

    "CityTier": np.random.choice([1, 2, 3], n, p=[0.4, 0.35, 0.25]),

    "WarehouseToHome": np.random.randint(5, 51, n),

    "PreferredPaymentMode": np.random.choice(
        ["Debit Card", "Credit Card", "UPI", "Cash on Delivery", "E wallet"],
        n
    ),

    "Gender": np.random.choice(["Male", "Female"], n),

    "HourSpendOnApp": np.random.randint(1, 6, n),

    "NumberOfDeviceRegistered": np.random.randint(1, 7, n),

    "PreferedOrderCat": np.random.choice(
        [
            "Laptop & Accessory",
            "Mobile Phone",
            "Fashion",
            "Grocery",
            "Others"
        ],
        n
    ),

    "SatisfactionScore": np.random.randint(1, 6, n),

    "MaritalStatus": np.random.choice(
        ["Single", "Married", "Divorced"],
        n,
        p=[0.45, 0.45, 0.10]
    ),

    "NumberOfAddress": np.random.randint(1, 8, n),

    "Complain": np.random.choice([0, 1], n, p=[0.8, 0.2]),

    "OrderAmountHikeFromlastYear": np.random.randint(0, 31, n),

    "CouponUsed": np.random.randint(0, 11, n),

    "OrderCount": np.random.randint(1, 16, n),

    "DaySinceLastOrder": np.random.randint(0, 31, n),

    "CashbackAmount": np.random.randint(50, 501, n)
})

# Simpan ke CSV
df.to_csv("churn_1k.csv", index=False)

print(df.shape)
print(df.head())