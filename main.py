"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Production CLI & Pipeline Orchestrator
"""

import argparse
import logging
import time

from quantium_analytics.etl import execute_etl_pipeline
from quantium_analytics.segmentation import (
    calculate_segment_kpis, perform_welchs_hypothesis_test,
    calculate_purchasing_affinities, generate_segmentation_plots
)
from quantium_analytics.causal_inference import (
    aggregate_store_monthly_metrics, match_synthetic_control,
    evaluate_causal_impact, generate_causal_plots
)
from quantium_analytics.config import CLEAN_DATA_CSV
from quantium_analytics.reporting import generate_executive_pdf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger('Q-RECS-CLI')


def run_etl():
    logger.info("=== STAGE 1: INGESTION & ETL PIPELINE ===")
    return execute_etl_pipeline()


def run_segmentation(df=None):
    logger.info("=== STAGE 2: BEHAVIORAL COHORTING & HYPOTHESIS TESTING ===")
    if df is None:
        import pandas as pd
        df = pd.read_csv(CLEAN_DATA_CSV)

    metrics = calculate_segment_kpis(df)
    test_res = perform_welchs_hypothesis_test(df)
    brand_aff, pack_aff = calculate_purchasing_affinities(df)
    generate_segmentation_plots(metrics, brand_aff, pack_aff)
    return metrics, test_res, brand_aff, pack_aff


def run_inference(df=None):
    logger.info("=== STAGE 3: SYNTHETIC CONTROL MATCHING & CAUSAL INFERENCE ===")
    if df is None:
        import pandas as pd
        df = pd.read_csv(CLEAN_DATA_CSV)
        df['DATE'] = pd.to_datetime(df['DATE_CLEAN'])

    monthly_full, full_stores = aggregate_store_monthly_metrics(df)

    trial_stores = [77, 86, 88]
    eval_results = {}

    for ts in trial_stores:
        best_control, rankings = match_synthetic_control(monthly_full, ts, full_stores)
        scale_sales, scale_cust, std_sales, std_cust, eval_df = evaluate_causal_impact(monthly_full, ts, best_control)
        generate_causal_plots(monthly_full, ts, best_control, scale_sales, scale_cust, std_sales, std_cust)
        eval_results[ts] = {'control': best_control, 'eval_df': eval_df}

    return eval_results


def run_reporting():
    logger.info("=== STAGE 4: C-SUITE INTELLIGENCE PDF REPORTING ===")
    return generate_executive_pdf()


def main():
    parser = argparse.ArgumentParser(description="Quantium Enterprise Retail Analytics Platform CLI (Q-RECS)")
    parser.add_argument('--stage', choices=['etl', 'segment', 'infer', 'report'], help="Execute specific pipeline stage")
    parser.add_argument('--pipeline', choices=['all'], help="Execute full end-to-end analytics pipeline")

    args = parser.parse_args()

    start_time = time.time()

    if args.stage == 'etl':
        run_etl()
    elif args.stage == 'segment':
        run_segmentation()
    elif args.stage == 'infer':
        run_inference()
    elif args.stage == 'report':
        run_reporting()
    else:
        # Default or --pipeline all
        logger.info("Executing End-to-End Enterprise Analytics Pipeline...")
        df = run_etl()
        run_segmentation(df)
        run_inference(df)
        run_reporting()

    elapsed = time.time() - start_time
    logger.info(f"Execution completed successfully in {elapsed:.2f} seconds.")


if __name__ == '__main__':
    main()
