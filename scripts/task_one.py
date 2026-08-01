"""
Quantium Retail Strategy and Analytics: Chip Category Purchasing Behavior Analysis
Task 1 Script - Powered by Quantium Enterprise Analytics Platform (Q-RECS)
"""

from quantium_analytics.etl import execute_etl_pipeline
from quantium_analytics.segmentation import (
    calculate_segment_kpis, perform_welchs_hypothesis_test,
    calculate_purchasing_affinities, generate_segmentation_plots
)


def main():
    print("=" * 80)
    print("QUANTIUM CATEGORY ANALYTICS - TASK 1 PIPELINE")
    print("=" * 80)

    df_merged = execute_etl_pipeline()
    metrics = calculate_segment_kpis(df_merged)
    test_res = perform_welchs_hypothesis_test(df_merged)
    brand_aff, pack_aff = calculate_purchasing_affinities(df_merged)
    generate_segmentation_plots(metrics, brand_aff, pack_aff)

    print("\n" + "=" * 80)
    print("TASK 1 COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == '__main__':
    main()
