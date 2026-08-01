"""
Quantium Enterprise Retail Experimentation & Customer Analytics Platform (Q-RECS)
Module: Programmatic C-Suite Intelligence Engine & PDF Report Generator
"""

import os
import logging
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from quantium_analytics.config import PDF_REPORT_PATH, ASSETS_DIR

logger = logging.getLogger(__name__)


def _get_img_path(filename):
    p_asset = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(p_asset):
        return p_asset
    if os.path.exists(filename):
        return filename
    return None


def generate_executive_pdf(output_filename=PDF_REPORT_PATH):
    """Build publication-quality slide-deck PDF report using ReportLab following Minto's Pyramid Principle."""
    logger.info(f"Generating Executive C-Suite PDF Report at '{output_filename}'...")

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch
    )

    styles = getSampleStyleSheet()

    PRIMARY_NAVY = colors.HexColor("#0A2540")
    ACCENT_ORANGE = colors.HexColor("#FF6B00")
    TEXT_DARK = colors.HexColor("#2C3E50")
    BG_LIGHT = colors.HexColor("#F8F9FA")
    CARD_BG = colors.HexColor("#EDF2F7")

    style_title = ParagraphStyle('CoverTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=28, leading=34, textColor=PRIMARY_NAVY, spaceAfter=10)
    style_subtitle = ParagraphStyle('CoverSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=15, leading=20, textColor=ACCENT_ORANGE, spaceAfter=20)
    style_meta = ParagraphStyle('CoverMeta', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=16, textColor=TEXT_DARK)
    style_h1 = ParagraphStyle('H1_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=PRIMARY_NAVY, spaceAfter=12)
    style_h2 = ParagraphStyle('H2_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=ACCENT_ORANGE, spaceAfter=8)
    style_body = ParagraphStyle('Body_Custom', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=TEXT_DARK, spaceAfter=8)
    style_bullet = ParagraphStyle('Bullet_Custom', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=TEXT_DARK, leftIndent=15, firstLineIndent=-10, spaceAfter=6)
    style_callout = ParagraphStyle('Callout_Text', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=15, textColor=PRIMARY_NAVY)
    style_th = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=1)
    style_tc = ParagraphStyle('TC', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=TEXT_DARK)
    style_tcb = ParagraphStyle('TCB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=PRIMARY_NAVY)

    story = []

    # SLIDE 1: COVER
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("QUANTIUM ENTERPRISE RETAIL EXPERIMENTATION PLATFORM", style_subtitle))
    story.append(Paragraph("Category Performance & Store Trial Strategic Review", style_title))
    story.append(HRFlowable(width="100%", thickness=4, color=ACCENT_ORANGE, spaceAfter=25, spaceBefore=5))

    cover_meta_text = """
    <b>Prepared for:</b> Julia, Category Manager (Chips)<br/>
    <b>Prepared by:</b> Quantium Retail Data Science & Behavioral Analytics Team<br/>
    <b>Framework:</b> Barbara Minto's Pyramid Principle Strategic Analysis<br/>
    <b>Status:</b> Production Verified Executive Intelligence<br/>
    """
    story.append(Paragraph(cover_meta_text, style_meta))
    story.append(Spacer(1, 0.4 * inch))

    pyramid_top = """
    <b>EXECUTIVE SUMMARY (THE PYRAMID PRINCIPLE TOP):</b><br/><br/>
    • <b>CORE RECOMMENDATION:</b> Execute full system-wide rollout of trial store shelf layout across all retail locations. Experimental trial evaluation in Stores 77, 86, and 88 demonstrated statistically significant sales increases of up to <b>+72.1%</b> ($t=5.93, p<0.05$), driven primarily by expanding the customer footprint (+70.4% customer expansion).<br/><br/>
    • <b>PRIMARY GROWTH SEGMENT:</b> <i>Young Singles/Couples (Mainstream)</i> represent the largest revenue expansion vector—driving <b>$147.58k</b> in revenue across <b>7,917 customers</b> with the highest unit price willingness ($4.07/unit, Welch's $t=34.84, p < 10^{-200}$).<br/><br/>
    • <b>ASSORTMENT STRATEGY:</b> Position high-affinity premium brands (Kettle, Doritos, Pringles, Tyrrells) and large sharing sizes (270g, 330g, 380g) in prime front-of-store & impulse locations.
    """

    callout_table = Table([[Paragraph(pyramid_top, style_callout)]], colWidths=[10 * inch])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
        ('BOX', (0, 0), (-1, -1), 1.5, PRIMARY_NAVY),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(callout_table)
    story.append(PageBreak())

    # SLIDE 2: SEGMENTATION
    story.append(Paragraph("1. Customer Segmentation & Revenue Drivers", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_NAVY, spaceAfter=12))
    story.append(Paragraph("<b>Key Question:</b> Who buys chips and what drives spending across customer segments?", style_h2))

    seg_data = [
        [Paragraph("Lifestage", style_th), Paragraph("Premium Tier", style_th), Paragraph("Total Sales ($)", style_th), Paragraph("Customers", style_th), Paragraph("Avg Units/Cust", style_th), Paragraph("Avg Price/Unit ($)", style_th), Paragraph("Classification", style_th)],
        [Paragraph("Older Families", style_tcb), Paragraph("Budget", style_tc), Paragraph("$156,863.75", style_tc), Paragraph("4,611", style_tc), Paragraph("9.08", style_tcb), Paragraph("$3.75", style_tc), Paragraph("High Volume Driver", style_tc)],
        [Paragraph("Young Singles/Couples", style_tcb), Paragraph("Mainstream", style_tcb), Paragraph("$147,582.20", style_tcb), Paragraph("7,917", style_tcb), Paragraph("4.58", style_tc), Paragraph("$4.07", style_tcb), Paragraph("Target Growth Segment", style_tcb)],
        [Paragraph("Retirees", style_tc), Paragraph("Mainstream", style_tc), Paragraph("$145,168.95", style_tc), Paragraph("6,358", style_tc), Paragraph("5.93", style_tc), Paragraph("$3.85", style_tc), Paragraph("Core Customer Base", style_tc)],
        [Paragraph("Young Families", style_tc), Paragraph("Budget", style_tc), Paragraph("$129,717.95", style_tc), Paragraph("3,953", style_tc), Paragraph("8.72", style_tc), Paragraph("$3.76", style_tc), Paragraph("Volume Family Base", style_tc)],
        [Paragraph("Older Singles/Couples", style_tc), Paragraph("Budget", style_tc), Paragraph("$127,833.60", style_tc), Paragraph("4,849", style_tc), Paragraph("6.78", style_tc), Paragraph("$3.89", style_tc), Paragraph("Steady Contributor", style_tc)]
    ]

    t_seg = Table(seg_data, colWidths=[1.8 * inch, 1.3 * inch, 1.2 * inch, 1.1 * inch, 1.1 * inch, 1.2 * inch, 1.8 * inch])
    t_seg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#FFF3E0")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_seg)
    story.append(Spacer(1, 10))

    p_sales = _get_img_path('total_sales_by_segment.png')
    p_price = _get_img_path('price_per_unit.png')
    if p_sales and p_price:
        im1 = Image(p_sales, width=4.8 * inch, height=2.4 * inch)
        im2 = Image(p_price, width=4.8 * inch, height=2.4 * inch)
        img_table = Table([[im1, im2]], colWidths=[5.0 * inch, 5.0 * inch])
        img_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(img_table)

    story.append(PageBreak())

    # SLIDE 3: AFFINITY
    story.append(Paragraph("2. Deep Dive: Young Singles/Couples (Mainstream)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_NAVY, spaceAfter=12))
    story.append(Paragraph("<b>Price Sensitivity & Purchasing Affinity:</b> Why do they spend more and what do they buy?", style_h2))

    story.append(Paragraph("• <b>Welch's Hypothesis Test:</b> Mainstream Young Singles/Couples pay a significantly higher unit price ($4.07/unit) compared to Budget & Premium peers ($3.66/unit) — <b>t = 34.84, p &lt; 10^-200</b>.", style_bullet))
    story.append(Paragraph("• <b>Brand Preference Vector:</b> High affinity for premium brands: Tyrrells (1.24x), Twisties (1.22x), Doritos (1.21x), Tostitos (1.21x), Kettle (1.19x), and Pringles (1.18x).", style_bullet))
    story.append(Paragraph("• <b>Pack Size Preference Vector:</b> Strong preference for sharing sizes: 270g (1.27x), 380g (1.26x), 330g (1.22x), and 210g (1.18x). Under-indexing on budget pack sizes.", style_bullet))
    story.append(Spacer(1, 8))

    p_brand = _get_img_path('brand_affinity_young_mainstream.png')
    p_pack = _get_img_path('pack_size_affinity_young_mainstream.png')
    if p_brand and p_pack:
        im_b = Image(p_brand, width=4.8 * inch, height=2.5 * inch)
        im_p = Image(p_pack, width=4.8 * inch, height=2.5 * inch)
        img_table2 = Table([[im_b, im_p]], colWidths=[5.0 * inch, 5.0 * inch])
        img_table2.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(img_table2)

    story.append(PageBreak())

    # SLIDE 4: TRIAL EVALUATION
    story.append(Paragraph("3. Synthetic Control Matching & Trial Evaluation (Stores 77, 86, 88)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_NAVY, spaceAfter=12))
    story.append(Paragraph("<b>Difference-in-Differences (DiD) Causal Impact Analysis:</b> Feb 2019 - Apr 2019", style_h2))

    trial_data = [
        [Paragraph("Trial Store", style_th), Paragraph("Matched Control", style_th), Paragraph("Pre-Trial Match Score", style_th), Paragraph("Sales Growth (%)", style_th), Paragraph("Sales t-stat (95% Sig)", style_th), Paragraph("Customer Growth (%)", style_th), Paragraph("Cust t-stat (95% Sig)", style_th)],
        [Paragraph("Store 77", style_tcb), Paragraph("Store 233", style_tc), Paragraph("98.5%", style_tcb), Paragraph("Mar: +35.9% | Apr: +72.1%", style_tc), Paragraph("t = 5.93 (Yes)", style_tcb), Paragraph("Mar: +28.6% | Apr: +70.4%", style_tc), Paragraph("t = 15.14 (Yes)", style_tcb)],
        [Paragraph("Store 86", style_tcb), Paragraph("Store 155", style_tc), Paragraph("92.5%", style_tcb), Paragraph("Mar: +26.8%", style_tc), Paragraph("t = 6.68 (Yes)", style_tcb), Paragraph("Feb: +13.8% | Mar: +18.3%", style_tc), Paragraph("t = 5.37 (Yes)", style_tcb)],
        [Paragraph("Store 88", style_tcb), Paragraph("Store 237", style_tc), Paragraph("76.7%", style_tcb), Paragraph("Mar: +25.7%", style_tc), Paragraph("t = 3.38 (Yes)", style_tcb), Paragraph("Mar: +15.2%", style_tc), Paragraph("t = 5.36 (Yes)", style_tcb)]
    ]

    t_trial = Table(trial_data, colWidths=[1.1 * inch, 1.2 * inch, 1.3 * inch, 2.0 * inch, 1.4 * inch, 1.8 * inch, 1.2 * inch])
    t_trial.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_trial)
    story.append(Spacer(1, 10))

    p_77 = _get_img_path('trial_store_77_sales.png')
    p_86 = _get_img_path('trial_store_86_sales.png')
    if p_77 and p_86:
        im77 = Image(p_77, width=4.8 * inch, height=2.3 * inch)
        im86 = Image(p_86, width=4.8 * inch, height=2.3 * inch)
        img_table3 = Table([[im77, im86]], colWidths=[5.0 * inch, 5.0 * inch])
        img_table3.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(img_table3)

    story.append(PageBreak())

    # SLIDE 5: RECOMMENDATIONS
    story.append(Paragraph("4. Strategic Recommendations & Rollout Roadmap", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_NAVY, spaceAfter=12))
    story.append(Paragraph("<b>Actionable Strategy for Category Manager Julia:</b>", style_h2))

    rec_text = """
    <b>1. FULL SYSTEM-WIDE ROLLOUT OF TRIAL LAYOUT:</b><br/>
    • <b>Action:</b> Expand the experimental trial store shelf layout across all store locations in the network.<br/>
    • <b>Financial Rationale:</b> Empirically proven to drive statistically significant sales increases of up to <b>+72.1%</b>, driven by higher customer foot traffic.<br/><br/>

    <b>2. OPTIMIZE ASSORTMENT FOR MAINSTREAM YOUNG SINGLES/COUPLES:</b><br/>
    • <b>Action:</b> Allocate premium shelf space to Kettle, Doritos, Pringles, Tyrrells, and 270g+ sharing sizes.<br/>
    • <b>Placement Strategy:</b> Feature in high-visibility front-of-store endcaps and near beverage displays.<br/><br/>

    <b>3. PROTECT VOLUME DRIVERS FOR OLDER FAMILIES (BUDGET):</b><br/>
    • <b>Action:</b> Maintain family multi-packs to preserve high volume purchasing (~9.08 units/customer).
    """

    rec_table = Table([[Paragraph(rec_text, style_body)]], colWidths=[10 * inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1.5, ACCENT_ORANGE),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(rec_table)

    doc.build(story)
    logger.info(f"Successfully compiled executive PDF report at '{output_filename}'.")
    return output_filename
