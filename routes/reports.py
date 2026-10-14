import io
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from models import db, Sale, SaleItem, Expense, Product, Customer, Debt
from utils.decorators import require_permission

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _parse_range():
    today = datetime.utcnow().date()
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    start = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else today - timedelta(days=29)
    end = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else today
    return start, end


def _pdf_header(business, title, start, end):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=16, spaceAfter=2)
    sub_style = ParagraphStyle("SubStyle", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
    elements = [
        Paragraph(business.name, title_style),
        Paragraph(f"{title} &nbsp;|&nbsp; {start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')}", sub_style),
        Spacer(1, 12),
    ]
    return elements


def _styled_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


@reports_bp.route("/")
@login_required
@require_permission("reports")
def index():
    start, end = _parse_range()
    return render_template("reports.html", date_from=start.isoformat(), date_to=end.isoformat())


@reports_bp.route("/sales/pdf")
@login_required
@require_permission("reports")
def sales_pdf():
    business = current_user.business
    start, end = _parse_range()
    sales = Sale.query.filter(
        Sale.business_id == business.id,
        db.func.date(Sale.created_at) >= start,
        db.func.date(Sale.created_at) <= end,
    ).order_by(Sale.created_at).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    elements = _pdf_header(business, "Sales Report", start, end)

    data = [["Receipt", "Date", "Customer", "Payment", "Total", "Paid", "Balance"]]
    total_sum = paid_sum = balance_sum = 0
    for s in sales:
        data.append([
            s.receipt_number, s.created_at.strftime("%d %b %Y"),
            s.customer.name if s.customer else "Walk-in",
            s.payment_method.capitalize(),
            f"{s.total_amount:,.2f}", f"{s.amount_paid:,.2f}", f"{s.balance:,.2f}",
        ])
        total_sum += s.total_amount
        paid_sum += s.amount_paid
        balance_sum += s.balance
    data.append(["", "", "", "TOTAL", f"{total_sum:,.2f}", f"{paid_sum:,.2f}", f"{balance_sum:,.2f}"])

    elements.append(_styled_table(data))
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"sales_report_{start}_{end}.pdf")


@reports_bp.route("/sales/excel")
@login_required
@require_permission("reports")
def sales_excel():
    business = current_user.business
    start, end = _parse_range()
    sales = Sale.query.filter(
        Sale.business_id == business.id,
        db.func.date(Sale.created_at) >= start,
        db.func.date(Sale.created_at) <= end,
    ).order_by(Sale.created_at).all()

    rows = [{
        "Receipt": s.receipt_number,
        "Date": s.created_at.strftime("%Y-%m-%d %H:%M"),
        "Customer": s.customer.name if s.customer else "Walk-in",
        "Payment Method": s.payment_method,
        "Subtotal": s.subtotal,
        "Discount": s.discount,
        "Total": s.total_amount,
        "Paid": s.amount_paid,
        "Balance": s.balance,
        "Profit": s.profit,
    } for s in sales]

    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sales")
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"sales_report_{start}_{end}.xlsx",
                      mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@reports_bp.route("/profit/pdf")
@login_required
@require_permission("reports")
def profit_pdf():
    business = current_user.business
    start, end = _parse_range()

    sales = Sale.query.filter(
        Sale.business_id == business.id,
        db.func.date(Sale.created_at) >= start,
        db.func.date(Sale.created_at) <= end,
    ).all()
    expenses = Expense.query.filter(
        Expense.business_id == business.id, Expense.expense_date >= start, Expense.expense_date <= end
    ).all()

    total_revenue = sum(s.total_amount for s in sales)
    total_cogs = sum(item.unit_cost * item.quantity for s in sales for item in s.items)
    gross_profit = total_revenue - total_cogs
    total_expenses = sum(e.amount for e in expenses)
    net_profit = gross_profit - total_expenses

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    elements = _pdf_header(business, "Profit & Loss Summary", start, end)

    data = [
        ["Metric", "Amount"],
        ["Total Revenue", f"{total_revenue:,.2f}"],
        ["Cost of Goods Sold", f"{total_cogs:,.2f}"],
        ["Gross Profit", f"{gross_profit:,.2f}"],
        ["Total Expenses", f"{total_expenses:,.2f}"],
        ["Net Profit", f"{net_profit:,.2f}"],
    ]
    elements.append(_styled_table(data, col_widths=[300, 150]))

    if expenses:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Expense Breakdown", getSampleStyleSheet()["Heading3"]))
        by_cat = {}
        for e in expenses:
            by_cat[e.category] = by_cat.get(e.category, 0) + e.amount
        cat_data = [["Category", "Amount"]] + [[k, f"{v:,.2f}"] for k, v in sorted(by_cat.items(), key=lambda x: -x[1])]
        elements.append(_styled_table(cat_data, col_widths=[300, 150]))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"profit_report_{start}_{end}.pdf")


@reports_bp.route("/inventory/pdf")
@login_required
@require_permission("reports")
def inventory_pdf():
    business = current_user.business
    products = Product.query.filter_by(business_id=business.id, status="active").order_by(Product.name).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    today = datetime.utcnow().date()
    elements = _pdf_header(business, "Inventory Report", today, today)

    data = [["Product", "Category", "Stock", "Buying Price", "Selling Price", "Stock Value"]]
    total_value = 0
    for p in products:
        data.append([
            p.name, p.category.name if p.category else "—", str(p.current_stock),
            f"{p.buying_price:,.2f}", f"{p.selling_price:,.2f}", f"{p.stock_value:,.2f}",
        ])
        total_value += p.stock_value
    data.append(["", "", "", "", "TOTAL", f"{total_value:,.2f}"])

    elements.append(_styled_table(data))
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"inventory_report_{today}.pdf")


@reports_bp.route("/inventory/excel")
@login_required
@require_permission("reports")
def inventory_excel():
    business = current_user.business
    products = Product.query.filter_by(business_id=business.id, status="active").order_by(Product.name).all()

    rows = [{
        "Product": p.name,
        "SKU": p.sku,
        "Category": p.category.name if p.category else "",
        "Current Stock": p.current_stock,
        "Minimum Level": p.minimum_stock_level,
        "Buying Price": p.buying_price,
        "Selling Price": p.selling_price,
        "Stock Value": p.stock_value,
        "Low Stock": "Yes" if p.is_low_stock else "No",
    } for p in products]

    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")
    buffer.seek(0)
    today = datetime.utcnow().date()
    return send_file(buffer, as_attachment=True, download_name=f"inventory_report_{today}.xlsx",
                      mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@reports_bp.route("/expenses/pdf")
@login_required
@require_permission("reports")
def expenses_pdf():
    business = current_user.business
    start, end = _parse_range()
    expenses = Expense.query.filter(
        Expense.business_id == business.id, Expense.expense_date >= start, Expense.expense_date <= end
    ).order_by(Expense.expense_date).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    elements = _pdf_header(business, "Expenses Report", start, end)

    data = [["Date", "Category", "Description", "Payee", "Method", "Amount"]]
    total = 0
    for e in expenses:
        data.append([
            e.expense_date.strftime("%d %b %Y"), e.category, e.description or "—",
            e.payee or "—", e.payment_method.capitalize(), f"{e.amount:,.2f}",
        ])
        total += e.amount
    data.append(["", "", "", "", "TOTAL", f"{total:,.2f}"])

    elements.append(_styled_table(data))
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"expenses_report_{start}_{end}.pdf")


@reports_bp.route("/debts/pdf")
@login_required
@require_permission("reports")
def debts_pdf():
    business = current_user.business
    debts = Debt.query.filter_by(business_id=business.id, status="open").order_by(Debt.created_at).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    today = datetime.utcnow().date()
    elements = _pdf_header(business, "Outstanding Debts Report", today, today)

    data = [["Customer", "Phone", "Date", "Original", "Balance"]]
    total = 0
    for d in debts:
        data.append([
            d.customer.name, d.customer.phone or "—", d.created_at.strftime("%d %b %Y"),
            f"{d.original_amount:,.2f}", f"{d.balance:,.2f}",
        ])
        total += d.balance
    data.append(["", "", "", "TOTAL", f"{total:,.2f}"])

    elements.append(_styled_table(data))
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"debts_report_{today}.pdf")
