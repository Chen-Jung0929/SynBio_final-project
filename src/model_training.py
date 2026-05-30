#!/usr/bin/env python3
import os
import sys
import yaml
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix
import xgboost as xgb

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def train_and_evaluate(df_expr, df_meta, tables_dir, models_dir, ml_config):
    print("[*] Starting machine learning classifier training...")
    
    # Load top candidates (we use the top 100 genes by AUC to train our classifiers to avoid overfitting and keep XAI clean)
    candidates_path = tables_dir / "top_tumor_high_candidates.csv"
    df_cand = pd.read_csv(candidates_path)
    top_genes = df_cand["gene"].head(100).tolist()
    
    print(f"[*] Selected top 100 candidate genes for model training.")
    
    # Prepare X and y
    # Samples as rows, genes as columns
    X = df_expr.loc[top_genes].T
    y = (df_meta.set_index("sample_id").loc[X.index]["group"] == "PDAC").astype(int).values
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=(1.0 - ml_config["train_size"]), 
        random_state=ml_config["random_state"],
        stratify=y
    )
    
    print(f"[*] Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    
    # We will compare three models: L1 Logistic Regression, Random Forest, and XGBoost
    models = {
        "Logistic_Regression_L1": LogisticRegression(penalty="l1", solver="liblinear", C=0.5, random_state=ml_config["random_state"]),
        "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=ml_config["random_state"]),
        "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss", max_depth=3, random_state=ml_config["random_state"])
    }
    
    cv_results = []
    cv_folds = ml_config["cv_folds"]
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=ml_config["random_state"])
    
    for model_name, model in models.items():
        print(f"[*] Evaluating {model_name} with {cv_folds}-fold CV...")
        fold_auc = []
        fold_acc = []
        fold_f1 = []
        
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train[train_idx], y_train[val_idx]
            
            # Train
            model.fit(X_tr, y_tr)
            
            # Predict
            preds = model.predict(X_val)
            probs = model.predict_proba(X_val)[:, 1]
            
            # Metrics
            fold_auc.append(roc_auc_score(y_val, probs))
            fold_acc.append(accuracy_score(y_val, preds))
            fold_f1.append(f1_score(y_val, preds))
            
        cv_results.append({
            "Model": model_name,
            "Mean_CV_AUC": np.mean(fold_auc),
            "Std_CV_AUC": np.std(fold_auc),
            "Mean_CV_Accuracy": np.mean(fold_acc),
            "Mean_CV_F1": np.mean(fold_f1)
        })
        
    df_cv = pd.DataFrame(cv_results)
    cv_out = tables_dir / "cross_validation_results.csv"
    df_cv.to_csv(cv_out, index=False)
    print(f"[+] Saved CV results to {cv_out}")
    print(df_cv.to_string(index=False))
    
    # Train final models on X_train and evaluate on X_test
    perf_results = []
    best_test_auc = -1.0
    best_model = None
    best_model_name = ""
    
    for model_name, model in models.items():
        print(f"[*] Training final model {model_name} on train set...")
        model.fit(X_train, y_train)
        
        # Test performance
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]
        
        test_auc = roc_auc_score(y_test, probs)
        test_acc = accuracy_score(y_test, preds)
        test_prec = precision_score(y_test, preds)
        test_rec = recall_score(y_test, preds)
        test_f1 = f1_score(y_test, preds)
        
        cm = confusion_matrix(y_test, preds)
        
        perf_results.append({
            "Model": model_name,
            "Test_AUC": test_auc,
            "Test_Accuracy": test_acc,
            "Test_Precision": test_prec,
            "Test_Recall": test_rec,
            "Test_F1": test_f1,
            "TN": cm[0, 0],
            "FP": cm[0, 1],
            "FN": cm[1, 0],
            "TP": cm[1, 1]
        })
        
        if test_auc > best_test_auc:
            best_test_auc = test_auc
            best_model = model
            best_model_name = model_name
            
    df_perf = pd.DataFrame(perf_results)
    perf_out = tables_dir / "model_performance_summary.csv"
    df_perf.to_csv(perf_out, index=False)
    print(f"[+] Saved model performance summary to {perf_out}")
    print(df_perf.to_string(index=False))
    
    # Save the best model
    models_dir.mkdir(parents=True, exist_ok=True)
    best_model_path = models_dir / "best_classifier.pkl"
    # We save a dictionary containing the model, the feature names (genes used), and train/test splits for XAI
    model_data = {
        "model": best_model,
        "model_name": best_model_name,
        "features": top_genes,
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test
    }
    joblib.dump(model_data, best_model_path)
    print(f"[+] Saved best classifier ({best_model_name}) to {best_model_path}")

def main():
    config = load_config()
    processed_dir = Path(__file__).parent.parent / config["data"]["processed_dir"]
    tables_dir = Path(__file__).parent.parent / config["results"]["tables_dir"]
    models_dir = Path(__file__).parent.parent / config["results"]["models_dir"]
    
    expr_path = processed_dir / "expression_matrix.csv.gz"
    meta_path = tables_dir / "sample_metadata.csv"
    
    df_expr = pd.read_csv(expr_path, index_col=0, compression="gzip")
    df_meta = pd.read_csv(meta_path)
    
    train_and_evaluate(df_expr, df_meta, tables_dir, models_dir, config["ml_model"])

if __name__ == "__main__":
    main()
