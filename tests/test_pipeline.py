"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Unit Test Suite
"""

import unittest
import pandas as pd
import numpy as np

from quantium_analytics.config import BRAND_MAPPING
from quantium_analytics.segmentation import perform_welchs_hypothesis_test


class TestQuantiumPipeline(unittest.TestCase):

    def setUp(self):
        # Create synthetic test dataset
        self.test_df = pd.DataFrame({
            'LYLTY_CARD_NBR': [1001, 1002, 1003, 1004, 1005],
            'LIFESTAGE': ['YOUNG SINGLES/COUPLES'] * 5,
            'PREMIUM_CUSTOMER': ['Mainstream', 'Mainstream', 'Budget', 'Premium', 'Budget'],
            'TOT_SALES': [10.0, 12.0, 7.0, 8.0, 7.5],
            'PROD_QTY': [2, 2, 2, 2, 2],
            'BRAND': ['KETTLE', 'DORITOS', 'SMITHS', 'RRD', 'WW'],
            'PACK_SIZE': [175.0, 170.0, 175.0, 150.0, 175.0]
        })

    def test_brand_mapping_keys(self):
        self.assertIn('RED', BRAND_MAPPING)
        self.assertEqual(BRAND_MAPPING['RED'], 'RRD')
        self.assertEqual(BRAND_MAPPING['KETTLE'], 'KETTLE')

    def test_welchs_hypothesis_test(self):
        res = perform_welchs_hypothesis_test(self.test_df)
        self.assertIn('t_stat', res)
        self.assertIn('p_value', res)
        self.assertGreater(res['mean_target'], res['mean_peer'])


if __name__ == '__main__':
    unittest.main()
