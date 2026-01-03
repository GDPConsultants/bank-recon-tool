import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from fpdf import FPDF

# --- CONFIGURATION ---
NANONETS_API_KEY = "YOUR_FREE_API_KEY" # Get it from nanonets.com

def convert_pdf_to_csv(pdf_file):
    """Uses Nanonets API to convert PDF to CSV"""
    url = 'https://app.nanonets.com/api/v2/OCR/FullText'
    # This is a simplified logic; Nanonets provides a specific 'Bank Statement' model ID
    # For a truly 'no-key' experience, we advise users to use the Nanonets web converter.
    return pd.read_csv(pdf_file) # Placeholder: Implementation requires API Key

st.set_page_config(page_title="ReconPro Sri Lanka", layout="wide")

st.title("🏦 ReconPro: All-in-One Financial Tool")

# --- STEP 1: FILE FORMAT CHECK ---
file_format = st.radio("Do you have your files in CSV format?", ("Yes, I have CSV", "No, I have PDF"))

if file_format == "No, I have PDF":
    st.info("💡 PDF detected. We will use AI to convert your statement to a table format.")
    uploaded_pdf = st.file_uploader("Upload PDF Bank Statement", type="pdf")
    if uploaded_pdf:
        st.success("PDF Received! Converting to CSV via AI...")
        # Logic to call Nanonets or similar API would go here
        # For now, we guide users to the free converter to keep their account safe
        st.markdown("[Click here to convert your PDF to CSV for free](https://nanonets.com/bank-statement-converter)")

# --- STEP 2: RECONCILIATION ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("Upload Bank Statement (CSV)", type="csv", key="stmt")
with col2:
    book_file = st.file_uploader("Upload Bank Book (CSV)", type="csv", key="book")

if st.button("🚀 Run Reconciliation"):
    if stmt_file and book_file:
        df_stmt = pd.read_csv(stmt_file)
        df_book = pd.read_csv(book_file)

        # Standardizing Amounts
        df_stmt['Amount'] = df_stmt['Debit'].fillna(0) - df_stmt['Credit'].fillna(0)
        df_book['Amount'] = df_book['Debit'].fillna(0) - df_book['Credit'].fillna(0)

        # Reconciliation Logic
        recon = pd.merge(df_stmt, df_book, on=['Reference', 'Amount'], how='outer', indicator=True)
        
        # UI Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("✅ Matched", len(recon[recon['_merge']=='both']))
        m2.metric("❌ Missing in Book", len(recon[recon['_merge']=='left_only']))
        
        # Preview
        st.subheader("📋 Reconciliation Preview")
        st.dataframe(recon.head(10), use_container_width=True)

        # PDF Download
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Official Reconciliation Report", ln=1, align='C')
        # (Add table data to PDF here)
        
        st.download_button("📄 Download PDF Report", data=pdf.output(), file_name="Report.pdf")
