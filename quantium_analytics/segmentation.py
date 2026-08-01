import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from quantium_analytics.config import ASSETS_DIR

logger = logging.getLogger(__name__)


def _save_fig(filename, dpi=300):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    plt.savefig(os.path.join(ASSETS_DIR, filename), dpi=dpi)



def calculate_segment_kpis(df):
    """Aggregate customer segment KPI metrics: Total Revenue, Unique Customers, Units/Cust, Price/Unit."""
    logger.info("Computing Multi-Dimensional Customer Segment KPIs...")
    sales = df.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'])['TOT_SALES'].sum()
    cust_count = df.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'])['LYLTY_CARD_NBR'].nunique()
    qty = df.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'])['PROD_QTY'].sum()

    metrics = pd.DataFrame({
        'TOT_SALES': sales,
        'CUST_COUNT': cust_count,
        'TOTAL_QTY': qty
    }).reset_index()

    metrics['AVG_UNITS_PER_CUST'] = metrics['TOTAL_QTY'] / metrics['CUST_COUNT']
    metrics['AVG_PRICE_PER_UNIT'] = metrics['TOT_SALES'] / metrics['TOTAL_QTY']
    metrics = metrics.sort_values(by='TOT_SALES', ascending=False).reset_index(drop=True)
    return metrics


def perform_welchs_hypothesis_test(df, target_lifestage='YOUNG SINGLES/COUPLES', target_premium='Mainstream'):
    """Perform Welch's 2-Sample Asymptotic t-test comparing unit prices of target segment vs peers."""
    logger.info(f"Executing Welch's t-test for target cohort ({target_lifestage} - {target_premium})...")
    df['UNIT_PRICE'] = df['TOT_SALES'] / df['PROD_QTY']

    target_mask = (df['LIFESTAGE'] == target_lifestage) & (df['PREMIUM_CUSTOMER'] == target_premium)
    peer_mask = (df['LIFESTAGE'] == target_lifestage) & (df['PREMIUM_CUSTOMER'] != target_premium)

    target_prices = df[target_mask]['UNIT_PRICE']
    peer_prices = df[peer_mask]['UNIT_PRICE']

    mean_target = target_prices.mean()
    mean_peer = peer_prices.mean()

    t_stat, p_val = stats.ttest_ind(target_prices, peer_prices, equal_var=False)

    results = {
        'mean_target': mean_target,
        'mean_peer': mean_peer,
        'diff': mean_target - mean_peer,
        't_stat': t_stat,
        'p_value': p_val,
        'is_significant': p_val < 0.05
    }
    logger.info(f"Welch's t-test: t={t_stat:.4f}, p={p_val:.4e} | Target Mean: ${mean_target:.2f}, Peer Mean: ${mean_peer:.2f}")
    return results


def calculate_purchasing_affinities(df, target_lifestage='YOUNG SINGLES/COUPLES', target_premium='Mainstream'):
    """Compute Brand and Pack Size Purchasing Affinity Vector Indices."""
    logger.info("Computing Purchasing Affinity Vectors...")
    target_mask = (df['LIFESTAGE'] == target_lifestage) & (df['PREMIUM_CUSTOMER'] == target_premium)

    target_df = df[target_mask]
    baseline_df = df[~target_mask]

    # Brand Affinity
    t_brand = target_df['BRAND'].value_counts(normalize=True)
    b_brand = baseline_df['BRAND'].value_counts(normalize=True)
    brand_aff = pd.DataFrame({'TARGET_PROP': t_brand, 'BASELINE_PROP': b_brand}).fillna(0)
    brand_aff['AFFINITY'] = brand_aff['TARGET_PROP'] / brand_aff['BASELINE_PROP']
    brand_aff = brand_aff.sort_values(by='AFFINITY', ascending=False)

    # Pack Size Affinity
    t_pack = target_df['PACK_SIZE'].value_counts(normalize=True)
    b_pack = baseline_df['PACK_SIZE'].value_counts(normalize=True)
    pack_aff = pd.DataFrame({'TARGET_PROP': t_pack, 'BASELINE_PROP': b_pack}).fillna(0)
    pack_aff['AFFINITY'] = pack_aff['TARGET_PROP'] / pack_aff['BASELINE_PROP']
    pack_aff = pack_aff.sort_values(by='AFFINITY', ascending=False)

    return brand_aff, pack_aff


def generate_segmentation_plots(metrics, brand_aff, pack_aff):
    """Generate high-resolution publication charts for segment analysis."""
    logger.info("Generating Segmentation & Affinity Visualizations...")

    # Helper formatting
    metrics['SEGMENT'] = metrics['LIFESTAGE'] + "\n(" + metrics['PREMIUM_CUSTOMER'] + ")"
    accent_color = '#0A2540'
    highlight_color = '#FF6B00'

    # 1. Total Sales
    plt.figure(figsize=(12, 6))
    ms = metrics.sort_values(by='TOT_SALES', ascending=True)
    colors = [highlight_color if 'YOUNG SINGLES/COUPLES\n(Mainstream)' in s else accent_color for s in ms['SEGMENT']]
    plt.barh(ms['SEGMENT'], ms['TOT_SALES'] / 1000, color=colors)
    plt.title('Total Chip Revenue by Customer Segment ($K)', fontweight='bold', pad=15)
    plt.xlabel('Total Sales ($ Thousands)')
    plt.tight_layout()
    _save_fig('total_sales_by_segment.png', dpi=300)
    plt.close()

    # 2. Customer Count
    plt.figure(figsize=(12, 6))
    mc = metrics.sort_values(by='CUST_COUNT', ascending=True)
    colors = [highlight_color if 'YOUNG SINGLES/COUPLES\n(Mainstream)' in s else accent_color for s in mc['SEGMENT']]
    plt.barh(mc['SEGMENT'], mc['CUST_COUNT'], color=colors)
    plt.title('Total Customer Footprint by Segment', fontweight='bold', pad=15)
    plt.xlabel('Unique Customers')
    plt.tight_layout()
    _save_fig('customer_count_by_segment.png', dpi=300)
    plt.close()

    # 3. Units per Customer
    plt.figure(figsize=(12, 6))
    mu = metrics.sort_values(by='AVG_UNITS_PER_CUST', ascending=True)
    colors = [highlight_color if 'YOUNG SINGLES/COUPLES\n(Mainstream)' in s else accent_color for s in mu['SEGMENT']]
    plt.barh(mu['SEGMENT'], mu['AVG_UNITS_PER_CUST'], color=colors)
    plt.title('Average Purchased Packs per Customer', fontweight='bold', pad=15)
    plt.xlabel('Avg Units per Customer')
    plt.tight_layout()
    _save_fig('units_per_customer.png', dpi=300)
    plt.close()

    # 4. Price per Unit
    plt.figure(figsize=(12, 6))
    mp = metrics.sort_values(by='AVG_PRICE_PER_UNIT', ascending=True)
    colors = [highlight_color if 'YOUNG SINGLES/COUPLES\n(Mainstream)' in s else accent_color for s in mp['SEGMENT']]
    plt.barh(mp['SEGMENT'], mp['AVG_PRICE_PER_UNIT'], color=colors)
    plt.title('Average Price per Unit ($) by Segment', fontweight='bold', pad=15)
    plt.xlabel('Average Unit Price ($)')
    plt.tight_layout()
    _save_fig('price_per_unit.png', dpi=300)
    plt.close()

    # 5. Brand Affinity Plot
    plt.figure(figsize=(10, 5))
    ba = brand_aff.sort_values(by='AFFINITY', ascending=True)
    colors = ['#2ca02c' if a > 1.0 else '#d62728' for a in ba['AFFINITY']]
    plt.barh(ba.index, ba['AFFINITY'], color=colors)
    plt.axvline(1.0, color='black', linestyle='--', linewidth=1)
    plt.title('Brand Purchasing Affinity Index: Young Singles/Couples (Mainstream)', fontweight='bold', pad=15)
    plt.xlabel('Affinity Index (>1.0 = High Preference)')
    plt.tight_layout()
    _save_fig('brand_affinity_young_mainstream.png', dpi=300)
    plt.close()

    # 6. Pack Size Affinity Plot
    plt.figure(figsize=(10, 5))
    pa = pack_aff.sort_values(by='AFFINITY', ascending=True)
    pa.index = [f"{int(x)}g" for x in pa.index]
    colors = ['#2ca02c' if a > 1.0 else '#d62728' for a in pa['AFFINITY']]
    plt.barh(pa.index, pa['AFFINITY'], color=colors)
    plt.axvline(1.0, color='black', linestyle='--', linewidth=1)
    plt.title('Pack Size Purchasing Affinity Index: Young Singles/Couples (Mainstream)', fontweight='bold', pad=15)
    plt.xlabel('Affinity Index (>1.0 = High Preference)')
    plt.tight_layout()
    _save_fig('pack_size_affinity_young_mainstream.png', dpi=300)
    plt.close()

    logger.info("Saved all publication-quality segmentation plots.")
