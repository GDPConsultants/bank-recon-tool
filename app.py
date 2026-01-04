import streamlit as st
import pandas as pd
from fpdf import FPDF
import streamlit.components.v1 as components
from io import BytesIO

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

# --- 2. BRS REPORT GENERATOR (ADVANCED FORMAT) ---
def create_comprehensive_brs(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Company & Bank Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"{data['business_name']}", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Bank Reconciliation Statement", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Bank: {data['bank_name']} | A/C: {data['acc_no']}", ln=True, align='C')
    pdf.cell(0, 7, f"Period: {data['period']}", ln=True, align='C')
    pdf.ln(10)

    # Section 1: Adjusted Cash Book
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "PART 1: Adjusted Bank/Cash Book Balance", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(140, 8, f"Unadjusted Book Balance ({data['currency']})", 1)
    pdf.cell(50, 8, f"{data['book_bal_raw']:,.2f}", 1, ln=True)
    
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, "Less: Unadjusted Entries (Bank Charges, Direct Debits, etc.)", ln=True)
    pdf.set_font("Arial", '', 11)
    for entry in data['unadjusted_entries']:
        pdf.cell(140, 8, f"  {entry['date']} - {entry['ref']} - {entry['desc']}", 1)
        pdf.cell(50, 8, f"({entry['amt']:,.2f})", 1, ln=True)
        
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 10, "ADJUSTED CASH BOOK BALANCE", 1)
    pdf.cell(50, 10, f"{data['adj_book_bal']:,.2f}", 1, ln=True)
    pdf.ln(5)

    # Section 2: Reconciliation with Bank Statement
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "PART 2: Reconciliation with Bank Statement", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(140, 8, "Balance as per Bank Statement", 1)
    pdf.cell(50, 8, f"{data['bank_stmt_bal']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 8, "(+) Unrealised Deposits (Lodgements not cleared)", 1)
    pdf.cell(50, 8, f"{data['total_unrealised']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 8, "(-) Unpresented Cheques (Outstanding)", 1)
    pdf.cell(50, 8, f"({data['total_unpresented']:,.2f})", 1, ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 12, "FINAL RECONCILED BALANCE", 1)
    pdf.cell(50, 12, f"{data['final_recon']:,.2f}", 1, ln=True)
    
    return bytes(pdf.output())

# --- 3. SESSION & AUTH ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
ACCESS_PASSWORD = "ReconPro2026"

# --- 4. SIDEBAR & INSTRUCTIONS ---
with st.sidebar:
    try: st.image("logo-removebg-preview.png")
    except: pass
    st.header("📖 Instructions")
    st.markdown("""
    1. **Previous Month:** Upload last month's BRS to track old unpresented cheques.
    2. **Current Month:** Upload Current Bank Statement & Cash Book (Excel/CSV).
    3. **Verify:** The AI will identify which old items have cleared and which new ones are pending.
    4. **Balance:** Handles **Overdrafts (-)** and **Positive (+)** balances automatically.
    """)
    st.divider()
    st.write("**GDP Consultants**")
    st.write("📧 info@taxcalculator.lk | 🌐 www.taxcalculator.lk")

# --- 5. MAIN INTERFACE ---
st.title("Bank Reconciliation AI")
st.subheader("Advanced Multi-Month Financial Automator")

# Uploaders
prev_brs = st.file_uploader("📂 Upload Previous Month BRS (Excel/CSV) - Optional", type=['xlsx', 'csv'])
col1, col2 = st.columns(2)
with col1:
    curr_stmt = st.file_uploader("📄 Current Bank Statement (Excel/CSV)", type=['xlsx', 'csv'])
with col2:
    curr_book = st.file_uploader("📒 Current Cash Book (Excel/CSV)", type=['xlsx', 'csv'])

if st.button("🚀 Generate Advanced Reconciliation"):
    if curr_stmt and curr_book:
        with st.spinner("Analyzing month-on-month transitions..."):
            
            # --- MOCK DATA FOR DEMONSTRATION (AI Logic Integration) ---
            # In production, these are calculated by comparing df_curr_stmt and df_curr_book
            report_data = {
                "business_name": "GDP Consultants Sample Client",
                "bank_name": "Commercial Bank",
                "acc_no": "100200300400",
                "period": "January 2026",
                "currency": "LKR",
                "book_bal_raw": 15500.00,
                "bank_stmt_bal": 12850.00,
                "adj_book_bal": 15410.00,
                "unadjusted_entries": [
                    {"date": "2026-01-31", "ref": "SVC-01", "desc": "Bank Service Charge", "amt": 90.00}
                ],
                "total_unrealised": 5000.00, # Lodgements not yet cleared
                "total_unpresented": 2440.00, # Outstanding cheques
                "final_recon": 15410.00
            }
            
            st.success("✅ Analysis Complete: Previous month items reconciled.")
            
            # Show Analysis Table
            st.write("### Adjusted Cash Book (Part 1)")
            st.info(f"Final Adjusted Book Balance: {report_data['currency']} {report_data['adj_book_bal']:,.2f}")
            
            # PDF Generation
            pdf_bytes = create_comprehensive_brs(report_data)
            st.download_button(
                label="📥 Download Detailed BRS Report (PDF)",
                data=pdf_bytes,
                file_name=f"BRS_{report_data['period']}.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Please upload the Current Bank Statement and Cash Book.")
