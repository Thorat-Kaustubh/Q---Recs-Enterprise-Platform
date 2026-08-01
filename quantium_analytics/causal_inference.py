"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Module: Synthetic Control Matching Engine (SCME) & Causal Inference Framework
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from quantium_analytics.config import PRE_TRIAL_MONTHS, TRIAL_MONTHS, CRITICAL_T_VALUE, ASSETS_DIR

logger = logging.getLogger(__name__)


def _save_fig(filename, dpi=300):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    plt.savefig(os.path.join(ASSETS_DIR, filename), dpi=dpi)



def aggregate_store_monthly_metrics(df):
    """Aggregate store transactions into monthly metrics and isolate 12-month fully operational stores."""
    logger.info("Aggregating Store Monthly Metrics...")
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df.get('DATE')):
        if 'DATE_CLEAN' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE_CLEAN'])
        else:
            df['DATE'] = pd.to_datetime(df['DATE'])

    df['YEARMONTH'] = df['DATE'].dt.year * 100 + df['DATE'].dt.month

    monthly = df.groupby(['STORE_NBR', 'YEARMONTH']).agg(
        totSales=('TOT_SALES', 'sum'),
        nCustomers=('LYLTY_CARD_NBR', 'nunique'),
        nTxns=('TXN_ID', 'nunique'),
        totQty=('PROD_QTY', 'sum')
    ).reset_index()

    monthly['nTxnsPerCust'] = monthly['nTxns'] / monthly['nCustomers']
    monthly['nChipsPerTxn'] = monthly['totQty'] / monthly['nTxns']
    monthly['avgPricePerUnit'] = monthly['totSales'] / monthly['totQty']

    # Filter fully operational stores across 12 months
    store_month_counts = monthly.groupby('STORE_NBR')['YEARMONTH'].nunique()
    full_stores = store_month_counts[store_month_counts == 12].index.tolist()
    monthly_full = monthly[monthly['STORE_NBR'].isin(full_stores)].copy()

    logger.info(f"Identified {len(full_stores)} stores with complete 12-month pre/post trial operation.")
    return monthly_full, full_stores


def calculate_pearson_correlation(df_pre, trial_store, metric, candidate_stores):
    """Calculate Pearson correlation for a target metric between trial store and candidates."""
    trial_series = df_pre[df_pre['STORE_NBR'] == trial_store].set_index('YEARMONTH')[metric]
    correlations = {}
    for store in candidate_stores:
        if store == trial_store:
            continue
        control_series = df_pre[df_pre['STORE_NBR'] == store].set_index('YEARMONTH')[metric]
        correlations[store] = trial_series.corr(control_series)
    return pd.Series(correlations)


def calculate_magnitude_distance_score(df_pre, trial_store, metric, candidate_stores):
    """Calculate normalized magnitude distance score: 1 - (dist - min_dist)/(max_dist - min_dist)."""
    trial_series = df_pre[df_pre['STORE_NBR'] == trial_store].set_index('YEARMONTH')[metric]
    distances = {}
    for store in candidate_stores:
        if store == trial_store:
            continue
        control_series = df_pre[df_pre['STORE_NBR'] == store].set_index('YEARMONTH')[metric]
        distances[store] = np.mean(np.abs(trial_series - control_series))

    dist_series = pd.Series(distances)
    min_dist, max_dist = dist_series.min(), dist_series.max()
    magnitude_score = 1.0 - (dist_series - min_dist) / (max_dist - min_dist) if max_dist > min_dist else 1.0
    return magnitude_score


def match_synthetic_control(monthly_full, trial_store, full_stores):
    """Synthetic Control Matching Engine (SCME) utilizing Composite Pearson-Magnitude Metric."""
    logger.info(f"SCME Matching: Finding control store match for Trial Store {trial_store}...")
    df_pre = monthly_full[monthly_full['YEARMONTH'].isin(PRE_TRIAL_MONTHS)]

    corr_sales = calculate_pearson_correlation(df_pre, trial_store, 'totSales', full_stores)
    corr_cust = calculate_pearson_correlation(df_pre, trial_store, 'nCustomers', full_stores)

    mag_sales = calculate_magnitude_distance_score(df_pre, trial_store, 'totSales', full_stores)
    mag_cust = calculate_magnitude_distance_score(df_pre, trial_store, 'nCustomers', full_stores)

    score_sales = 0.5 * corr_sales + 0.5 * mag_sales
    score_cust = 0.5 * corr_cust + 0.5 * mag_cust
    final_score = 0.5 * score_sales + 0.5 * score_cust

    rankings = pd.DataFrame({
        'corr_sales': corr_sales,
        'corr_cust': corr_cust,
        'mag_sales': mag_sales,
        'mag_cust': mag_cust,
        'final_score': final_score
    }).sort_values(by='final_score', ascending=False)

    best_control = rankings.index[0]
    best_score = rankings.loc[best_control, 'final_score']
    logger.info(f"Trial Store {trial_store} matched with Control Store {best_control} (Composite Match Score: {best_score * 100:.1f}%).")
    return best_control, rankings


def evaluate_causal_impact(monthly_full, trial_store, control_store):
    """Difference-in-Differences (DiD) Causal Impact Evaluation with Scaled Controls."""
    logger.info(f"Evaluating Causal Impact: Trial Store {trial_store} vs Control Store {control_store}...")
    df_pre = monthly_full[monthly_full['YEARMONTH'].isin(PRE_TRIAL_MONTHS)]
    df_trial = monthly_full[monthly_full['YEARMONTH'].isin(TRIAL_MONTHS)]

    t_pre = df_pre[df_pre['STORE_NBR'] == trial_store].set_index('YEARMONTH')
    c_pre = df_pre[df_pre['STORE_NBR'] == control_store].set_index('YEARMONTH')

    # Scaling Factors
    scale_sales = t_pre['totSales'].sum() / c_pre['totSales'].sum()
    scale_cust = t_pre['nCustomers'].sum() / c_pre['nCustomers'].sum()

    # Pre-trial percentage standard deviation
    pre_diff_sales = (t_pre['totSales'] - c_pre['totSales'] * scale_sales) / (c_pre['totSales'] * scale_sales)
    std_sales = pre_diff_sales.std()

    pre_diff_cust = (t_pre['nCustomers'] - c_pre['nCustomers'] * scale_cust) / (c_pre['nCustomers'] * scale_cust)
    std_cust = pre_diff_cust.std()

    # Evaluate Trial Period
    t_tr = df_trial[df_trial['STORE_NBR'] == trial_store].set_index('YEARMONTH')
    c_tr = df_trial[df_trial['STORE_NBR'] == control_store].set_index('YEARMONTH')

    results = []
    for m in TRIAL_MONTHS:
        s_tr = t_tr.loc[m, 'totSales']
        s_co_scaled = c_tr.loc[m, 'totSales'] * scale_sales
        s_diff = (s_tr - s_co_scaled) / s_co_scaled
        s_tstat = s_diff / std_sales if std_sales > 0 else 0

        c_tr_val = t_tr.loc[m, 'nCustomers']
        c_co_scaled = c_tr.loc[m, 'nCustomers'] * scale_cust
        c_diff = (c_tr_val - c_co_scaled) / c_co_scaled
        c_tstat = c_diff / std_cust if std_cust > 0 else 0

        results.append({
            'YEARMONTH': m,
            'Sales_Trial': s_tr,
            'Sales_Control_Scaled': s_co_scaled,
            'Sales_Pct_Diff': s_diff,
            'Sales_t_stat': s_tstat,
            'Sales_Sig_95': s_tstat > CRITICAL_T_VALUE,
            'Cust_Trial': c_tr_val,
            'Cust_Control_Scaled': c_co_scaled,
            'Cust_Pct_Diff': c_diff,
            'Cust_t_stat': c_tstat,
            'Cust_Sig_95': c_tstat > CRITICAL_T_VALUE
        })

    eval_df = pd.DataFrame(results)
    return scale_sales, scale_cust, std_sales, std_cust, eval_df


def generate_causal_plots(monthly_full, trial_store, control_store, scale_sales, scale_cust, std_sales, std_cust):
    """Generate time-series causal evaluation charts with 95% confidence bands."""
    logger.info(f"Plotting Causal Impact Time-Series for Store {trial_store}...")
    store_m = monthly_full[monthly_full['STORE_NBR'].isin([trial_store, control_store])].copy()
    store_m['YEARMONTH_STR'] = store_m['YEARMONTH'].astype(str)
    months_order = sorted(store_m['YEARMONTH_STR'].unique())

    df_t = store_m[store_m['STORE_NBR'] == trial_store].set_index('YEARMONTH_STR')
    df_c = store_m[store_m['STORE_NBR'] == control_store].set_index('YEARMONTH_STR')

    plot_df = pd.DataFrame(index=months_order)
    plot_df['Trial_Sales'] = df_t['totSales']
    plot_df['Scaled_Control_Sales'] = df_c['totSales'] * scale_sales
    plot_df['Sales_5pct'] = plot_df['Scaled_Control_Sales'] * (1 - CRITICAL_T_VALUE * std_sales)
    plot_df['Sales_95pct'] = plot_df['Scaled_Control_Sales'] * (1 + CRITICAL_T_VALUE * std_sales)

    plot_df['Trial_Cust'] = df_t['nCustomers']
    plot_df['Scaled_Control_Cust'] = df_c['nCustomers'] * scale_cust
    plot_df['Cust_5pct'] = plot_df['Scaled_Control_Cust'] * (1 - CRITICAL_T_VALUE * std_cust)
    plot_df['Cust_95pct'] = plot_df['Scaled_Control_Cust'] * (1 + CRITICAL_T_VALUE * std_cust)

    x_labels = [f"{m[:4]}-{m[4:]}" for m in months_order]

    # Sales Plot
    plt.figure(figsize=(11, 5))
    plt.plot(x_labels, plot_df['Trial_Sales'], marker='o', linewidth=2.5, color='#0A2540', label=f'Trial Store {trial_store}')
    plt.plot(x_labels, plot_df['Scaled_Control_Sales'], marker='s', linewidth=2, linestyle='--', color='#FF6B00', label=f'Control Store {control_store} (Scaled)')
    plt.fill_between(x_labels, plot_df['Sales_5pct'], plot_df['Sales_95pct'], color='#FF6B00', alpha=0.15, label='95% Confidence Band')
    plt.axvspan(7, 9, color='lightgreen', alpha=0.3, label='Trial Period (Feb-Apr 2019)')
    plt.title(f'Total Sales Performance: Trial Store {trial_store} vs Control Store {control_store}', fontweight='bold', pad=15)
    plt.xlabel('Month')
    plt.ylabel('Total Sales ($)')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.tight_layout()
    _save_fig(f'trial_store_{trial_store}_sales.png', dpi=300)
    plt.close()

    # Customers Plot
    plt.figure(figsize=(11, 5))
    plt.plot(x_labels, plot_df['Trial_Cust'], marker='o', linewidth=2.5, color='#2ca02c', label=f'Trial Store {trial_store}')
    plt.plot(x_labels, plot_df['Scaled_Control_Cust'], marker='s', linewidth=2, linestyle='--', color='#d62728', label=f'Control Store {control_store} (Scaled)')
    plt.fill_between(x_labels, plot_df['Cust_5pct'], plot_df['Cust_95pct'], color='#d62728', alpha=0.15, label='95% Confidence Band')
    plt.axvspan(7, 9, color='lightgreen', alpha=0.3, label='Trial Period (Feb-Apr 2019)')
    plt.title(f'Customer Footprint Performance: Trial Store {trial_store} vs Control Store {control_store}', fontweight='bold', pad=15)
    plt.xlabel('Month')
    plt.ylabel('Unique Customers')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.tight_layout()
    _save_fig(f'trial_store_{trial_store}_customers.png', dpi=300)
    plt.close()


def run_placebo_permutation_test(monthly_full, trial_store, candidate_stores, sample_size=30):
    """Execute In-Space Placebo Permutation Test (Abadie et al.) computing RMSPE effect ratios."""
    logger.info(f"Executing In-Space Placebo Permutation Test for Trial Store {trial_store} across {sample_size} placebo stores...")

    # Filter candidate placebo stores excluding actual trial stores
    non_trial_candidates = [s for s in candidate_stores if s not in [77, 86, 88]][:sample_size]

    df_pre = monthly_full[monthly_full['YEARMONTH'].isin(PRE_TRIAL_MONTHS)]
    df_post = monthly_full[monthly_full['YEARMONTH'].isin(TRIAL_MONTHS)]

    placebo_ratios = []

    for store in non_trial_candidates:
        match_store, _ = match_synthetic_control(monthly_full, store, [s for s in candidate_stores if s != store])

        # Pre-trial RMSPE
        t_pre = df_pre[df_pre['STORE_NBR'] == store].set_index('YEARMONTH')['totSales']
        c_pre = df_pre[df_pre['STORE_NBR'] == match_store].set_index('YEARMONTH')['totSales']
        scale = t_pre.sum() / c_pre.sum() if c_pre.sum() > 0 else 1.0
        pre_rmspe = np.sqrt(np.mean((t_pre - c_pre * scale) ** 2))

        # Post-trial RMSPE
        t_post = df_post[df_post['STORE_NBR'] == store].set_index('YEARMONTH')['totSales']
        c_post = df_post[df_post['STORE_NBR'] == match_store].set_index('YEARMONTH')['totSales']
        post_rmspe = np.sqrt(np.mean((t_post - c_post * scale) ** 2))

        ratio = post_rmspe / pre_rmspe if pre_rmspe > 0 else 1.0
        placebo_ratios.append(ratio)

    # Compute actual trial store ratio
    actual_control, _ = match_synthetic_control(monthly_full, trial_store, candidate_stores)
    t_pre_tr = df_pre[df_pre['STORE_NBR'] == trial_store].set_index('YEARMONTH')['totSales']
    c_pre_tr = df_pre[df_pre['STORE_NBR'] == actual_control].set_index('YEARMONTH')['totSales']
    scale_tr = t_pre_tr.sum() / c_pre_tr.sum()
    pre_rmspe_tr = np.sqrt(np.mean((t_pre_tr - c_pre_tr * scale_tr) ** 2))

    t_post_tr = df_post[df_post['STORE_NBR'] == trial_store].set_index('YEARMONTH')['totSales']
    c_post_tr = df_post[df_post['STORE_NBR'] == actual_control].set_index('YEARMONTH')['totSales']
    post_rmspe_tr = np.sqrt(np.mean((t_post_tr - c_post_tr * scale_tr) ** 2))

    trial_ratio = post_rmspe_tr / pre_rmspe_tr if pre_rmspe_tr > 0 else 1.0

    # Empirical p-value computation
    empirical_p = np.sum(np.array(placebo_ratios) >= trial_ratio) / len(placebo_ratios)
    logger.info(f"Placebo Test Complete for Store {trial_store}: Empirical p-value = {empirical_p:.4f} (Trial Ratio: {trial_ratio:.2f})")

    return {
        'trial_store': trial_store,
        'trial_ratio': trial_ratio,
        'placebo_ratios': placebo_ratios,
        'empirical_p_value': empirical_p
    }

