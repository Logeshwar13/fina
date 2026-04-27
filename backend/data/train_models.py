"""
data/train_models.py
────────────────────
Trains ALL ML models using REAL CSV data + synthetic augmentation.

Datasets used:
  1. data/creditcard.csv   → Fraud Detection (Isolation Forest)
     columns: Time, V1-V28, Amount, Class (0=legit, 1=fraud)
  2. data/myExpenses1.csv  → Categorizer (TF-IDF + Logistic Regression)
     columns: Date, Item, Amount, Category, Time, day
  + Faker synthetic data augments both datasets

Run:
    cd backend
    python data/train_models.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from faker import Faker
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score

DATA_DIR  = Path(__file__).parent
MODEL_DIR = Path(__file__).parent.parent / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

FRAUD_CSV   = DATA_DIR / "creditcard.csv"
EXPENSE_CSV = DATA_DIR / "myExpenses1.csv"

fake = Faker(); Faker.seed(0)

# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIZER  (TF-IDF + Logistic Regression)
# ─────────────────────────────────────────────────────────────────────────────

SYNTHETIC_TEMPLATES = {
    "Food & Dining":    ["lunch at {c}", "coffee {c}", "dinner {c}", "swiggy order", "zomato delivery",
                          "grocery {c}", "chai stall", "pizza delivery", "breakfast", "restaurant bill"],
    "Transportation":   ["uber ride", "ola cab", "metro card recharge", "fuel {c}", "bus ticket",
                          "auto fare", "parking fee", "cab {c}", "rapido ride", "toll tax"],
    "Shopping":         ["amazon {c}", "flipkart order", "clothes {c}", "shoes purchase", "mall {c}",
                          "myntra order", "electronics {c}", "home decor", "gadget {c}", "accessories"],
    "Entertainment":    ["netflix subscription", "spotify premium", "movie tickets", "concert {c}",
                          "gaming top-up", "hotstar plan", "bowling {c}", "theme park", "book {c}", "streaming"],
    "Healthcare":       ["pharmacy {c}", "doctor consultation", "lab test", "hospital bill", "medical checkup",
                          "dental checkup", "medicine purchase", "physiotherapy", "eye test", "surgery",
                          "heart operation", "cardiac surgery", "cancer treatment", "chemotherapy", "dialysis",
                          "mri scan", "ct scan", "x-ray", "blood test", "health checkup", "vaccination",
                          "emergency room", "ambulance", "hospital admission", "icu charges", "operation theatre",
                          "medical procedure", "diagnostic test", "pathology", "radiology", "consultation fee",
                          "specialist doctor", "cardiologist", "neurologist", "orthopedic", "pediatrician"],
    "Insurance":        ["health insurance premium", "life insurance premium", "term insurance", "medical insurance",
                          "car insurance", "vehicle insurance", "home insurance", "travel insurance policy",
                          "insurance renewal", "policy premium", "insurance payment", "coverage premium"],
    "Utilities":        ["electricity bill", "water bill", "internet recharge", "mobile recharge {c}",
                          "gas cylinder", "wifi bill", "broadband {c}", "dth recharge", "utility bill"],
    "Housing":          ["monthly rent", "house maintenance", "apartment deposit", "plumber {c}",
                          "electrician", "cleaning service", "painting", "repair work"],
    "Education":        ["course fee {c}", "textbook purchase", "online class", "tuition fee",
                          "library subscription", "udemy course", "certification exam", "stationery"],
    "Travel":           ["hotel {c}", "flight ticket", "airbnb stay", "travel insurance",
                          "holiday package", "visa fee", "luggage {c}", "train ticket", "vacation rental"],
    "Income":           ["salary credit", "freelance payment {c}", "transfer received", "bonus credit",
                          "dividend", "rental income", "refund received"],
}


def _generate_synthetic_expenses(n_per_class=300):
    rows = []
    for cat, templates in SYNTHETIC_TEMPLATES.items():
        for _ in range(n_per_class):
            tmpl = np.random.choice(templates)
            desc = tmpl.format(c=fake.company()) if "{c}" in tmpl else tmpl
            rows.append({"description": desc, "category": cat})
    return pd.DataFrame(rows)


def _load_expense_df():
    frames = []

    # Real CSV
    if EXPENSE_CSV.exists():
        df = pd.read_csv(EXPENSE_CSV)
        print(f"  Real expense CSV: {len(df)} rows, columns: {list(df.columns)}")
        # Try common column names
        desc_col = next((c for c in df.columns if c.lower() in ["item","description","name","desc","product"]), None)
        cat_col  = next((c for c in df.columns if c.lower() in ["category","cat","type","label"]), None)
        if desc_col and cat_col:
            real = df[[desc_col, cat_col]].copy()
            real.columns = ["description", "category"]
            real = real.dropna()
            real["description"] = real["description"].astype(str)
            real["category"]    = real["category"].astype(str)
            print(f"  Using columns: '{desc_col}' → description, '{cat_col}' → category")
            print(f"  Real categories: {sorted(real['category'].unique())}")
            frames.append(real)
        else:
            print(f"  Could not auto-detect description/category columns — using synthetic only")
    else:
        print(f"  myExpenses1.csv not found — using synthetic only")

    # Synthetic augmentation
    synth = _generate_synthetic_expenses(n_per_class=300)
    frames.append(synth)
    print(f"  Synthetic rows added: {len(synth)}")

    combined = pd.concat(frames, ignore_index=True).dropna()
    print(f"  Combined dataset: {len(combined)} rows, {combined['category'].nunique()} categories")
    return combined


def train_categorizer():
    print("\n══════════════════════════════════════════════")
    print("  CATEGORIZER  (TF-IDF + Logistic Regression)")
    print("══════════════════════════════════════════════")
    df = _load_expense_df()

    X_train, X_test, y_train, y_test = train_test_split(
        df["description"], df["category"],
        test_size=0.2, random_state=42, stratify=df["category"]
    )

    vec = TfidfVectorizer(
        ngram_range=(1, 2), max_features=8000,
        sublinear_tf=True, strip_accents="unicode",
        analyzer="word", token_pattern=r"\w{1,}"
    )
    X_tr = vec.fit_transform(X_train)
    X_te = vec.transform(X_test)

    clf = LogisticRegression(max_iter=1500, C=5.0, solver="lbfgs", multi_class="multinomial")
    clf.fit(X_tr, y_train)

    acc = accuracy_score(y_test, clf.predict(X_te))
    print(f"\n  Test Accuracy: {acc:.2%}")
    print(classification_report(y_test, clf.predict(X_te), zero_division=0))

    joblib.dump(vec, MODEL_DIR / "tfidf_vectorizer.pkl")
    joblib.dump(clf, MODEL_DIR / "category_classifier.pkl")
    print(f"  ✓ Saved to ml/models/")


# ─────────────────────────────────────────────────────────────────────────────
# FRAUD DETECTOR  (Isolation Forest)
# ─────────────────────────────────────────────────────────────────────────────

def _engineer_features(amounts, times=None):
    """Convert raw values to 5 engineered features."""
    amounts = np.array(amounts, dtype=float)
    if times is None:
        times = np.zeros(len(amounts))
    times = np.array(times, dtype=float)
    hours = (times % 86400 // 3600).astype(int)

    return np.stack([
        np.log1p(np.abs(amounts)),            # log-amount
        (amounts % 100 == 0).astype(float),   # round amount
        ((hours < 6) | (hours >= 22)).astype(float),  # night tx
        np.zeros(len(amounts)),               # foreign (unknown)
        (amounts > 3000).astype(float),       # high amount
    ], axis=1)


def _generate_synthetic_fraud():
    """Synthetic legit + fraud data to augment real creditcard.csv."""
    rng = np.random.default_rng(42)
    # Legit
    n_legit = 3000
    l_amounts = rng.lognormal(4.0, 1.2, n_legit)
    l_times   = rng.uniform(8*3600, 22*3600, n_legit)  # daytime
    X_legit   = _engineer_features(l_amounts, l_times)

    # Fraud
    n_fraud = 150
    f_amounts = np.concatenate([
        rng.uniform(5000, 15000, 50),  # large amounts
        np.tile([100, 500, 1000, 9999, 4999], 20)[:n_fraud-50],
    ])
    f_times = rng.uniform(0*3600, 4*3600, n_fraud)  # late night
    X_fraud = _engineer_features(f_amounts, f_times)

    return X_legit, X_fraud


def train_fraud_detector():
    print("\n══════════════════════════════════════════════")
    print("  FRAUD DETECTOR  (Isolation Forest)")
    print("══════════════════════════════════════════════")

    X_legit_parts = []
    total_fraud = 0

    # Real creditcard.csv
    if FRAUD_CSV.exists():
        df = pd.read_csv(FRAUD_CSV)
        print(f"  Real data: {len(df):,} rows | Fraud: {df['Class'].sum():,} | Legit: {(df['Class']==0).sum():,}")
        total_fraud = int(df['Class'].sum())

        # Use all legitimate transactions (capped at 20k for speed)
        df_legit = df[df["Class"] == 0].sample(min(20000, len(df[df["Class"] == 0])), random_state=42)
        X_real_legit = _engineer_features(df_legit["Amount"].values, df_legit["Time"].values)
        X_legit_parts.append(X_real_legit)
        print(f"  Using {len(X_real_legit):,} real legit transactions for training")
    else:
        print("  creditcard.csv not found — using synthetic only")

    # Synthetic augmentation
    X_synth_legit, X_synth_fraud = _generate_synthetic_fraud()
    X_legit_parts.append(X_synth_legit)
    print(f"  + {len(X_synth_legit)} synthetic legit  +  {len(X_synth_fraud)} synthetic fraud (injected)")

    X_all = np.vstack(X_legit_parts)

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X_all)

    contamination = min(0.05, (len(X_synth_fraud) / len(X_all)) + 0.01)
    model = IsolationForest(
        n_estimators=400,
        contamination=contamination,
        random_state=42,
        max_features=1.0,
        n_jobs=-1,
    )
    model.fit(X_scaled)

    # Quick eval on synthetic fraud
    X_synth_fraud_scaled = scaler.transform(X_synth_fraud)
    preds = model.predict(X_synth_fraud_scaled)
    detection_rate = (preds == -1).mean()
    print(f"\n  Synthetic fraud detection rate: {detection_rate:.1%}")
    print(f"  Anomaly threshold: {model.offset_:.4f}")

    joblib.dump(model,  MODEL_DIR / "fraud_model.pkl")
    joblib.dump(scaler, MODEL_DIR / "fraud_scaler.pkl")
    print(f"  ✓ Saved to ml/models/")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  FinA — Model Training Pipeline")
    print("=" * 55)
    train_categorizer()
    train_fraud_detector()
    print("\n" + "=" * 55)
    print("  ✅  All models trained and saved to ml/models/")
    print("  Restart uvicorn to pick up the new models.")
    print("=" * 55)
