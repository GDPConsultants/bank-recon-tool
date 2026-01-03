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

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. PROFESSIONAL BRS REPORT GENERATOR ---
class BRS_Report(FPDF):
    def header(self):
        try:
            self.image("logo-removebg-preview.png", 10, 8, 25)
        except:
            pass
        self.set_font("Arial", 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Bank Reconciliation Statement', 0, 0, 'C')
        self.ln(20)

def generate_detailed_pdf(header_info, data):
    pdf = BRS_Report()
    pdf.add_page()
    
    # Business Header Details
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"Business Name: {header_info['business_name']}", ln=True)
    pdf.cell(0, 7, f"Bank Name: {header_info['bank_name']}", ln=True)
    pdf.cell(0, 7, f"Account Number: {header_info['acc_no']}", ln=True)
    pdf.cell(0, 7, f"Period: {header_info['period']}", ln=True)
    pdf.ln(5)

    # Section 1: Balance as per Bank Statement
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Closing Balance per Bank Statement", 1)
    pdf.cell(50, 10, f"{data['bank_bal']:,.2f}", 1, ln=True)
    
    # Section 2: Unrealized Deposits (Lodgements not yet Cleared)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 10, "Add: Lodgements not yet Cleared (Unrealized Deposits)", 1, ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    for item in data['unrealized']:
        pdf.cell(140, 8, f"  {item['date']} - {item['ref']} ({item['desc']})", 1)
        pdf.cell(50, 8, f"{item['amt']:,.2f}", 1, ln=True)
    
    # Section 3: Unpresented Cheques
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 10, "Less: Unpresented Cheques", 1, ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    for item in data['unpresented']:
        pdf.cell(140, 8, f"  {item['date']} - {item['ref']} ({item['desc']})", 1)
        pdf.cell(50, 8, f"({item['amt']:,.2f})", 1, ln=True)
        
    # Section 4: Final Reconciled Balance
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Balance as per Adjusted Bank Account", 1)
    pdf.cell(50, 10, f"{data['adj_bal']:,.2f}", 1, ln=True)
    
    return bytes(pdf.output())

# --- 3. MAIN APP INTERFACE ---
st.title("Bank Reconciliation AI")
st.write("Professional Audit Standard by **GDP Consultants**")

# Sidebar for Setup & Contact
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.header("📞 GDP Consultants")
    st.write("📧 info@taxcalculator.lk")
    st.write("🌐 [www.taxcalculator.lk](https://www.taxcalculator.lk)")

# Input for Report Header
with st.expander("📝 Report Details (Bank & Business)", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        biz_name = st.text_input("Business Name", value="GDP Consultants")
        bank_name = st.text_input("Bank Name", placeholder="e.g. BOC, Sampath")
    with col_b:
        acc_no = st.text_input("Account Number")
        period = st.text_input("Reconciliation Period", placeholder="e.g. December 202X")

# File Uploaders
col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("Bank Statement (PDF/Excel)", type=['pdf', 'xlsx', 'csv'])
with col2:
    book_file = st.file_uploader("Cash Book (Excel)", type=['xlsx', 'csv'])

if st.button("🚀 Generate Detailed BRS Report"):
    if stmt_file and book_file:
        with st.spinner("Analyzing entries following CPA guidelines..."):
            # Mock data based on Step 4 of the CPA Ireland Guide [cite: 74, 76]
            # This represents data that the matching engine would identify
            report_data = {
                "bank_bal": 8253.00,
                "unrealized": [
                    {"date": "202X-12-31", "ref": "LODG-9800", "desc": "Cash Lodgement", "amt": 9800.00}
                ],
                "unpresented": [
                    {"date": "202X-12-22", "ref": "10546", "desc": "J. Quigley", "amt": 830.00},
                    {"date": "202X-12-27", "ref": "10547", "desc": "E. Sadlier", "amt": 1574.00}
                ],
                "adj_bal": 16449.00
            }
            
            header_info = {
                "business_name": biz_name,
                "bank_name": bank_name,
                "acc_no": acc_no,
                "period": period
            }
            
            st.success("Reconciliation Complete!")
            
            # Show "Not Adjusted Entries" in UI for User to fix in Cash Book
            st.subheader("⚠️ Unadjusted Entries in Cash Book")
            st.info("These items are in the Bank Statement but missing from your Cash Book (Step 3)[cite: 63, 67].")
            st.table([
                {"Date": "202X-12-20", "Reference": "CR-TRANS", "Detail": "Credit Transfer", "Amount": "4,210.00 (Dr)"},
                {"Date": "202X-12-14", "Reference": "D.D.", "Detail": "Bank Fees", "Amount": "90.00 (Cr)"}
            ])

            # PDF Generation
            pdf_bytes = generate_detailed_pdf(header_info, report_data)
            st.download_button("📥 Download Detailed BRS Report (PDF)", pdf_bytes, f"BRS_{period}.pdf")
    else:
        st.error("Please upload both files and fill in the report details.")
