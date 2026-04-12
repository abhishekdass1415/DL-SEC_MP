"""
Production training pipeline for CNN-LSTM on UNSW-NB15.
Run from project root: python backend/ml/train_model.py
Saves: cnn_lstm_model.h5, scaler.pkl, feature_columns.pkl, latest_training_metrics.json
"""

import os
import sys
import json
import argparse

# Resolve paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
MODELS_DIR = os.path.join(BACKEND_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Dropout, LSTM, Dense

# Dataset paths
DEFAULT_TRAIN_CSV = os.path.join(PROJECT_ROOT, "UNSW_NB15_training-set.csv")
DEFAULT_TEST_CSV = os.path.join(PROJECT_ROOT, "UNSW_NB15_testing-set.csv")

CATEGORICAL_COLS = ["proto", "service", "state"]
TARGET_COL = "label"

MODEL_PATH = os.path.join(MODELS_DIR, "cnn_lstm_model.h5")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
FEATURE_COLUMNS_PATH = os.path.join(MODELS_DIR, "feature_columns.pkl")
LATEST_METRICS_PATH = os.path.join(MODELS_DIR, "latest_training_metrics.json")

EPOCHS = 20
BATCH_SIZE = 64
VAL_SPLIT = 0.2
RANDOM_STATE = 42


# -----------------------------
# Data Cleaning
# -----------------------------
def load_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop(columns=["id", "attack_cat"], errors="ignore")

    if "service" in df.columns:
        df["service"] = df["service"].replace("-", "unknown")

    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].fillna("unknown").astype(str)

    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if col != TARGET_COL:
            df[col] = df[col].fillna(0)

    if TARGET_COL in df.columns:
        df[TARGET_COL] = df[TARGET_COL].fillna(0).astype(int).clip(0, 1)

    return df


# -----------------------------
# Preprocessing (Training)
# -----------------------------
def preprocess_train(train_df: pd.DataFrame, scaler: MinMaxScaler):
    train_df = load_and_clean(train_df)

    numerical_cols = [
        c for c in train_df.columns
        if c not in CATEGORICAL_COLS and c != TARGET_COL
    ]

    cat_dummies = pd.get_dummies(train_df[CATEGORICAL_COLS], dtype=int)

    X_num = train_df[numerical_cols]
    X_num_scaled = scaler.fit_transform(X_num)
    X_num_df = pd.DataFrame(X_num_scaled, columns=numerical_cols, index=train_df.index)

    feature_columns = list(numerical_cols) + list(cat_dummies.columns)

    X = pd.concat([X_num_df, cat_dummies], axis=1)
    X = X[feature_columns]

    y = train_df[TARGET_COL].values

    return X, y, feature_columns, numerical_cols


# -----------------------------
# Preprocessing (Testing)
# -----------------------------
def preprocess_test(test_df: pd.DataFrame, scaler, feature_columns, numerical_cols):
    test_df = load_and_clean(test_df)

    cat_dummies = pd.get_dummies(test_df[CATEGORICAL_COLS], dtype=int)

    X_num = test_df[numerical_cols]
    X_num_scaled = scaler.transform(X_num)
    X_num_df = pd.DataFrame(X_num_scaled, columns=numerical_cols, index=test_df.index)

    X = pd.concat([X_num_df, cat_dummies], axis=1)
    X = X.reindex(columns=feature_columns, fill_value=0)

    y = test_df[TARGET_COL].values

    return X, y


# -----------------------------
# Model Architecture
# -----------------------------
def build_model(n_features: int):
    model = Sequential()

    model.add(Conv1D(64, kernel_size=1, activation="relu", input_shape=(1, n_features)))
    model.add(MaxPooling1D(pool_size=1))
    model.add(Dropout(0.2))

    model.add(Conv1D(128, kernel_size=1, activation="relu"))
    model.add(MaxPooling1D(pool_size=1))
    model.add(Dropout(0.2))

    model.add(Conv1D(256, kernel_size=1, activation="relu"))
    model.add(MaxPooling1D(pool_size=1))

    model.add(LSTM(128, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(64, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(32, return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(64, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    return model


# -----------------------------
# Main Training Flow
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default=DEFAULT_TRAIN_CSV)
    parser.add_argument("--test", default=DEFAULT_TEST_CSV)
    args = parser.parse_args()

    print("Loading datasets...")
    train_df = pd.read_csv(args.train, low_memory=False)
    test_df = pd.read_csv(args.test, low_memory=False)

    scaler = MinMaxScaler()

    print("Preprocessing training set...")
    X_train, y_train, feature_columns, numerical_cols = preprocess_train(train_df, scaler)

    n_features = X_train.shape[1]
    print("Total features:", n_features)

    # Train / Validation Split
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train,
        y_train,
        test_size=VAL_SPLIT,
        random_state=RANDOM_STATE,
        stratify=y_train
    )

    # -----------------------------
    # 🔥 CLASS IMBALANCE HANDLING
    # -----------------------------
    class_weights_array = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(y_tr),
        y=y_tr
    )
    class_weights = dict(zip(np.unique(y_tr), class_weights_array))
    print("Class Weights:", class_weights)

    # Reshape for CNN-LSTM
    print("Before reshape (train):", X_tr.shape)
    print("Before reshape (val):", X_val.shape)

    X_tr_r = X_tr.values.reshape((X_tr.shape[0], 1, n_features))
    X_val_r = X_val.values.reshape((X_val.shape[0], 1, n_features))

    print("After reshape (train):", X_tr_r.shape)
    print("After reshape (val):", X_val_r.shape)

    # Build & Train
    print("Building model...")
    model = build_model(n_features)
    model.summary()

    print("Training model...")
    model.fit(
        X_tr_r,
        y_tr,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_val_r, y_val),
        class_weight=class_weights,
        verbose=1
    )

    # Save artifacts
    model.save(MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(
        {"feature_columns": feature_columns, "numerical_cols": numerical_cols},
        FEATURE_COLUMNS_PATH
    )

    print("Saved model and preprocessing artifacts.")

    # Evaluation
    print("Evaluating on test set...")
    X_test, y_test = preprocess_test(test_df, scaler, feature_columns, numerical_cols)
    X_test_r = X_test.values.reshape((X_test.shape[0], 1, n_features))

    y_pred_proba = model.predict(X_test_r, verbose=0)
    y_pred = (y_pred_proba.flatten() > 0.5).astype(int)

    cm = confusion_matrix(y_test, y_pred)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        "confusion_matrix": {
            "tn": int(cm[0][0]),
            "fp": int(cm[0][1]),
            "fn": int(cm[1][0]),
            "tp": int(cm[1][1]),
        },
    }

    print("Test Metrics:", metrics)

    with open(LATEST_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Training completed successfully.")


if __name__ == "__main__":
    main()
