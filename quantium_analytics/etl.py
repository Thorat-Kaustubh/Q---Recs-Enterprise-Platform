"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Module: Production ETL & Data Pipeline Engine
"""

import os
import re
import logging
import pandas as pd
import numpy as np

from quantium_analytics.config import (
    RAW_TXN_CSV, RAW_TXN_XLSX, RAW_CUST_CSV, CLEAN_DATA_CSV, BRAND_MAPPING
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_raw_data():
    """Load raw transaction and customer dataset with fallback handling and data contract auditing."""
    if os.path.exists(RAW_TXN_CSV):
        logger.info(f"Ingesting transaction data from '{RAW_TXN_CSV}'...")
        df_tx = pd.read_csv(RAW_TXN_CSV)
    elif os.path.exists(RAW_TXN_XLSX):
        logger.info(f"Ingesting transaction data from '{RAW_TXN_XLSX}'...")
        df_tx = pd.read_excel(RAW_TXN_XLSX)
    else:
        raise FileNotFoundError("Raw transaction dataset not found!")

    logger.info(f"Ingesting customer behavior dataset from '{RAW_CUST_CSV}'...")
    df_cust = pd.read_csv(RAW_CUST_CSV)

    # Data Contract Schema Auditing
    from quantium_analytics.data_contracts import validate_transaction_schema, validate_customer_schema
    validate_transaction_schema(df_tx)
    validate_customer_schema(df_cust)

    logger.info(f"Raw Transactions Shape: {df_tx.shape} | Raw Customers Shape: {df_cust.shape}")
    return df_tx, df_cust


def clean_transactions(df_tx):
    """Perform data hygiene, date parsing, category filtering, and outlier isolation."""
    logger.info("Executing Transaction Data Hygiene & Cleaning...")

    # Date Parsing (Excel integer date offset handling)
    if np.issubdtype(df_tx['DATE'].dtype, np.number):
        df_tx['DATE_CLEAN'] = pd.to_datetime(df_tx['DATE'], origin='1899-12-30', unit='D')
    else:
        df_tx['DATE_CLEAN'] = pd.to_datetime(df_tx['DATE'])

    # Category Hygiene: Remove non-chip Salsa products
    salsa_mask = df_tx['PROD_NAME'].str.lower().str.contains('salsa')
    salsa_count = salsa_mask.sum()
    logger.info(f"Category Hygiene: Excluded {salsa_count} non-chip Salsa transactions.")
    df_chips = df_tx[~salsa_mask].copy()

    # Outlier Isolation: Commercial bulk purchasing (QTY >= 200)
    outliers = df_chips[df_chips['PROD_QTY'] >= 200]
    if not outliers.empty:
        outlier_cards = outliers['LYLTY_CARD_NBR'].unique()
        logger.warning(f"Anomaly Isolation: Excluding {len(outliers)} commercial outlier transactions for Card(s): {list(outlier_cards)}")
        df_chips = df_chips[~df_chips['LYLTY_CARD_NBR'].isin(outlier_cards)].copy()

    return df_chips


def extract_features(df_chips):
    """Extract Grammage (Pack Size) and Standardized Brand Features."""
    logger.info("Executing Feature Engineering Engine...")

    # Pack Size Extraction (grams)
    df_chips['PACK_SIZE'] = df_chips['PROD_NAME'].str.extract(r'(\d+)g', flags=re.IGNORECASE)[0].astype(float)

    # Standardized Brand Parsing
    def parse_brand(prod_name):
        first_word = prod_name.split()[0].upper()
        return BRAND_MAPPING.get(first_word, first_word)

    df_chips['BRAND'] = df_chips['PROD_NAME'].apply(parse_brand)
    logger.info(f"Extracted {df_chips['BRAND'].nunique()} standardized brands & {df_chips['PACK_SIZE'].nunique()} pack sizes.")
    return df_chips


def execute_etl_pipeline():
    """End-to-end execution of production ETL pipeline."""
    logger.info("Starting Quantium Production ETL Pipeline...")
    df_tx, df_cust = load_raw_data()
    df_chips = clean_transactions(df_tx)
    df_chips = extract_features(df_chips)

    # Left merge on Loyalty Card Number
    df_merged = pd.merge(df_chips, df_cust, on='LYLTY_CARD_NBR', how='left')
    logger.info(f"ETL Complete. Output Dataset Shape: {df_merged.shape}")

    df_merged.to_csv(CLEAN_DATA_CSV, index=False)
    logger.info(f"Persisted cleaned analytical dataset to '{CLEAN_DATA_CSV}'.")
    return df_merged


if __name__ == '__main__':
    execute_etl_pipeline()
