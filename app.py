import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import streamlit.components.v1 as components

# --- 1. BRANDING & UI CONFIGURATION ---
st.set_page_config(
    page_title="Bank Reconciliation AI | GDP Consultants", 
    layout="wide", 
    page_icon="logo-removebg-preview.png"
)

# Hide Streamlit UI elements
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stDeployButton {display:none;}</style>", unsafe_allow_html=True)

# --- 2. BRS PDF REPORT GENERATOR (Standard Format) ---
class BRS_Report(FPDF):
    def header(self):
        try:
            self.image("logo-removebg-preview.png", 10, 8, 25)
        except:
            pass
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, "Bank Reconciliation Statement (BRS)", ln=True, align='C')
        self.set_font("Arial", 'I', 10)
        self.cell(0, 5, "GDP Consultants | info@taxcalculator.lk", ln=True, align='C')
        self.ln(10)

def create_full_report(biz_name, bank_name, acc_no, period, bank_bal, unpresented, unrealised, unadjusted_items):
    pdf = BRS_Report()
    pdf.add_page()
    
    # Header Details
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 7, f"Business Name: {biz_name}")
    pdf.cell(0, 7, f"Period: {period}", ln=True)
    pdf.cell(100, 7, f"Bank: {bank_name}")
    pdf.cell(0, 7, f"Account No: {acc_no}", ln=True)
    pdf.ln(5)

    # Section A: Bank Statement Reconciliation (Step 4)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(140, 8, "Description", 1, 0, 'C', True)
    pdf.cell(50, 8, "Amount (LKR)", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 8, f"Closing Balance per Bank Statement ({period})", 1)
    pdf.cell(50, 8, f"{bank_bal:,.2f}", 1, 1, 'R')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "Add: Lodgements not yet Cleared (Unrealised Deposits)", 1, 1, 'L', True)
    pdf.set_font("Arial", '', 10)
    for item in unrealised:
        pdf.cell(140, 8, f"  {item['date']} - {item['ref']} ({item['desc']})", 1)
        pdf.cell(50, 8, f"{item['amt']:,.2f}", 1, 1, 'R')

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "Less: Unpresented Cheques", 1, 1, 'L', True)
    pdf.set_font("Arial", '', 10)
    for item in unpresented:
        pdf.cell(140, 8, f"  {item['date']} - {item['ref']} ({item['desc']})", 1)
        pdf.cell(50, 8, f"({item['amt']:,.2f})", 1, 1, 'R')

    # Section B: Not Adjusted Entries in Cash Book (Step 3)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Not Adjusted Entries in Bank/Cash Book", ln=True)
    pdf.set_font("Arial", '', 10)
    for item in unadjusted_items:
        pdf.cell(140, 8, f"  {item['date']} - {item['ref']}: {item['desc']}", 1)
        pdf.cell(50, 8, f"{item['amt']:,.2f}", 1, 1, 'R')

    return bytes(pdf.output())

# --- 3. MAIN APP INTERFACE ---
st.title("Bank Reconciliation AI")
st.write("Professional Automation by **GDP Consultants**")

with st.expander("📝 Reporting Details"):
    c1, c2 = st.columns(2)
    biz_name = c1.text_input("Business Name", "GDP Consultants")
    bank_name = c2.text_input("Bank Name", "Commercial Bank")
    acc_no = c1.text_input("Account Number", "0012345678")
    period = c2.text_input("Reconciliation Period", "December 2025")

col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("Bank Statement (PDF/XLSX/CSV)", type=['pdf', 'xlsx', 'csv'])
with col2:
    book_file = st.file_uploader("Bank/Cash Book (XLSX/CSV)", type=['xlsx', 'csv'])

if st.button("🚀 Run Standard Reconciliation"):
    if stmt_file and book_file:
        # Placeholder Data for Demonstration (Normally parsed from uploaded files)
        unrealised = [{"date": "2025-12-31", "ref": "LODG-900", "desc": "Cash Lodgement", "amt": 9800.00}]
        unpresented = [{"date": "2025-12-27", "ref": "10546", "desc": "J. Quigley", "amt": 830.00}]
        unadjusted = [{"date": "2025-12-31", "ref": "BANK-FEE", "desc": "Monthly Charges", "amt": -180.00}]
        
        pdf_bytes = create_full_report(biz_name, bank_name, acc_no, period, 8253.00, unpresented, unrealised, unadjusted)
        st.download_button("📥 Download Final BRS Report", pdf_bytes, f"BRS_{biz_name}_{period}.pdf")
    else:
        st.error("Please upload both documents.")
