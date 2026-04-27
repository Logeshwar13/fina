"""
ml/categorizer.py
─────────────────
Expense categorization model.
  - Training: TF-IDF vectorizer + Logistic Regression on personal_expense.csv
              columns → Item (text), Category (target label)
  - Inference: predict_category(description) → (category, confidence, alternatives)
  - Falls back to a keyword-based heuristic if model file not found.
"""

import os
import re
import joblib
import numpy as np
from pathlib import Path
from typing import Tuple, List

# ── Model paths ───────────────────────────────────────────────────────────────
MODEL_DIR     = Path(__file__).parent / "models"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
CLASSIFIER_PATH = MODEL_DIR / "category_classifier.pkl"

# ── Category labels (keep in sync with training) ─────────────────────────────
CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Insurance",
    "Utilities",
    "Housing",
    "Education",
    "Travel",
    "Income",
    "Other",
]

# ── Keyword fallback ──────────────────────────────────────────────────────────
KEYWORD_MAP = {
    "Food & Dining":    r"food|restaurant|cafe|coffee|lunch|dinner|breakfast|pizza|burger|grocery|supermarket|eat|meal|chai|snack",
    "Transportation":   r"uber|lyft|taxi|bus|train|metro|fuel|gas|petrol|parking|toll|cab|transport|commute",
    "Shopping":         r"amazon|flipkart|mall|shop|store|purchase|buy|cloth|fashion|shoe|apparel|retail",
    "Entertainment":    r"netflix|spotify|movie|cinema|theatre|game|concert|event|ticket|streaming|music",
    "Healthcare":       r"doctor|hospital|pharmacy|medicine|clinic|health|dental|medical|surgery|operation|treatment|checkup|test|scan|mri|ct|x-ray|blood|vaccination|emergency|ambulance|icu|cardiac|heart|cancer|chemotherapy|dialysis|pathology|radiology|consultation|specialist|cardiologist|neurologist|orthopedic|pediatrician",
    "Insurance":        r"insurance premium|life insurance|health insurance|term insurance|medical insurance|policy premium|insurance renewal|insurance payment|coverage|policy|premium payment",
    "Utilities":        r"electric|water|gas bill|internet|wifi|broadband|utility|bill|recharge|mobile",
    "Housing":          r"rent|mortgage|house|apartment|home|maintenance|repair|real estate",
    "Education":        r"school|college|university|course|tuition|book|stationery|library|fees",
    "Travel":           r"hotel|flight|airlines|airbnb|vacation|trip|tourism|booking|holiday",
    "Income":           r"salary|income|payroll|wage|freelance|transfer received|credit",
}


def _keyword_predict(description: str) -> Tuple[str, float]:
    """Simple rule-based fallback categorizer."""
    desc = description.lower()
    for category, pattern in KEYWORD_MAP.items():
        if re.search(pattern, desc):
            return category, 0.75
    return "Other", 0.50


class CategoryPredictor:
    """Wraps the trained TF-IDF + LR model with a keyword fallback."""

    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self._loaded = False
        self._load()

    def _load(self):
        """Load pickled model if it exists."""
        if VECTORIZER_PATH.exists() and CLASSIFIER_PATH.exists():
            try:
                self.vectorizer = joblib.load(VECTORIZER_PATH)
                self.classifier = joblib.load(CLASSIFIER_PATH)
                self._loaded = True
                print("[Categorizer] ML model loaded ✓")
            except Exception as e:
                print(f"[Categorizer] Failed to load model: {e}. Using keyword fallback.")
        else:
            print("[Categorizer] No trained model found → using keyword fallback. "
                  "Run data/train_models.py to train.")

    def predict(self, description: str) -> Tuple[str, float, List[str]]:
        """
        Returns (category, confidence, top_alternatives)
        """
        if not self._loaded:
            cat, conf = _keyword_predict(description)
            return cat, conf, []

        X = self.vectorizer.transform([description])
        proba = self.classifier.predict_proba(X)[0]
        classes = self.classifier.classes_

        # top prediction
        top_idx  = int(np.argmax(proba))
        category = classes[top_idx]
        confidence = float(proba[top_idx])

        # top-3 alternatives (excluding winner)
        sorted_idx = np.argsort(proba)[::-1]
        alternatives = [classes[i] for i in sorted_idx if i != top_idx][:2]

        return category, confidence, list(alternatives)


# Singleton instance loaded at startup
predictor = CategoryPredictor()
