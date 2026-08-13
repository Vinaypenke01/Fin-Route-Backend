"""
route_email_report_service.py — Service to generate multi-sheet XML SpreadsheetML (.xls)
reports and send automated daily route closure emails with file attachments to guest users.
"""

import os
import re
import logging
from datetime import datetime, date as dt_date, timedelta
from django.conf import settings
from django.db.models import Sum, Count
from django.core.mail import EmailMessage

from apps.guest_workspace.models import (
    GuestWorkspace,
    CollectionLine,
    CustomerProfile,
    CollectionEntry,
    CapitalEntry,
    Expense,
)

logger = logging.getLogger(__name__)


def escape_xml(text) -> str:
    if text is None:
        return ""
    s = str(text)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


class RouteEmailReportService:

    @staticmethod
    def generate_excel_workbook(workspace: GuestWorkspace, line: CollectionLine, target_date: dt_date = None) -> tuple[str, str]:
        """
        Generates native XML SpreadsheetML (.xls) content for the given line up to target_date.
        Returns tuple of (filename, xml_content_string).
        """
        if not target_date:
            target_date = dt_date.today()

        today_str = target_date.isoformat()

        # 1. Query line customers & collections
        customers_qs = CustomerProfile.objects.filter(workspace=workspace)
        if line:
            customers_qs = customers_qs.filter(line=line)
        customers = list(customers_qs.order_by("sequence_number", "id"))

        collections_qs = CollectionEntry.objects.filter(workspace=workspace, collection_date__lte=target_date)
        if line:
            collections_qs = collections_qs.filter(customer__line=line)
        collections = list(collections_qs.select_related("customer"))

        # Map customer collections
        customer_col_map = {}
        date_set = set()

        for c in collections:
            c_id = c.customer_id
            if c_id not in customer_col_map:
                customer_col_map[c_id] = []
            customer_col_map[c_id].append(c)

            d_str = c.collection_date.isoformat() if c.collection_date else ""
            if d_str and d_str <= today_str:
                date_set.add(d_str)

        for cust in customers:
            if cust.start_date and cust.start_date.isoformat() <= today_str:
                curr = cust.start_date
                while curr <= target_date:
                    date_set.add(curr.isoformat())
                    curr += timedelta(days=7)

        date_headers = sorted(list(date_set))
        if not date_headers:
            date_headers = [today_str]

        # Line Name & Area
        line_name_str = line.name if line else "All Lines"
        line_area_str = f" ({line.area})" if (line and line.area) else ""
        full_line_title = f"{line_name_str}{line_area_str}"

        # 2. Sheet 1: Borrower Payment Ledger
        sheet1_title = f"BORROWER PAYMENT LEDGER — {full_line_title.upper()}"
        sheet1_base_headers = [
            "Customer Code", "Customer Name", "Phone", "Line / Route", "Day", "Status",
            "Loan Amount (Rs)", "Disbursed Amount (Rs)", "Total Installments",
            "Installment Amount (Rs)", "Disbursed Date", "First Installment Date",
            "Total Paid (Rs)", "Installments Paid", "Outstanding Balance (Rs)",
        ]
        sheet1_headers = sheet1_base_headers + date_headers

        sheet1_rows = []
        daily_col_totals = {d: 0.0 for d in date_headers}

        for cust in customers:
            c_cols = customer_col_map.get(cust.id, [])
            c_paid_dates = {}
            for col in c_cols:
                d_str = col.collection_date.isoformat() if col.collection_date else ""
                if d_str:
                    c_paid_dates[d_str] = float(col.collected_amount or 0)

            cust_start_str = cust.start_date.isoformat() if cust.start_date else ""

            row_data = [
                cust.customer_code or "",
                cust.full_name or "",
                cust.mobile_number or "",
                line_name_str,
                (cust.collection_day or "monday").capitalize(),
                (cust.status or "active").capitalize(),
                float(cust.loan_amount or 0),
                float(cust.disbursed_amount or cust.loan_amount or 0),
                cust.total_installments or 20,
                float(cust.installment_amount or 0),
                cust.start_date.isoformat() if cust.start_date else "",
                cust.start_date.isoformat() if cust.start_date else "",
                float(cust.total_paid or 0),
                cust.installments_paid_count or 0,
                float(cust.outstanding_balance or 0),
            ]

            # Date cells
            for d in date_headers:
                if d in c_paid_dates:
                    amt = c_paid_dates[d]
                    row_data.append(amt)
                    daily_col_totals[d] += amt
                elif cust_start_str and d < cust_start_str:
                    row_data.append("-")
                else:
                    row_data.append(0.0)

            sheet1_rows.append(row_data)

        sheet1_total_row = ["TOTAL DAILY COLLECTIONS"] + [""] * (len(sheet1_base_headers) - 1) + [daily_col_totals[d] for d in date_headers]

        # 3. Sheet 2: Daily Cash Flow Summary
        sheet2_title = f"DAILY CASH FLOW SUMMARY — {full_line_title.upper()}"
        sheet2_headers = [
            "Date", "Starting / Opening Amount (Rs)", "Collected Amount (Rs)",
            "Newly Given Loan Amount (Rs)", "Expenses (Rs)", "Final Value / Closing Cash (Rs)"
        ]

        sheet2_rows = []
        tot_starting = 0.0
        tot_collected = 0.0
        tot_disbursed = 0.0
        tot_expenses = 0.0
        tot_final = 0.0

        for d in date_headers:
            try:
                curr_date = datetime.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                curr_date = target_date

            # Collections on d
            c_qs = CollectionEntry.objects.filter(workspace=workspace, collection_date=curr_date)
            if line:
                c_qs = c_qs.filter(customer__line=line)
            c_tot = float(c_qs.aggregate(t=Sum("collected_amount"))["t"] or 0)

            # Starting Capital on d
            cap_tot = float(CapitalEntry.objects.filter(workspace=workspace, entry_date=curr_date).aggregate(t=Sum("amount"))["t"] or 0)

            # Disbursements on d
            d_qs = CustomerProfile.objects.filter(workspace=workspace, start_date=curr_date)
            if line:
                d_qs = d_qs.filter(line=line)
            disb_tot = float(d_qs.aggregate(t=Sum("disbursed_amount"))["t"] or 0)

            # Expenses on d
            exp_tot = float(Expense.objects.filter(workspace=workspace, expense_date=curr_date).aggregate(t=Sum("amount"))["t"] or 0)

            closing_cash = (cap_tot + c_tot) - (disb_tot + exp_tot)

            sheet2_rows.append([d, cap_tot, c_tot, disb_tot, exp_tot, closing_cash])
            tot_starting += cap_tot
            tot_collected += c_tot
            tot_disbursed += disb_tot
            tot_expenses += exp_tot
            tot_final += closing_cash

        sheet2_total_row = ["TOTAL SUM", tot_starting, tot_collected, tot_disbursed, tot_expenses, tot_final]

        # Helper to render XML cells
        def build_xml_row(cells, style="Default"):
            cell_xmls = []
            for val in cells:
                if isinstance(val, (int, float)):
                    cell_xmls.append(f'<Cell ss:StyleID="{style}Number"><Data ss:Type="Number">{val}</Data></Cell>')
                elif val == "-":
                    cell_xmls.append(f'<Cell ss:StyleID="{style}"><Data ss:Type="String">-</Data></Cell>')
                else:
                    cell_xmls.append(f'<Cell ss:StyleID="{style}"><Data ss:Type="String">{escape_xml(val)}</Data></Cell>')
            return f'<Row>{"".join(cell_xmls)}</Row>'

        xml_content = f"""<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
 <Styles>
  <Style ss:ID="Default" ss:Name="Normal">
   <Alignment ss:Vertical="Bottom"/>
   <Font ss:FontName="Calibri" x:Family="Swiss" ss:Size="11" ss:Color="#000000"/>
  </Style>
  <Style ss:ID="Title">
   <Font ss:FontName="Calibri" ss:Size="14" ss:Bold="1" ss:Color="#047857"/>
  </Style>
  <Style ss:ID="Header">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#FFFFFF"/>
   <Interior ss:Color="#059669" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="HeaderNumber">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#FFFFFF"/>
   <Interior ss:Color="#059669" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="#,##0.00"/>
  </Style>
  <Style ss:ID="Total">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#065F46"/>
   <Interior ss:Color="#ECFDF5" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="TotalNumber">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#065F46"/>
   <Interior ss:Color="#ECFDF5" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="#,##0.00"/>
  </Style>
  <Style ss:ID="DefaultNumber">
   <NumberFormat ss:Format="#,##0.00"/>
  </Style>
 </Styles>

 <Worksheet ss:Name="Borrower Payment Ledger">
  <Table>
   <Row><Cell ss:StyleID="Title"><Data ss:Type="String">{escape_xml(sheet1_title)}</Data></Cell></Row>
   <Row/>
   {build_xml_row(sheet1_headers, "Header")}
   {"\n   ".join(build_xml_row(r) for r in sheet1_rows)}
   {build_xml_row(sheet1_total_row, "Total")}
  </Table>
 </Worksheet>

 <Worksheet ss:Name="Daily Cash Flow Summary">
  <Table>
   <Row><Cell ss:StyleID="Title"><Data ss:Type="String">{escape_xml(sheet2_title)}</Data></Cell></Row>
   <Row/>
   {build_xml_row(sheet2_headers, "Header")}
   {"\n   ".join(build_xml_row(r) for r in sheet2_rows)}
   {build_xml_row(sheet2_total_row, "Total")}
  </Table>
 </Worksheet>
</Workbook>"""

        # Generate Filename: line name (location)_first date_to_last date.xls
        first_date = date_headers[0] if date_headers else today_str
        last_date = date_headers[-1] if date_headers else today_str
        raw_name = f"{full_line_title}_{first_date}_to_{last_date}"
        clean_filename = re.sub(r'[/\\?%*:|"<>]', "_", raw_name).strip() + ".xls"

        return clean_filename, xml_content

    @classmethod
    def send_route_email(cls, workspace: GuestWorkspace, line: CollectionLine, target_date: dt_date = None, recipient_email: str = None) -> bool:
        """
        Generates the Excel report and sends an HTML closure email with the file attached.
        """
        if not target_date:
            target_date = dt_date.today()

        if not recipient_email:
            recipient_email = getattr(workspace.owner, "email", None) or workspace.owner_email
        if not recipient_email and hasattr(workspace.owner, "username") and "@" in workspace.owner.username:
            recipient_email = workspace.owner.username

        if not recipient_email:
            logger.warning("No valid recipient email address found for workspace %s", workspace.name)
            return False

        line_name_str = line.name if line else "All Route Lines"
        filename, xml_content = cls.generate_excel_workbook(workspace, line, target_date)

        # 1. Query Collections
        collections_qs = CollectionEntry.objects.filter(workspace=workspace, collection_date=target_date).select_related("customer")
        if line:
            collections_qs = collections_qs.filter(customer__line=line)

        paid_entries = collections_qs.filter(collected_amount__gt=0).exclude(status_code="skipped")
        skipped_entries = collections_qs.filter(status_code="skipped")

        # 2. Query line customers for unpaid borrower breakdown
        line_customers_qs = CustomerProfile.objects.filter(workspace=workspace).select_related("line")
        if line:
            line_customers_qs = line_customers_qs.filter(line=line)

        paid_customer_ids = set(paid_entries.values_list("customer_id", flat=True))
        logged_skipped_ids = set(skipped_entries.values_list("customer_id", flat=True))
        unpaid_customers = line_customers_qs.exclude(id__in=paid_customer_ids | logged_skipped_ids)

        # 3. Aggregates
        col_tot = float(paid_entries.aggregate(total=Sum("collected_amount"))["total"] or 0)
        cap_tot = float(CapitalEntry.objects.filter(workspace=workspace, entry_date=target_date).aggregate(total=Sum("amount"))["total"] or 0)

        disbursements_qs = CustomerProfile.objects.filter(workspace=workspace, start_date=target_date)
        if line:
            disbursements_qs = disbursements_qs.filter(line=line)
        disb_tot = float(disbursements_qs.aggregate(total=Sum("disbursed_amount"))["total"] or 0)

        exp_tot = float(Expense.objects.filter(workspace=workspace, expense_date=target_date).aggregate(total=Sum("amount"))["total"] or 0)
        net_cash = (col_tot + cap_tot) - (disb_tot + exp_tot)

        subject = f"FinRoute Evening Collection Ledger: {line_name_str} ({target_date.strftime('%d %b %Y')})"

        # Build Paid Rows
        paid_rows_html = ""
        for p in paid_entries:
            c = p.customer
            c_name = c.full_name if c else (p.customer_name or "N/A")
            c_code = c.customer_code if c else (p.customer_code or "")
            paid_rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px 12px; font-weight: 700; color: #1e293b;">{c_name} <span style="font-size: 11px; font-weight: normal; color: #64748b;">({c_code})</span></td>
              <td style="padding: 10px 12px; font-family: monospace; font-weight: 800; color: #059669; text-align: right;">+₹{float(p.collected_amount):,.2f}</td>
              <td style="padding: 10px 12px; text-align: center;"><span style="background: #ecfdf5; color: #047857; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">Paid</span></td>
            </tr>
            """
        if not paid_rows_html:
            paid_rows_html = """<tr><td colspan="3" style="padding: 12px; text-align: center; color: #94a3b8; font-size: 12px;">No payment receipts recorded for this route today.</td></tr>"""

        # Build Skipped & Unpaid Rows
        skipped_rows_html = ""
        for s in skipped_entries:
            c = s.customer
            c_name = c.full_name if c else (s.customer_name or "N/A")
            c_code = c.customer_code if c else (s.customer_code or "")
            skipped_rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px 12px; font-weight: 700; color: #1e293b;">{c_name} <span style="font-size: 11px; font-weight: normal; color: #64748b;">({c_code})</span></td>
              <td style="padding: 10px 12px; font-family: monospace; font-weight: 700; color: #e11d48; text-align: right;">Skipped</td>
              <td style="padding: 10px 12px; text-align: center;"><span style="background: #fff1f2; color: #e11d48; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">Skipped</span></td>
            </tr>
            """
        for u in unpaid_customers:
            skipped_rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px 12px; font-weight: 700; color: #1e293b;">{u.full_name} <span style="font-size: 11px; font-weight: normal; color: #64748b;">({u.customer_code})</span></td>
              <td style="padding: 10px 12px; font-family: monospace; font-weight: 700; color: #d97706; text-align: right;">₹{float(u.installment_amount or u.loan_amount or 0):,.2f}</td>
              <td style="padding: 10px 12px; text-align: center;"><span style="background: #fef3c7; color: #b45309; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">Unpaid</span></td>
            </tr>
            """
        if not skipped_rows_html:
            skipped_rows_html = """<tr><td colspan="3" style="padding: 12px; text-align: center; color: #059669; font-size: 12px;">🎉 100% Collection Completed! All borrowers paid today.</td></tr>"""

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; color: #1e293b; margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #059669 0%, #047857 100%); padding: 28px 24px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }}
            .header p {{ margin: 6px 0 0 0; opacity: 0.9; font-size: 13px; }}
            .body {{ padding: 24px; }}
            .badge {{ display: inline-block; background: #ecfdf5; color: #047857; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px; border: 1px solid #a7f3d0; margin-bottom: 20px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; text-align: left; }}
            .card-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 4px; }}
            .card-val {{ font-size: 20px; font-weight: 800; font-family: monospace; margin: 0; }}
            .green {{ color: #059669; }}
            .blue {{ color: #2563eb; }}
            .purple {{ color: #7c3aed; }}
            .rose {{ color: #e11d48; }}
            .section-header {{ font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #334155; margin: 24px 0 10px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }}
            .table-container {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; margin-bottom: 16px; font-size: 13px; }}
            .table-container th {{ background: #f1f5f9; padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; }}
            .summary-box {{ background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 14px; padding: 20px; margin-top: 20px; }}
            .summary-title {{ font-size: 12px; font-weight: 800; text-transform: uppercase; color: #065f46; }}
            .summary-val {{ font-size: 26px; font-weight: 900; color: #047857; font-family: monospace; margin-top: 4px; }}
            .attachment-banner {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 12px 16px; font-size: 12px; color: #1e40af; margin-bottom: 16px; font-weight: 600; }}
            .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>📊 FinRoute Daily Route Evening Ledger</h1>
              <p>{workspace.name} • {line_name_str}</p>
            </div>
            <div class="body">
              <div style="text-align: center;">
                <span class="badge">📅 Route Date: {target_date.strftime('%d %B %Y')}</span>
              </div>

              <div class="attachment-banner">
                📎 Attached File: <b>{filename}</b> (Multi-Sheet Excel Borrower Payment Ledger & Cash Flow Summary)
              </div>

              <!-- 4-PILLAR RECONCILIATION CARDS -->
              <table width="100%" style="border-collapse: separate; border-spacing: 8px;">
                <tr>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">📥 Collections ({paid_entries.count()} Paid)</div>
                      <div class="card-val green">₹{col_tot:,.2f}</div>
                    </div>
                  </td>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">💵 Starting Cash</div>
                      <div class="card-val blue">₹{cap_tot:,.2f}</div>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">📤 Disbursed ({disbursements_qs.count()} New Loans)</div>
                      <div class="card-val purple">₹{disb_tot:,.2f}</div>
                    </div>
                  </td>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">💸 Expenses</div>
                      <div class="card-val rose">₹{exp_tot:,.2f}</div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- NET CASH SUMMARY BOX -->
              <div class="summary-box">
                <div class="summary-title">💰 Final Closing Handheld Cash</div>
                <div style="font-size: 11px; color: #047857; margin-top: 2px;">(Starting Cash + Collections) − (Disbursements + Expenses)</div>
                <div class="summary-val">₹{net_cash:,.2f}</div>
              </div>

              <!-- 1. PAID BORROWERS LIST -->
              <div class="section-header" style="color: #059669;">📥 Paid Customers ({paid_entries.count()})</div>
              <table class="table-container">
                <thead>
                  <tr>
                    <th>Borrower Name & Code</th>
                    <th style="text-align: right;">Amount Paid</th>
                    <th style="text-align: center;">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {paid_rows_html}
                </tbody>
              </table>

              <!-- 2. SKIPPED & UNPAID BORROWERS LIST -->
              <div class="section-header" style="color: #e11d48;">🔴 Skipped / Unpaid Customers ({skipped_entries.count() + unpaid_customers.count()})</div>
              <table class="table-container">
                <thead>
                  <tr>
                    <th>Borrower Name & Code</th>
                    <th style="text-align: right;">Installment Due</th>
                    <th style="text-align: center;">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {skipped_rows_html}
                </tbody>
              </table>

            </div>
            <div class="footer">
              Automated Evening Route Ledger generated by <b>FinRoute Platform</b>.<br/>
              © 2026 FinRoute Finance Systems.
            </div>
          </div>
        </body>
        </html>
        """

        # Dispatch Email with Excel Attachment
        try:
            email = EmailMessage(
                subject=subject,
                body=html_body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FinRoute Reports <info@fin-route.site>'),
                to=[recipient_email],
            )
            email.content_subtype = "html"
            email.attach(filename, xml_content.encode("utf-8"), "application/vnd.ms-excel")
            email.send(fail_silently=False)
            logger.info("✅ SUCCESS: Evening route email sent to %s for line %s with attachment %s", recipient_email, line_name_str, filename)
            return True
        except Exception as err:
            logger.error("❌ ERROR sending route email to %s: %s", recipient_email, err, exc_info=True)
            return False
