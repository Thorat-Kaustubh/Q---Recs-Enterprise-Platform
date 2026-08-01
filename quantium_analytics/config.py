"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Module: Config & Environment Parameters
"""

import os

# Base Directories & Data Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

RAW_TXN_CSV = os.path.join(RAW_DATA_DIR, 'QVI_transaction_data.csv')
RAW_TXN_XLSX = os.path.join(RAW_DATA_DIR, 'QVI_transaction_data.xlsx')
RAW_CUST_CSV = os.path.join(RAW_DATA_DIR, 'QVI_purchase_behaviour.csv')
CLEAN_DATA_CSV = os.path.join(PROCESSED_DATA_DIR, 'QVI_data.csv')
PDF_REPORT_PATH = os.path.join(REPORTS_DIR, 'Quantium_Category_Review_Report.pdf')

# Statistical Parameters
ALPHA_SIGNIFICANCE = 0.05
PRE_TRIAL_MONTHS = [201807, 201808, 201809, 201810, 201811, 201812, 201901]
TRIAL_MONTHS = [201902, 201903, 201904]
TRIAL_STORES = [77, 86, 88]

# Critical t-value for df=6 (7 pre-trial months - 1), 95% 2-tailed CI
CRITICAL_T_VALUE = 2.446912

# Brand Standardizing Dictionary
BRAND_MAPPING = {
    'RED': 'RRD',
    'REDS': 'RRD',
    'RED ROCK DELI': 'RRD',
    'NATURAL': 'NCC',
    'NCC': 'NCC',
    'DORITOS': 'DORITOS',
    'DORITO': 'DORITOS',
    'SMITHS': 'SMITHS',
    'SMITH': 'SMITHS',
    'INFUZIONS': 'INFUZIONS',
    'INFZNS': 'INFUZIONS',
    'KETTLE': 'KETTLE',
    'WOOLWORTHS': 'WW',
    'WW': 'WW',
    'GRAIN': 'GRNWVES',
    'GRNWVES': 'GRNWVES',
    'SUNBITES': 'SNBTS',
    'SNBTS': 'SNBTS',
    'CHEZELS': 'CHEEZELS',
    'CHEEZELS': 'CHEEZELS',
    'THINS': 'THINS',
    'PRINGLES': 'PRINGLES',
    'TYRRELLS': 'TYRRELLS',
    'OLD': 'OLD EL PASO',
    'COBS': 'COBS',
    'CCS': 'CCS',
    'TWISTIES': 'TWISTIES',
    'BURGER': 'BURGER',
    'FRENCH': 'FRENCH',
    'TOSTITOS': 'TOSTITOS',
    'CHEETOS': 'CHEETOS'
}
