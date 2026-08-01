"""
Quantium Retail Strategy and Analytics: Strategic Executive Presentation Report & PDF Generator
Task 3 Script - Powered by Quantium Enterprise Analytics Platform (Q-RECS)
"""

from quantium_analytics.reporting import generate_executive_pdf


def build_pdf_report(filename="Quantium_Category_Review_Report.pdf"):
    print("=" * 80)
    print("GENERATING QUANTIUM STRATEGIC CATEGORY REVIEW PDF REPORT (TASK 3)")
    print("=" * 80)
    generate_executive_pdf(filename)


if __name__ == '__main__':
    build_pdf_report()
