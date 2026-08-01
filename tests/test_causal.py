"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Unit Test Suite - Causal Inference & Data Contracts
"""

import unittest
import pandas as pd
import numpy as np

from quantium_analytics.data_contracts import (
    validate_transaction_schema, validate_customer_schema, DataContractViolation
)


class TestCausalAndDataContracts(unittest.TestCase):

    def setUp(self):
        self.valid_tx = pd.DataFrame({
            'DATE': ['2018-07-01'],
            'STORE_NBR': [1],
            'LYLTY_CARD_NBR': [1000],
            'TXN_ID': [1],
            'PROD_NBR': [10],
            'PROD_NAME': ['Kettle Chips 175g'],
            'PROD_QTY': [2],
            'TOT_SALES': [10.0]
        })

        self.valid_cust = pd.DataFrame({
            'LYLTY_CARD_NBR': [1000],
            'LIFESTAGE': ['YOUNG SINGLES/COUPLES'],
            'PREMIUM_CUSTOMER': ['Mainstream']
        })

    def test_data_contract_success(self):
        self.assertTrue(validate_transaction_schema(self.valid_tx))
        self.assertTrue(validate_customer_schema(self.valid_cust))

    def test_data_contract_negative_sales_failure(self):
        bad_tx = self.valid_tx.copy()
        bad_tx['TOT_SALES'] = [-5.0]
        with self.assertRaises(DataContractViolation):
            validate_transaction_schema(bad_tx)

    def test_data_contract_missing_column_failure(self):
        bad_tx = self.valid_tx.drop(columns=['PROD_QTY'])
        with self.assertRaises(DataContractViolation):
            validate_transaction_schema(bad_tx)


if __name__ == '__main__':
    unittest.main()
