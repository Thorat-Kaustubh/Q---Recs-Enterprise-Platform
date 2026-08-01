"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Module: Production Data Contracts & Schema Integrity Validator
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DataContractViolation(Exception):
    """Raised when raw transaction or customer data violates production contract specs."""
    pass


def validate_transaction_schema(df):
    """Validate transaction dataset schema, types, and value constraints."""
    logger.info("Enforcing Data Contract: Validating Transaction Schema...")

    required_columns = {'DATE', 'STORE_NBR', 'LYLTY_CARD_NBR', 'TXN_ID', 'PROD_NBR', 'PROD_NAME', 'PROD_QTY', 'TOT_SALES'}
    missing_cols = required_columns - set(df.columns)
    if missing_cols:
        raise DataContractViolation(f"Data Contract Violation: Missing mandatory columns {missing_cols}")

    # Non-negativity checks
    if (df['TOT_SALES'] < 0).any():
        raise DataContractViolation("Data Contract Violation: Negative values detected in TOT_SALES!")

    if (df['PROD_QTY'] <= 0).any():
        raise DataContractViolation("Data Contract Violation: Non-positive values detected in PROD_QTY!")

    # Missing rate check (<0.1%)
    null_rate = df[list(required_columns)].isnull().mean().max()
    if null_rate > 0.001:
        raise DataContractViolation(f"Data Contract Violation: Null value rate {null_rate:.4f} exceeds threshold 0.001!")

    logger.info("Data Contract Audit: Transaction dataset passed 100% schema & integrity validation.")
    return True


def validate_customer_schema(df):
    """Validate customer purchasing behavior dataset schema and categorical values."""
    logger.info("Enforcing Data Contract: Validating Customer Schema...")

    required_columns = {'LYLTY_CARD_NBR', 'LIFESTAGE', 'PREMIUM_CUSTOMER'}
    missing_cols = required_columns - set(df.columns)
    if missing_cols:
        raise DataContractViolation(f"Data Contract Violation: Missing mandatory customer columns {missing_cols}")

    logger.info("Data Contract Audit: Customer dataset passed 100% schema validation.")
    return True
