"""
PDF cost report generator using ReportLab.
Produces a professional A4 summary suitable for sharing with banks
and housing programmes.
"""
import io
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

_GREEN = colors.HexColor('#2D6A4F')
_LIGHT_GREEN = colors.HexColor('#D8F3DC')
_GREY = colors.HexColor('#6B7280')
_WHITE = colors.white
_BLACK = colors.black


def _header_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'Header', parent=styles['Title'],
        textColor=_GREEN, fontSize=20, spaceAfter=4,
    )


def _subheader_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'SubHeader', parent=styles['Heading2'],
        textColor=_GREEN, fontSize=13, spaceBefore=12, spaceAfter=4,
    )


def _body_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'Body', parent=styles['Normal'],
        textColor=_BLACK, fontSize=9, leading=14,
    )


def _disclaimer_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        'Disclaimer', parent=styles['Normal'],
        textColor=_GREY, fontSize=8, leading=11,
    )


def _table_style(header_bg=None):
    bg = header_bg or _GREEN
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), _WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [_WHITE, _LIGHT_GREEN]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ])


def generate_report(layout, estimate: dict, tco: dict) -> bytes:
    """
    Build and return a PDF as bytes.

    Args:
        layout: Layout model instance
        estimate: dict from cost_calculator.calculate_cost()
        tco:      dict from tco_calculator.project_tco()
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title='EcoChain Cost Report',
    )

    h = _header_style()
    sh = _subheader_style()
    body = _body_style()
    disc = _disclaimer_style()

    story = []

    # ── Title block ──────────────────────────────────────────────────────────
    story.append(Paragraph('EcoChain Build Cost Report', h))
    story.append(Paragraph(f'Generated: {date.today().strftime("%d %B %Y")}', disc))
    story.append(HRFlowable(width='100%', thickness=1, color=_GREEN, spaceAfter=10))

    # ── Project Overview ─────────────────────────────────────────────────────
    story.append(Paragraph('Project Overview', sh))
    overview_data = [
        ['Layout ID', str(layout.id)],
        ['Bedrooms', str(layout.bedrooms)],
        ['Build Style', layout.style.capitalize()],
        ['Climate Zone', layout.climate_zone.replace('_', ' ').title()],
        ['Orientation', layout.orientation.capitalize()],
        ['Total Floor Area', f'{layout.total_area_sqm:.1f} m²'],
        ['Eco Score', f'{layout.eco_score} / 100'],
        ['Country', estimate.get('country', '—')],
    ]
    t = Table(overview_data, colWidths=[5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [_WHITE, _LIGHT_GREEN]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    # ── Upfront Construction Cost ────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph('Upfront Construction Cost', sh))

    currency = estimate.get('currency', 'USD')
    breakdown = estimate.get('breakdown', [])
    total_cost = float(estimate.get('total_cost', 0) or 0)
    cost_data = [['Category', 'Item', 'Qty', 'Unit Cost', f'Total ({currency})']]
    for item in breakdown:
        cost_data.append([
            item.get('category', '').capitalize(),
            item.get('description', ''),
            f'{float(item.get("quantity", 0)):.1f}',
            f'{float(item.get("unit_cost", 0)):,.2f}',
            f'{float(item.get("total", 0)):,.2f}',
        ])
    cost_data.append(['', '', '', 'TOTAL', f'{total_cost:,.2f}'])

    t = Table(cost_data, colWidths=[2.5 * cm, 6 * cm, 1.8 * cm, 2.5 * cm, 3.2 * cm])
    ts = _table_style()
    ts.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    ts.add('BACKGROUND', (0, -1), (-1, -1), _LIGHT_GREEN)
    t.setStyle(ts)
    story.append(t)

    if estimate.get('disclaimer'):
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f'* {estimate["disclaimer"]}', disc))

    # ── 5-Year Operational Savings ───────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    years = tco.get('projection_years', 5)
    story.append(Paragraph(f'{years}-Year Operational Savings', sh))

    savings_data = [['Saving Category', 'Annual Saving (USD)', 'Notes']]
    for item in tco.get('savings_breakdown', []):
        savings_data.append([
            item.get('category', '').capitalize(),
            f'{float(item.get("annual_saving", 0)):,.2f}',
            item.get('description', ''),
        ])
    savings_data.append([
        f'TOTAL OVER {years} YEARS',
        f'{float(tco.get("total_savings", 0) or 0):,.2f}',
        f'Payback in {tco.get("payback_months", "—")} months',
    ])

    t = Table(savings_data, colWidths=[3.5 * cm, 4 * cm, 8.5 * cm])
    ts = _table_style(header_bg=colors.HexColor('#1B4332'))
    ts.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    ts.add('BACKGROUND', (0, -1), (-1, -1), _LIGHT_GREEN)
    t.setStyle(ts)
    story.append(t)

    # ── TCO Summary ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph('Total Cost of Ownership Summary', sh))
    upfront = float(tco.get('upfront_cost', 0) or 0)
    total_sav = float(tco.get('total_savings', 0) or 0)
    eco_net = upfront - total_sav
    conv_cost = upfront * 1.10  # conventional is ~10% cheaper upfront
    summary_data = [
        ['', 'Upfront Cost (USD)', f'{years}-Yr Savings (USD)', f'Net Cost after {years} Yrs (USD)'],
        ['Conventional Build', f'{conv_cost:,.2f}', '0.00', f'{conv_cost:,.2f}'],
        ['EcoChain Build', f'{upfront:,.2f}', f'{total_sav:,.2f}', f'{eco_net:,.2f}'],
    ]
    t = Table(summary_data, colWidths=[3.5 * cm, 4 * cm, 4 * cm, 4.5 * cm])
    ts = _table_style()
    ts.add('TEXTCOLOR', (0, 2), (-1, 2), _GREEN)
    ts.add('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold')
    t.setStyle(ts)
    story.append(t)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=_GREY))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        'This report was generated by EcoChain. Prices are indicative and based on '
        'current market data at time of generation. Labour rates may vary by contractor. '
        'Operational savings projections are modelled estimates; actual savings depend on '
        'occupancy, local tariffs, and construction quality.',
        disc,
    ))
    story.append(Paragraph('© EcoChain · eco-chain.io', disc))

    doc.build(story)
    return buffer.getvalue()
