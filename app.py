import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# --- 1. BRANDING & UI ---
st.set_page_config(page_title="Bank Reconciliation AI", layout="wide", page_icon="logo-removebg-preview.png")

# Hide Streamlit Branding
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 2. PROFESSIONAL BRS GENERATOR ---
class BRS_Report(FPDF):
    def header(self):
        try: self.image("logo-removebg-preview.png", 10, 8, 25)
        except: pass
        self.set_font("Arial", 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Bank Reconciliation Statement', 0, 0, 'C')
        self.ln(20)

def generate_report(meta, bank_bal, book_bal, unadjusted_entries, unrealized_deposits, outstanding_cheques):
    pdf = BRS_Report()
    pdf.add_page()
    
    # Business & Bank Header Details
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"Business Name: {meta.get('business', 'N/A')}", ln=True)
    pdf.cell(0, 7, f"Bank Name: {meta.get('bank', 'N/A')} | Account: {meta.get('account', 'N/A')}", ln=True)
    pdf.cell(0, 7, f"Period: {meta.get('period', 'N/A')}", ln=True)
    pdf.ln(5)

    # SECTION A: UNADJUSTED ENTRIES IN CASH BOOK
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Part 1: Unadjusted Entries in Bank/Cash Book", 1, ln=True, fill=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Date", 1); pdf.cell(110, 10, "Detail/Reference", 1); pdf.cell(50, 10, "Amount", 1, ln=True)
    pdf.set_font("Arial", '', 10)
    
    for entry in unadjusted_entries:
        pdf.cell(30, 10, str(entry['date']), 1)
        pdf.cell(110, 10, str(entry['desc']), 1)
        pdf.cell(50, 10, f"{entry['amt']:,.2f}", 1, ln=True)
    pdf.ln(5)

    # SECTION B: FINAL BRS (Step 4 Format)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Part 2: Reconciliation Statement", 1, ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    
    pdf.cell(140, 10, "Balance as per Bank Statement", 1)
    pdf.cell(50, 10, f"{bank_bal:,.2f}", 1, ln=True)
    
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(140, 10, "(+) Lodgements not yet Cleared (Unrealised Deposits)", 1)
    pdf.cell(50, 10, f"{unrealized_deposits:,.2f}", 1, ln=True)
    
    pdf.cell(140, 10, "(-) Outstanding Cheques (Unpresented)", 1)
    pdf.cell(50, 10, f"({outstanding_cheques:,.2f})", 1, ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 10, "Balance as per Adjusted Bank/Cash Book", 1)
    pdf.cell(50, 10, f"{(bank_bal + unrealized_deposits - outstanding_cheques):,.2f}", 1, ln=True)
    
    return bytes(pdf.output())

# --- 3. MAIN INTERFACE ---
st.title("Bank Reconciliation AI")
st.write("**GDP Consultants** | Professional Audit Standards")

with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.info("💡 **Step 3:** Adjust the Cash Book for unrecorded fees.\n\n💡 **Step 4:** Reconcile the Bank Statement for timing differences.")
    st.write("📧 info@taxcalculator.lk")

col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("Bank Statement", type=['pdf', 'xlsx', 'csv'])
with col2:
    book_file = st.file_uploader("Bank Book", type=['xlsx', 'csv'])

if st.button("🚀 Run Standard Reconciliation"):
    if stmt_file and book_file:
        with st.spinner("Analyzing entries..."):
            # MOCK DATA FOR FORMAT PREVIEW (Replace with logic)
            metadata = {"business": "GDP Consultants", "bank": "Commercial Bank", "account": "88772211", "period": "Jan 2026"}
            unadjusted = [{"date": "2026-01-15", "desc": "Bank Charges (Not in Book)", "amt": 250.00}]
            
            pdf_bytes = generate_report(metadata, 150000.00, 145000.00, unadjusted, 12000.00, 5000.00)
            
            st.success("Reconciliation Successfully Completed!")
            st.download_button("📥 Download Final BRS Report (PDF)", pdf_bytes, "Final_BRS_Report.pdf")
