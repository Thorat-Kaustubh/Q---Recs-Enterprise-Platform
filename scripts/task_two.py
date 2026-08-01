"""
Quantium Retail Strategy and Analytics: Store Trial Performance & Control Matching
Task 2 Script - Powered by Quantium Enterprise Analytics Platform (Q-RECS)
"""

import pandas as pd
from quantium_analytics.config import CLEAN_DATA_CSV
from quantium_analytics.causal_inference import (
    aggregate_store_monthly_metrics, match_synthetic_control,
    evaluate_causal_impact, generate_causal_plots
)


def load_data():
    df = pd.read_csv(CLEAN_DATA_CSV)
    df['DATE'] = pd.to_datetime(df['DATE_CLEAN'])
    return df


def aggregate_monthly_data(df):
    return aggregate_store_monthly_metrics(df)


def find_control_store(monthly_full, trial_store, full_stores):
    return match_synthetic_control(monthly_full, trial_store, full_stores)


def evaluate_trial_performance(monthly_full, trial_store, control_store):
    scale_sales, scale_cust, std_sales, std_cust, eval_df = evaluate_causal_impact(monthly_full, trial_store, control_store)
    from quantium_analytics.config import CRITICAL_T_VALUE
    return scale_sales, scale_cust, std_sales, std_cust, CRITICAL_T_VALUE, eval_df


def main():
    print("=" * 80)
    print("QUANTIUM STORE TRIAL EXPERIMENTATION - TASK 2 PIPELINE")
    print("=" * 80)

    df = load_data()
    monthly_full, full_stores = aggregate_monthly_data(df)

    for ts in [77, 86, 88]:
        best_control, rankings = match_synthetic_control(monthly_full, ts, full_stores)
        scale_sales, scale_cust, std_sales, std_cust, eval_df = evaluate_causal_impact(monthly_full, ts, best_control)
        generate_causal_plots(monthly_full, ts, best_control, scale_sales, scale_cust, std_sales, std_cust)

    print("\n" + "=" * 80)
    print("TASK 2 COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == '__main__':
    main()
