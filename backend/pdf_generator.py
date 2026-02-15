from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from schemas import InvoiceRequest, InvoiceTotals


def _money(value) -> str:
    return f"₹ {value:,.2f}"


def build_invoice_pdf(payload: InvoiceRequest, totals: InvoiceTotals) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>{payload.business_name}</b>", styles["Title"]))
    story.append(Paragraph(payload.business_address, styles["BodyText"]))
    story.append(Paragraph(f"GSTIN: {payload.business_gst_number}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    invoice_meta = Table(
        [
            ["Invoice Number", payload.invoice_number, "Date", payload.invoice_date.strftime("%d-%m-%Y")],
            ["Customer", payload.customer_name, "Phone", payload.customer_phone],
        ],
        colWidths=[35 * mm, 55 * mm, 20 * mm, 55 * mm],
    )
    invoice_meta.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(invoice_meta)
    story.append(Spacer(1, 14))

    items_table = Table(
        [
            ["Item", "Qty", "Unit Price", "GST %", "Line Total"],
            [
                payload.item_name,
                f"{payload.quantity}",
                _money(float(payload.unit_price)),
                f"{payload.gst_rate}%",
                _money(float(totals.subtotal)),
            ],
        ],
        colWidths=[72 * mm, 20 * mm, 30 * mm, 20 * mm, 30 * mm],
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 12))

    half_gst = totals.gst_amount / 2
    summary = Table(
        [
            ["Subtotal", _money(float(totals.subtotal))],
            [f"CGST ({payload.gst_rate / 2:.1f}%)", _money(float(half_gst))],
            [f"SGST ({payload.gst_rate / 2:.1f}%)", _money(float(half_gst))],
            ["Total", _money(float(totals.total))],
        ],
        colWidths=[55 * mm, 32 * mm],
        hAlign="RIGHT",
    )
    summary.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary)
    story.append(Spacer(1, 25))

    story.append(Paragraph("Signature: ________________________", styles["BodyText"]))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
