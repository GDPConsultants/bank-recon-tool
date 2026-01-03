import streamlit as st
import pandas as pd
import requests
import time
from fpdf import FPDF
from io import BytesIO

# --- NANONETS SETTINGS ---
NANONETS_API_KEY = "YOUR_NANONETS_API_KEY"  # Get this from app.nanonets.com
MODEL_ID = "YOUR_MODEL_ID" # Use 'Pre-built Bank Statement' model ID

def convert_pdf_to_csv(uploaded_file):
    """Sends PDF to Nanonets and returns a DataFrame"""
    url = f'https://app.nanonets.com/api/v2/OCR/Model/{MODEL_ID}/LabelFile/'
    data = {'file': uploaded_file}
    response = requests.post(url, auth=requests.auth.HTTPBasicAuth(NANONETS_API_KEY, ''), files=data)
    
    if response.status_code == 200:
        # Nanonets returns JSON/CSV. We parse the result table here.
        # Note: You can also set 'output_type' to 'csv' in the API request
        result = response.json()
        # simplified logic: extract transaction table from result
        return pd.DataFrame(result['result'][0]['prediction']) 
    else:
        st.error("Nanonets Conversion Failed. Check API Key/Model ID.")
        return None

def load_any_file(uploaded_file):
    """Handles PDF, XLSX, and CSV automatically"""
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.pdf'):
        with st.spinner("AI is reading your PDF Bank Statement..."):
            return convert_pdf_to_csv(uploaded_file)
    return None

# --- MAIN APP UI ---
st.title("🏦 ReconPro Smart Automator")

# Rearranged Instructions for the User
with st.sidebar:
    st.header("📖 How it Works")
    st.info("""
    1. **Upload:** Drop your files (PDF, Excel, or CSV).
    2. **AI Processing:** If you upload a PDF, our AI (Nanonets) reads it.
    3. **Verify:** Check the preview below.
    4. **Download:** Get your PDF Reconciliation report.
    """)

col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("Bank Statement (PDF/XLSX/CSV)", type=['pdf', 'xlsx', 'csv'])
with col2:
    book_file = st.file_uploader("Bank Book (XLSX/CSV)", type=['xlsx', 'csv'])

if st.button("🚀 Run Automation"):
    if stmt_file and book_file:
        df_stmt = load_any_file(stmt_file)
        df_book = load_any_file(book_file)
        
        if df_stmt is not None and df_book is not None:
            # (Rest of your matching and PDF generation logic goes here)
            st.success("Reconciliation Complete!")
            st.subheader("Standard Format Preview")
            st.dataframe(df_stmt.head())
