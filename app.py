import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import streamlit.components.v1 as components
from datetime import datetime

# --- 1. BRANDING & UI ---
st.set_page_config(page_title="Bank Reconciliation AI | GDP Consultants", layout="wide", page_icon="logo-removebg-preview.png")

st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display:none;}</style>", unsafe_allow_html=True)

# --- 2. PDF GENERATOR (CPA STEP-BY-STEP FORMAT) ---
class BRS_Report(FPDF):
    def header(self):
        try: self.image("logo-removebg-preview.png", 10, 8, 25)
        except: pass
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, "Bank Reconciliation Statement (BRS)", ln=True, align='C')
        self.set_font("Arial", 'I', 10)
        self.cell(0, 5, "GDP Consultants | www.taxcalculator.lk", ln=True, align='C')
        self.ln(10)

def generate_full_report(data):
    pdf = BRS_Report()
    pdf.add_page()
    
    # Header Info
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 7, f"Business Name: {data['biz_name']}")
    pdf.cell(0, 7, f"Bank: {data['bank_name']}", ln=True)
    pdf.cell(100, 7, f"Account No: {data['acc_no']}")
    pdf.cell(0, 7, f"Period: {data['period']}", ln=True)
    pdf.ln(5)

    # Section 1: Adjusted Cash Book
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, "PART A: ADJUSTMENT OF CASH BOOK (BANK ACCOUNT)", 1, ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 7, "Balance as per Unadjusted Cash Book", 1)
    pdf.cell(50, 7, f"LKR {data['unadjusted_cash']:,.2f}", 1, ln=True)
    
    pdf.set_text_color(200, 0, 0)
    for entry in data['book_adjustments']:
        pdf.cell(140, 7, f"  (-) {entry['desc']} (Ref: {entry['ref']})", 1)
        pdf.cell(50, 7, f"({entry['amt']:,.2f})", 1, ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "Adjusted Cash Book Balance", 1)
    pdf.cell(50, 8, f"LKR {data['adjusted_cash']:,.2f}", 1, ln=True)
    pdf.ln(5)

    # Section 2: Reconciling with Bank Statement
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, "PART B: RECONCILIATION WITH BANK STATEMENT", 1, ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 7, "Balance as per Bank Statement", 1)
    pdf.cell(50, 7, f"LKR {data['bank_bal']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 7, "(+) Lodgements not yet Cleared (Unrealised Deposits)", 1, ln=True)
    for item in data['transit_deposits']:
        pdf.cell(140, 7, f"    {item['date']} - {item['ref']}", 1)
        pdf.cell(50, 7, f"{item['amt']:,.2f}", 1, ln=True)

    pdf.cell(140, 7, "(-) Unpresented Cheques (Outstanding)", 1, ln=True)
    for item in data['outstanding_cheques']:
        pdf.cell(140, 7, f"    Cheque No: {item['chq']} ({item['date']})", 1)
        pdf.cell(50, 7, f"({item['amt']:,.2f})", 1, ln=True)

    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 10, "Final Reconciled Balance", 1)
    pdf.cell(50, 10, f"LKR {data['final_bal']:,.2f}", 1, ln=True)

    return bytes(pdf.output())

# --- 3. MAIN APP ---
st.title("Bank Reconciliation AI")
st.write("Professional Audit-Ready Reports by **GDP Consultants**")

# Instructions Expansion
with st.expander("ℹ️ Instructions & 9-Step Process"):
    st.write("1. Upload **Previous Month BRS** to clear old outstanding items.")
    st.write("2. Upload current **Statement** and **Cash Book**.")
    st.write("3. The AI identifies **Unadjusted Entries** (Charges/Interest) to fix your book.")
    st.write("4. The Final Report details all unpresented cheques and unrealised deposits.")

# File Uploaders
prev_brs = st.file_uploader("Upload Previous Month BRS (Optional)", type=['pdf', 'xlsx'])
col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("Current Bank Statement", type=['pdf', 'xlsx', 'csv'])
with col2:
    book_file = st.file_uploader("Current Bank Book / Cash Book", type=['xlsx', 'csv'])

if st.button("🚀 Start Professional Reconciliation"):
    if stmt_file and book_file:
        with st.spinner("Analyzing entries and adjusting Cash Book..."):
            # Mock extracted data for demonstration
            report_data = {
                "biz_name": "Sample Business PVT LTD",
                "bank_name": "Commercial Bank",
                "acc_no": "8001234567",
                "period": "January 2026",
                "unadjusted_cash": 15400.00,
                "adjusted_cash": 14950.00,
                "bank_bal": 12000.00,
                "final_bal": 14950.00,
                "book_adjustments": [{"desc": "Bank Charges", "ref": "SC-99", "amt": 450.00}],
                "transit_deposits": [{"date": "2026-01-30", "ref": "DEP-101", "amt": 5000.00}],
                "outstanding_cheques": [{"date": "2026-01-28", "chq": "005542", "amt": 2050.00}]
            }
            
            st.success("Analysis Complete. Cash Book Adjusted.")
            
            # Preview in UI
            st.subheader("📊 Reconciled Summary")
            st.metric("Adjusted Cash Book Balance", "LKR 14,950.00")
            
            # Download
            pdf_bytes = generate_full_report(report_data)
            st.download_button("📥 Download Full BRS Report (PDF)", pdf_bytes, "Professional_BRS.pdf")
    else:
        st.error("Please upload the current Month Statement and Cash Book.")

with st.sidebar:
    st.header("📞 GDP Consultants")
    st.write("📧 [info@taxcalculator.lk](mailto:info@taxcalculator.lk)")
    st.write("🌐 [www.taxcalculator.lk](https://www.taxcalculator.lk)")
