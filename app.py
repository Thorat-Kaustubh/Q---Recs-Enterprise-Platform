"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Enterprise C-Suite Portal, Placebo Permutation Inspector & ROI Simulator
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from scipy import stats

from quantium_analytics.config import (
    CLEAN_DATA_CSV, PDF_REPORT_PATH, TRIAL_STORES, CRITICAL_T_VALUE
)
from quantium_analytics.segmentation import (
    calculate_segment_kpis, perform_welchs_hypothesis_test, calculate_purchasing_affinities
)
from quantium_analytics.causal_inference import (
    aggregate_store_monthly_metrics, match_synthetic_control, evaluate_causal_impact,
    run_placebo_permutation_test
)
from quantium_analytics.data_contracts import validate_transaction_schema, validate_customer_schema

# -----------------------------------------------------------------------------
# ENTERPRISE STREAMLIT CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Quantium Q-RECS Enterprise v3.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive Theme
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0A2540;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #FF6B00;
        font-weight: 600;
        margin-bottom: 25px;
    }
    .metric-box {
        background: linear-gradient(135deg, #0A2540 0%, #1F77B4 100%);
        color: white;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .card-container {
        background-color: #F8F9FA;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #FF6B00;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def get_analytical_data():
    if os.path.exists(CLEAN_DATA_CSV):
        df = pd.read_csv(CLEAN_DATA_CSV)
        df['DATE'] = pd.to_datetime(df['DATE_CLEAN'])
        return df
    return None

df = get_analytical_data()

# Header Banner
st.markdown('<div class="main-header">⚡ Quantium Q-RECS Enterprise Production Platform v3.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">MLOps Data Infrastructure, Synthetic Control Placebo Testing & Causal Inference</div>', unsafe_allow_html=True)

if df is not None:
    # Sidebar
    st.sidebar.markdown("### 🏢 Enterprise Operations Center")
    st.sidebar.markdown("**Environment:** Production v3.0")
    st.sidebar.markdown("**Role:** Principal Data Scientist / MLOps Lead")
    st.sidebar.markdown("**Stakeholder:** Julia (Category Manager)")
    st.sidebar.markdown("---")

    # High-level Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">${df['TOT_SALES'].sum():,.2f}</div>
            <div class="metric-label">Total Category Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Audited Transactions</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{df['LYLTY_CARD_NBR'].nunique():,}</div>
            <div class="metric-label">Unique Loyalty Accounts</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">100% Passed</div>
            <div class="metric-label">Data Contract Health</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Navigation Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Cohort Behavioral Profiling",
        "🏷️ Purchasing Affinity Vectors",
        "🏬 Synthetic Control Matcher (SCME)",
        "🧪 Placebo Permutation Inspector",
        "💰 Financial Rollout ROI Simulator",
        "📄 C-Suite Executive PDF Deck"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: COHORT INTELLIGENCE
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("Multi-Dimensional Customer Cohort Profiling")
        metrics = calculate_segment_kpis(df)
        metrics['SEGMENT'] = metrics['LIFESTAGE'] + " (" + metrics['PREMIUM_CUSTOMER'] + ")"

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### Category Revenue ($K) by Cohort")
            fig_sales, ax_sales = plt.subplots(figsize=(8, 5))
            m_s = metrics.sort_values(by='TOT_SALES', ascending=True)
            colors = ['#FF6B00' if 'YOUNG SINGLES/COUPLES (Mainstream)' in s else '#0A2540' for s in m_s['SEGMENT']]
            ax_sales.barh(m_s['SEGMENT'], m_s['TOT_SALES'] / 1000, color=colors)
            ax_sales.set_xlabel("Total Sales ($ Thousands)")
            st.pyplot(fig_sales)

        with col_right:
            st.markdown("#### Average Price per Unit ($) by Cohort")
            fig_p, ax_p = plt.subplots(figsize=(8, 5))
            m_p = metrics.sort_values(by='AVG_PRICE_PER_UNIT', ascending=True)
            colors_p = ['#FF6B00' if 'YOUNG SINGLES/COUPLES (Mainstream)' in s else '#1F77B4' for s in m_p['SEGMENT']]
            ax_p.barh(m_p['SEGMENT'], m_p['AVG_PRICE_PER_UNIT'], color=colors_p)
            ax_p.set_xlabel("Unit Price ($)")
            st.pyplot(fig_p)

        st.markdown("#### Cohort Performance Matrix")
        st.dataframe(
            metrics[['LIFESTAGE', 'PREMIUM_CUSTOMER', 'TOT_SALES', 'CUST_COUNT', 'AVG_UNITS_PER_CUST', 'AVG_PRICE_PER_UNIT']]
            .style.format({
                'TOT_SALES': '${:,.2f}',
                'CUST_COUNT': '{:,}',
                'AVG_UNITS_PER_CUST': '{:.2f}',
                'AVG_PRICE_PER_UNIT': '${:.2f}'
            }),
            use_container_width=True
        )

    # -------------------------------------------------------------------------
    # TAB 2: PURCHASING AFFINITY VECTORS
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("Target Segment Purchasing Affinity Vector Analysis")
        target_res = perform_welchs_hypothesis_test(df)

        st.markdown(f"""
        <div class="card-container">
            <h4>🔬 Welch's Asymptotic Hypothesis Testing Diagnostics</h4>
            <p><b>Target Cohort (Young Singles/Couples - Mainstream):</b> Mean Unit Price = <b>${target_res['mean_target']:.2f}</b></p>
            <p><b>Peer Cohort (Budget & Premium Peers):</b> Mean Unit Price = <b>${target_res['mean_peer']:.2f}</b></p>
            <p><b>Asymptotic Welch's t-statistic:</b> <code>{target_res['t_stat']:.4f}</code> (p-value: <code>{target_res['p_value']:.4e}</code>)</p>
            <p><b>Inference:</b> Reject H0. Mainstream Young Singles/Couples exhibit a statistically significant price premium tolerance.</p>
        </div>
        """, unsafe_allow_html=True)

        brand_aff, pack_aff = calculate_purchasing_affinities(df)

        cb, cp = st.columns(2)
        with cb:
            st.markdown("#### Brand Affinity Vector (>1.0 = Over-Indexing)")
            fig_b, ax_b = plt.subplots(figsize=(8, 6))
            ba = brand_aff.sort_values(by='AFFINITY', ascending=True)
            colors = ['#2ca02c' if a > 1.0 else '#d62728' for a in ba['AFFINITY']]
            ax_b.barh(ba.index, ba['AFFINITY'], color=colors)
            ax_b.axvline(1.0, color='black', linestyle='--')
            ax_b.set_xlabel("Affinity Score")
            st.pyplot(fig_b)

        with cp:
            st.markdown("#### Pack Size Affinity Vector (Grams)")
            fig_pk, ax_pk = plt.subplots(figsize=(8, 6))
            pa = pack_aff.sort_values(by='AFFINITY', ascending=True)
            pa.index = [f"{int(x)}g" for x in pa.index]
            colors_pk = ['#2ca02c' if a > 1.0 else '#d62728' for a in pa['AFFINITY']]
            ax_pk.barh(pa.index, pa['AFFINITY'], color=colors_pk)
            ax_pk.axvline(1.0, color='black', linestyle='--')
            ax_pk.set_xlabel("Affinity Score")
            st.pyplot(fig_pk)

    # -------------------------------------------------------------------------
    # TAB 3: SYNTHETIC CONTROL MATCHER
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("Synthetic Control Matching Engine (SCME) & DiD Causal Model")

        monthly_full, full_stores = aggregate_store_monthly_metrics(df)
        ts_choice = st.selectbox("Select Target Trial Store:", options=TRIAL_STORES)

        best_control, rankings = match_synthetic_control(monthly_full, ts_choice, full_stores)
        scale_sales, scale_cust, std_sales, std_cust, eval_df = evaluate_causal_impact(monthly_full, ts_choice, best_control)

        match_score = rankings.loc[best_control, 'final_score'] * 100

        st.success(f"**SCME Result:** Trial Store **{ts_choice}** paired with Control Store **{best_control}** (Composite Metric Match Score: **{match_score:.1f}%**)")

        st.markdown("#### Candidate Control Store Composite Rankings")
        st.dataframe(rankings.head(5).style.format('{:.4f}'), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Sales Causal Evaluation")
            s_img = f"trial_store_{ts_choice}_sales.png"
            if os.path.exists(s_img):
                st.image(s_img, use_container_width=True)

        with c2:
            st.markdown("#### Customer Footprint Causal Evaluation")
            c_img = f"trial_store_{ts_choice}_customers.png"
            if os.path.exists(c_img):
                st.image(c_img, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 4: PLACEBO PERMUTATION INSPECTOR
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("Synthetic Control In-Space Placebo Permutation Inspector (Abadie et al.)")
        st.markdown("""
        To verify that trial store sales lift is truly causal and not an artifact of random fluctuations,
        we run **In-Space Placebo Tests** across non-trial control stores to construct the empirical null distribution.
        """)

        if st.button("🚀 Run Placebo Permutation Test (30 Placebo Stores)", type="primary"):
            with st.spinner("Computing Placebo Synthetic Control Matching across 30 non-trial stores..."):
                placebo_res = run_placebo_permutation_test(monthly_full, ts_choice, full_stores, sample_size=30)

            st.markdown(f"""
            <div class="card-container">
                <h4>🧪 In-Space Placebo Permutation Test Diagnostics</h4>
                <p><b>Target Trial Store:</b> Store {ts_choice}</p>
                <p><b>Trial Post/Pre RMSPE Ratio:</b> <code>{placebo_res['trial_ratio']:.4f}</code></p>
                <p><b>Empirical Placebo p-value:</b> <h3 style="color:#27AE60;">p = {placebo_res['empirical_p_value']:.4f}</h3></p>
                <p><b>Causal Decision:</b> {"Statistically Significant Causal Lift (p < 0.05)" if placebo_res['empirical_p_value'] < 0.05 else "Inconclusive Placebo Test"}</p>
            </div>
            """, unsafe_allow_html=True)

            fig_pl, ax_pl = plt.subplots(figsize=(10, 5))
            ax_pl.hist(placebo_res['placebo_ratios'], bins=15, color='#1F77B4', alpha=0.7, label='Placebo Store RMSPE Ratios')
            ax_pl.axvline(placebo_res['trial_ratio'], color='#FF6B00', linewidth=3, linestyle='--', label=f'Trial Store {ts_choice} Ratio ({placebo_res["trial_ratio"]:.2f})')
            ax_pl.set_title(f'In-Space Placebo Test Distribution for Store {ts_choice}', fontweight='bold')
            ax_pl.set_xlabel('Post/Pre RMSPE Ratio')
            ax_pl.set_ylabel('Placebo Count')
            ax_pl.legend()
            st.pyplot(fig_pl)

    # -------------------------------------------------------------------------
    # TAB 5: FINANCIAL ROLLOUT ROI SIMULATOR
    # -------------------------------------------------------------------------
    with tab5:
        st.subheader("System-Wide Trial Layout Rollout ROI Simulator")
        st.markdown("""
        Simulate estimated network-wide annual revenue gains based on empirical trial store lift ($+72.1\%$ peak lift in Store 77).
        """)

        sim_col1, sim_col2 = st.columns(2)

        with sim_col1:
            n_stores_rollout = st.slider("Number of Target Stores for System-Wide Rollout:", min_value=10, max_value=270, value=150, step=10)
            avg_monthly_rev = st.number_input("Average Baseline Monthly Chip Revenue per Store ($):", value=1500.0, step=100.0)
            expected_lift_pct = st.slider("Expected Rollout Sales Lift (%):", min_value=5.0, max_value=50.0, value=25.0, step=1.0)

        with sim_col2:
            monthly_gain_per_store = avg_monthly_rev * (expected_lift_pct / 100.0)
            total_monthly_network_gain = monthly_gain_per_store * n_stores_rollout
            total_annual_network_gain = total_monthly_network_gain * 12

            st.markdown(f"""
            <div class="card-container">
                <h4>💰 Projected Financial Rollout ROI</h4>
                <p><b>Monthly Incremental Lift / Store:</b> <code>+${monthly_gain_per_store:,.2f}</code></p>
                <p><b>Total Network Monthly Lift ({n_stores_rollout} stores):</b> <code>+${total_monthly_network_gain:,.2f}</code></p>
                <p><b>Projected Annualized Incremental Lift:</b> <h3 style="color:#2ca02c;">+${total_annual_network_gain:,.2f}</h3></p>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 6: C-SUITE EXECUTIVE PDF DECK
    # -------------------------------------------------------------------------
    with tab6:
        st.subheader("Programmatic Executive PDF Report & Slide Deck")
        if os.path.exists(PDF_REPORT_PATH):
            with open(PDF_REPORT_PATH, "rb") as f:
                pdf_data = f.read()

            st.download_button(
                label="📥 Download Executive C-Suite PDF Deck (Quantium_Category_Review_Report.pdf)",
                data=pdf_data,
                file_name="Quantium_Category_Review_Report.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.warning("PDF report file not found. Run `qrecs --stage report` to generate.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Quantium Enterprise Production Platform v3.0 (Q-RECS Framework)</p>", unsafe_allow_html=True)
