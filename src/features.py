# src/features.py
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

def prepare_X_y(df, target="price", top_k=50):
    """
    Prepares features (X), target (y), and a ColumnTransformer preprocessor.
    - Drops rows missing target.
    - Drops id-like categorical columns (userCode, travelCode, code, etc.)
    - Limits categories per categorical column to top_k (others -> "OTHER").
    - Returns X, y, preprocessor, num_cols, cat_cols.
    """
    # Drop rows where target is missing
    df = df.dropna(subset=[target])

    # Separate features & target
    X = df.drop(columns=[target])
    y = df[target].copy()

    # Detect categorical and numeric columns
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = X.select_dtypes(include=["int64", "float64", "float32", "int32"]).columns.tolist()

    # ✅ Drop ID-like columns (they don’t carry predictive info)
    drop_cols = [c for c in X.columns if any(k in c.lower() for k in ("id", "code"))]
    if drop_cols:
        print(f"[INFO] Dropping ID-like columns: {drop_cols}")
        X = X.drop(columns=drop_cols, errors="ignore")
        cat_cols = [c for c in cat_cols if c not in drop_cols]
        num_cols = [c for c in num_cols if c not in drop_cols]

    # Limit cardinality: replace rare categories with 'OTHER'
    for c in list(cat_cols):
        if c not in X.columns:
            continue
        top_values = X[c].value_counts().nlargest(top_k).index
        X[c] = X[c].where(X[c].isin(top_values), other="OTHER")

    # Numeric pipeline
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # Categorical pipeline
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols),
        ],
        remainder="drop",
        sparse_threshold=0.3
    )

    return X, y, preprocessor, num_cols, cat_cols