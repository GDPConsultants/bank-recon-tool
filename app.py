import streamlit as st
import pandas as pd
from thefuzz import fuzz
from fpdf import FPDF
import streamlit.components.v1 as components
from io import BytesIO

# --- PAGE CONFIG & THEME ---
st.set_page_config(page_title="ReconPro Sri Lanka", layout="wide", page_icon="🏦")

# Custom CSS for Attractive UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #0056b3; border: none; }
    .metric-card { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

ACCESS_PASSWORD = "ReconPro2026"

# --- HELPER: PDF GENERATOR ---
def create_pdf(matched_df, missing_book, missing_bank):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Bank Reconciliation Summary Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "Status: Generated via ReconPro Tool", ln=True, align='C')
    pdf.ln(10)
    
    # Summary Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Category")
    pdf.cell(40, 10, "Count")
    pdf.ln()
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 10, "Successfully Matched Items:")
    pdf.cell(40, 10, str(len(matched_df)))
    pdf.ln()
    pdf.cell(100, 10, "Unrecorded in Books (Check Bank Statement):")
    pdf.cell(40, 10, str(len(missing_book)))
    pdf.ln()
    pdf.cell(100, 10, "Outstanding in Bank (Check Book):")
    pdf.cell(40, 10, str(len(missing_bank)))
    
    return pdf.output()

# --- APP LOGIC & PAYWALL ---
if "reconcile_count" not in st.session_state: st.session_state.reconcile_count = 0
if "authenticated" not in st.session_state: st.session_state.authenticated = False

# [Paywall Logic Block - Same as previous, using your PayPal ID]
if st.session_state.reconcile_count >= 1 and not st.session_state.authenticated:
    st.title("🔓 Upgrade for Unlimited Access")
    # ... (PayPal Component here) ...
    st.stop()

# --- MAIN APP INTERFACE ---
st.title("🏦 ReconPro: Sri Lanka Financial Automator")

with st.expander("ℹ️ How to use this tool"):
    st.write("1. Upload your Bank Statement and Ledger (Bank Book) in **CSV** format.")
    st.write("2. Ensure columns are: **Date, Description, Reference, Debit, Credit**.")
    st.write("3. Review the preview and download your official PDF report.")

col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("📂 Upload Bank Statement", type="csv")
with col2:
    book_file = st.file_uploader("📖 Upload Bank Book", type="csv")

if st.button("🚀 Start Reconciliation"):
    if stmt_file and book_file:
        st.session_state.reconcile_count += 1
        
        # Data Processing
        df_stmt = pd.read_csv(stmt_file)
        df_book = pd.read_csv(book_file)
        
        # Calculation
        df_stmt['Amount'] = df_stmt['Debit'].fillna(0) - df_stmt['Credit'].fillna(0)
        df_book['Amount'] = df_book['Debit'].fillna(0) - df_book['Credit'].fillna(0)
        
        # Matching
        recon = pd.merge(df_stmt, df_book, on=['Reference', 'Amount'], how='outer', indicator=True, suffixes=('_Bank', '_Book'))
        
        matched = recon[recon['_merge'] == 'both']
        missing_book = recon[recon['_merge'] == 'left_only']
        missing_bank = recon[recon['_merge'] == 'right_only']

        # UI: Dashboard Metrics
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("✅ Matched", len(matched))
        m2.metric("❌ Missing in Book", len(missing_book))
        m3.metric("⏳ Outstanding in Bank", len(missing_bank))

        # UI: Standard Format Preview
        st.subheader("📋 Reconciliation Preview")
        tab1, tab2 = st.tabs(["Matched Items", "Discrepancies"])
        with tab1:
            st.dataframe(matched[['Date_Bank', 'Reference', 'Amount']].head(10), use_container_width=True)
        with tab2:
            st.write("**Items found in Bank but NOT in Books:**")
            st.dataframe(missing_book[['Date_Bank', 'Description_Bank', 'Amount']], use_container_width=True)

        # PDF Download Functionality
        pdf_data = create_pdf(matched, missing_book, missing_bank)
        st.download_button(
            label="📄 Download Official PDF Report",
            data=pdf_data,
            file_name="Recon_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Please upload both files to proceed.")
