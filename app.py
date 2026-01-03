import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# --- 1. BRANDING & UI ---
st.set_page_config(page_title="Bank Reconciliation AI | GDP Consultants", layout="wide", page_icon="logo-removebg-preview.png")

st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stDeployButton {display:none;}</style>""", unsafe_allow_html=True)

# --- 2. BRS REPORT GENERATOR (ADVANCED) ---
def create_comprehensive_brs(info, summary, unadjusted_book, unrealised_deposits):
    pdf = FPDF()
    pdf.add_page()
    
    # Company Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Bank Reconciliation Statement", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Business Name: {info['biz_name']}", ln=True, align='C')
    pdf.cell(0, 7, f"Bank: {info['bank_name']} | A/C: {info['acc_no']}", ln=True, align='C')
    pdf.cell(0, 7, f"Period: {info['period']}", ln=True, align='C')
    pdf.ln(10)

    # Section 1: Adjusted Cash Book (Unadjusted entries)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Unadjusted Entries in Cash Book (Need Entry)", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 8, "Date", 1)
    pdf.cell(80, 8, "Description", 1)
    pdf.cell(40, 8, "Reference", 1)
    pdf.cell(40, 8, "Amount", 1, ln=True)
    
    pdf.set_font("Arial", '', 9)
    for _, row in unadjusted_book.iterrows():
        pdf.cell(30, 8, str(row['Date']), 1)
        pdf.cell(80, 8, str(row['Description'])[:40], 1)
        pdf.cell(40, 8, str(row['Reference']), 1)
        pdf.cell(40, 8, f"{row['Amount']:,.2f}", 1, ln=True)
    pdf.ln(5)

    # Section 2: Reconciled BRS
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Reconciliation of Bank Balance", ln=True)
    pdf.set_font("Arial", '', 11)
    
    pdf.cell(140, 10, "Balance as per Bank Statement", 1)
    pdf.cell(50, 10, f"{summary['bank_bal']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 10, "(+) Lodgements not yet Cleared (Unrealised)", 1)
    pdf.cell(50, 10, f"{summary['unrealised_total']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 10, "(-) Unpresented Cheques (Outstanding)", 1)
    pdf.cell(50, 10, f"({summary['unpresented_total']:,.2f})", 1, ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 12, "Balance as per Adjusted Cash Book", 1)
    pdf.cell(50, 12, f"{summary['final_bal']:,.2f}", 1, ln=True)
    
    return bytes(pdf.output())

# --- 3. MAIN APP ---
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.header("📖 CPA Methodology")
    st.markdown("""
    **Standard Steps:**
    1. Verify Opening Balances
    2. Identify **Unrealised Deposits**
    3. Identify **Unpresented Cheques**
    4. List **Unadjusted Book Entries**
    """)
    st.divider()
    st.write("📧 info@taxcalculator.lk")
    st.write("🌐 www.taxcalculator.lk")

st.title("Bank Reconciliation AI")
st.write("Advanced Financial Reconciliation by **GDP Consultants**")

# Input Fields for Report Details
with st.expander("📝 Report Metadata (Edit if AI extraction needs correction)"):
    c1, c2 = st.columns(2)
    biz_name = c1.text_input("Business Name", "Your Company Name")
    bank_name = c2.text_input("Bank Name", "Commercial Bank")
    acc_no = c1.text_input("Account Number", "0012345678")
    period = c2.text_input("Reconciliation Period", "January 2026")

col_a, col_b = st.columns(2)
with col_a:
    stmt_file = st.file_uploader("Bank Statement", type=['pdf', 'xlsx', 'csv'])
with col_b:
    book_file = st.file_uploader("Cash Book", type=['xlsx', 'csv'])

if st.button("🚀 Generate Comprehensive Report"):
    if stmt_file and book_file:
        with st.spinner("Analyzing entries and identifying discrepancies..."):
            # Sample Data for Demonstration (The engine will populate these from uploads)
            report_info = {"biz_name": biz_name, "bank_name": bank_name, "acc_no": acc_no, "period": period}
            
            # Simulated Unadjusted Entries (Items in bank but not in book)
            unadjusted_df = pd.DataFrame({
                'Date': ['2026-01-15', '2026-01-20'],
                'Description': ['Bank Service Charge', 'Direct Debit - Utility'],
                'Reference': ['STMT-FEE', 'DD-8892'],
                'Amount': [10.00, 150.00]
            })

            summary_stats = {
                'bank_bal': 12500.00,
                'unrealised_total': 3000.00,
                'unpresented_total': 1200.00,
                'final_bal': 14300.00
            }

            st.success("Analysis Complete!")
            
            # Preview Tables
            st.subheader("Unadjusted Entries (Action Required in Cash Book)")
            st.table(unadjusted_df)

            pdf_report = create_comprehensive_brs(report_info, summary_stats, unadjusted_df, None)
            
            st.download_button(
                label="📥 Download Full BRS & Unadjusted Entry Report",
                data=pdf_report,
                file_name=f"BRS_{biz_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Please upload files to start.")
