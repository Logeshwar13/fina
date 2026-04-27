"""
ml/fraud_detector.py
────────────────────
Fraud detection using Isolation Forest trained on creditcard.csv.

creditcard.csv columns: Time, V1–V28, Amount, Class
  Class 0 = legitimate  |  Class 1 = fraud

For API transactions (which don't have V1-V28 PCA features), we derive
proxy features from the transaction's measurable properties:

  - amount_zscore   : how far amount deviates from user's history
  - amount_abs      : raw amount (log-scaled)
  - hour            : time-of-day (night txns riskier)
  - is_round_amount : amounts like 1000, 500 are suspicious
  - velocity        : number of transactions in last 1 hour (placeholder)

The Isolation Forest is trained on these engineered features using
synthetic data of the same shape (since creditcard.csv V features
are PCA-transformed and not reproducible from raw text).

If the model pkl is found it is loaded; otherwise a lightweight model
is fit on-the-fly from synthetic representative data.
"""

import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from typing import Tuple, List

MODEL_DIR   = Path(__file__).parent / "models"
MODEL_PATH  = MODEL_DIR / "fraud_model.pkl"
SCALER_PATH = MODEL_DIR / "fraud_scaler.pkl"

# Fraud threshold on anomaly score (the more negative → more anomalous)
ANOMALY_THRESHOLD = -0.10   # tuned on synthetic balanced data


def _make_features(amount: float, hour: int, location: str = "") -> np.ndarray:
    """
    Derive engineered features from a raw transaction.
    Returns shape (1, 5).
    """
    log_amount    = float(np.log1p(abs(amount)))
    is_round      = 1.0 if (amount % 100 == 0 and amount > 0) else 0.0
    is_night      = 1.0 if hour < 6 or hour >= 22 else 0.0
    is_foreign    = 1.0 if location and location.lower() not in ("", "local", "domestic") else 0.0
    high_amount   = 1.0 if amount > 3000 else 0.0

    return np.array([[log_amount, is_round, is_night, is_foreign, high_amount]])


def _fit_default_model():
    """
    Fit a fast Isolation Forest on representative synthetic data so the
    service can work without running train_models.py first.
    """
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(42)

    # Legitimate transactions
    n_legit = 5000
    # Create realistic typical spending
    leg_amounts = rng.lognormal(6.0, 1.5, n_legit) # average ~400, up to ~50k
    leg_hours   = rng.integers(6, 23, n_legit)
    # Roughly 30% of legitimate transactions are round numbers
    leg_round   = rng.choice([0.0, 1.0], size=n_legit, p=[0.7, 0.3])
    leg_night   = ((leg_hours < 6) | (leg_hours >= 23)).astype(float)
    leg_foreign = rng.binomial(1, 0.01, n_legit).astype(float)
    leg_high    = (leg_amounts > 10000).astype(float)

    legit = np.stack([
        np.log1p(leg_amounts), leg_round, leg_night.astype(float),
        leg_foreign, leg_high
    ], axis=1)

    # Fraudulent transactions
    n_fraud = 150
    # Extreme anomalies
    fr_amounts = rng.choice([50000, 100000, 250000, 4000, 200000], n_fraud)
    fr_hours   = rng.choice([1, 2, 3, 4], n_fraud)
    fr_data = np.stack([
        np.log1p(fr_amounts), np.ones(n_fraud), np.ones(n_fraud),
        rng.choice([1.0, 0.0], n_fraud, p=[0.8, 0.2]), np.ones(n_fraud)
    ], axis=1)

    X = np.vstack([legit, fr_data])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=300,
        contamination=0.03,
        random_state=42,
        max_features=1.0,
    )
    model.fit(X_scaled)

    # Save for future use
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print("[FraudDetector] Default model trained and saved ✓")
    return model, scaler


class FraudDetector:
    """
    Wraps Isolation Forest.
    Use detect(amount, hour, location) for per-transaction scoring.
    """

    def __init__(self):
        self.model  = None
        self.scaler = None
        self._load()

    def _load(self):
        if MODEL_PATH.exists() and SCALER_PATH.exists():
            try:
                self.model  = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                print("[FraudDetector] Model loaded ✓")
                return
            except Exception as e:
                print(f"[FraudDetector] Load error: {e}")
        print("[FraudDetector] No saved model → fitting default model …")
        self.model, self.scaler = _fit_default_model()

    def detect(
        self,
        amount: float,
        hour: int = 12,
        location: str = "",
    ) -> Tuple[bool, float, List[str]]:
        """
        Returns (is_fraud, fraud_score 0-1, list_of_reasons).
        fraud_score: 0 = totally normal, 1 = highly suspicious.
        """
        X = _make_features(amount, hour, location)
        X_scaled = self.scaler.transform(X)
        
        # Scikit-Learn IsolationForest returns positive for Safe (Inliers) and negative for Fraud (Outliers)
        decision_score = float(self.model.decision_function(X_scaled)[0])

        # Map decision_score (typically +0.1 to -0.2) to a 0.0 - 1.0 probability score
        # decision_score = 0 is exactly 50% anomaly threshold.
        fraud_score = float(np.clip(0.5 - (decision_score / 0.2), 0.0, 1.0))
        is_fraud = decision_score < 0.0

        reasons: List[str] = []
        if amount > 25000:
            reasons.append("Unusually high transaction amount")
        if hour < 6 or hour >= 23:
            reasons.append("Transaction at unusual hour")
        if amount % 100 == 0 and amount >= 50000:
            reasons.append("Round-number amount pattern at high value")
        if location and location.lower() not in ("", "local", "domestic"):
            reasons.append(f"Foreign/unfamiliar location: {location}")
        if not reasons and is_fraud:
            reasons.append("Statistical anomaly detected by AI model")

        return is_fraud, fraud_score, reasons


# Singleton loaded at startup
detector = FraudDetector()
