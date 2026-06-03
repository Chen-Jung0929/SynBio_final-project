#!/usr/bin/env python3
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import shap

def fit_polynomial_crossing(x, y):
    """
    Fits a 3rd degree polynomial to find the value of x where y crosses 0.
    Handles boundaries and falls back to simple sign-change crossing if needed.
    """
    try:
        poly = np.polyfit(x, y, 3)
        roots = np.roots(poly)
        valid_roots = [r for r in roots if np.isreal(r) and min(x) <= r <= max(x)]
        if valid_roots:
            return float(np.real(valid_roots[0]))
    except:
        pass
    
    # Fallback: identify sample-level zero crossing
    crossings = np.where(np.diff(np.sign(y)))[0]
    if len(crossings) > 0:
        return float(x[crossings[0]])
    return None

def compute_youden_threshold(x, y_true):
    """
    Fallback threshold estimation using Youden's J statistic.
    Finds the threshold in x that maximizes: sensitivity + specificity - 1.
    """
    best_thresh = np.median(x)
    best_youden = -1.0
    thresholds = np.percentile(x, np.linspace(5, 95, 100))
    for t in thresholds:
        y_pred = (x > t).astype(int)
        # Avoid division by zero
        if np.sum(y_true == 1) == 0 or np.sum(y_true == 0) == 0:
            continue
        sens = np.mean(y_pred[y_true == 1])
        spec = np.mean(y_pred[y_true == 0] == 0)
        youden = sens + spec - 1.0
        if youden > best_youden:
            best_youden = youden
            best_thresh = t
    return float(best_thresh)

def estimate_thresholds(df_expr, df_meta, top_genes, out_path=None):
    """
    Trains Elastic Net SAGA, Random Forest, and XGBoost on the top_genes.
    Extracts SHAP values and identifies zero-crossings for each gene and model.
    """
    y = (df_meta["group"] == "PDAC").astype(int).values
    X_raw = df_expr.loc[top_genes].T.values  # Shape: (samples, genes)
    
    # 1. Fit Elastic Net Logistic Regression SAGA (Scaled Features)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    lr = LogisticRegression(
        penalty="elasticnet",
        solver="saga",
        l1_ratio=0.5,
        C=0.5,
        max_iter=10000,
        random_state=42,
        n_jobs=-1
    )
    lr.fit(X_scaled, y)
    coefs = lr.coef_[0]
    
    # 2. Fit Random Forest Classifier (Unscaled Features)
    rf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
    rf.fit(X_raw, y)
    explainer_rf = shap.TreeExplainer(rf)
    shap_rf_all = explainer_rf.shap_values(X_raw)
    # Check shape for multi-class/binary list outputs
    if isinstance(shap_rf_all, list) and len(shap_rf_all) > 1:
        shap_rf = shap_rf_all[1]
    elif isinstance(shap_rf_all, np.ndarray) and len(shap_rf_all.shape) == 3:
        shap_rf = shap_rf_all[:, :, 1]
    else:
        shap_rf = shap_rf_all
        
    # 3. Fit XGBoost Classifier (Unscaled Features)
    xgb_model = xgb.XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.05, random_state=42, n_jobs=-1)
    xgb_model.fit(X_raw, y)
    explainer_xgb = shap.TreeExplainer(xgb_model)
    shap_xgb_raw = explainer_xgb.shap_values(X_raw)
    if isinstance(shap_xgb_raw, list) and len(shap_xgb_raw) > 1:
        shap_xgb = shap_xgb_raw[1]
    else:
        shap_xgb = shap_xgb_raw
        
    # Process each gene
    records = []
    for idx, gene in enumerate(top_genes):
        gene_expr = X_raw[:, idx]
        min_expr = np.min(gene_expr)
        max_expr = np.max(gene_expr)
        expr_range = max_expr - min_expr
        
        # A. Elastic Net Threshold (linear crossing at E[X_scaled] = 0 -> unscaled mean)
        w_g = coefs[idx]
        fallback_used_en = "no"
        fallback_reason_en = ""
        method_en = "linear_coefficient_crossing"
        if w_g != 0:
            k_en_orig = float(scaler.mean_[idx])
        else:
            k_en_orig = compute_youden_threshold(gene_expr, y)
            fallback_used_en = "yes"
            fallback_reason_en = "Zero coefficient in SAGA Elastic Net model"
            method_en = "youden_index_fallback"
        k_en_norm = (k_en_orig - min_expr) / expr_range if expr_range > 0 else 0.5
        
        # B. Random Forest Threshold (polynomial TreeSHAP crossing)
        rf_g_shap = shap_rf[:, idx]
        k_rf_orig = fit_polynomial_crossing(gene_expr, rf_g_shap)
        fallback_used_rf = "no"
        fallback_reason_rf = ""
        method_rf = "polynomial_shap_crossing"
        if k_rf_orig is None:
            k_rf_orig = compute_youden_threshold(gene_expr, y)
            fallback_used_rf = "yes"
            fallback_reason_rf = "No RF SHAP zero-crossing found"
            method_rf = "youden_index_fallback"
        k_rf_norm = (k_rf_orig - min_expr) / expr_range if expr_range > 0 else 0.5
        
        # C. XGBoost Threshold (polynomial TreeSHAP crossing)
        xgb_g_shap = shap_xgb[:, idx]
        k_xgb_orig = fit_polynomial_crossing(gene_expr, xgb_g_shap)
        fallback_used_xgb = "no"
        fallback_reason_xgb = ""
        method_xgb = "polynomial_shap_crossing"
        if k_xgb_orig is None:
            k_xgb_orig = compute_youden_threshold(gene_expr, y)
            fallback_used_xgb = "yes"
            fallback_reason_xgb = "No XGBoost SHAP zero-crossing found"
            method_xgb = "youden_index_fallback"
        k_xgb_norm = (k_xgb_orig - min_expr) / expr_range if expr_range > 0 else 0.5
        
        # Ensemble Stats
        k_vals = np.array([k_en_norm, k_rf_norm, k_xgb_norm])
        k_mean = np.mean(k_vals)
        k_median = np.median(k_vals)
        k_std = np.std(k_vals)
        k_iqr = np.percentile(k_vals, 75) - np.percentile(k_vals, 25)
        
        # Final threshold: default K_mean as ensemble average
        k_final = k_mean
        instability_score = k_std
        
        # Audit details
        any_fallback = "yes" if (fallback_used_en == "yes" or fallback_used_rf == "yes" or fallback_used_xgb == "yes") else "no"
        reasons = []
        if fallback_used_en == "yes": reasons.append(f"EN: {fallback_reason_en}")
        if fallback_used_rf == "yes": reasons.append(f"RF: {fallback_reason_rf}")
        if fallback_used_xgb == "yes": reasons.append(f"XGB: {fallback_reason_xgb}")
        reason_str = "; ".join(reasons) if reasons else "None"
        
        records.append({
            "gene": gene,
            "K_EN": k_en_norm,
            "K_RF": k_rf_norm,
            "K_XGB": k_xgb_norm,
            "K_mean": k_mean,
            "K_median": k_median,
            "K_std": k_std,
            "K_IQR": k_iqr,
            "K_final": k_final,
            "threshold_instability_score": instability_score,
            "threshold_method_EN": method_en,
            "threshold_method_RF": method_rf,
            "threshold_method_XGB": method_xgb,
            "fallback_used": any_fallback,
            "fallback_reason": reason_str,
            "K_EN_orig": k_en_orig,
            "K_RF_orig": k_rf_orig,
            "K_XGB_orig": k_xgb_orig,
            "K_mean_orig": k_mean * expr_range + min_expr if expr_range > 0 else min_expr
        })
        
    df_thresh = pd.DataFrame(records)
    if out_path:
        df_thresh.to_csv(out_path, index=False)
        print(f"[+] Saved thresholds to {out_path}")
        
    return df_thresh
