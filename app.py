import streamlit as st
import pandas as pd
from fpdf import FPDF
import streamlit.components.v1 as components

# --- 1. BRANDING & UI ---
st.set_page_config(page_title="Bank Reconciliation AI | GDP Consultants", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .report-box {background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE 5-STEP PROCESSOR ---
def create_recon_statement(df_stmt, df_book, bank_bal, book_bal):
    # Step 3: Identify Outstanding Items
    # Merging to find differences
    recon = pd.merge(df_stmt, df_book, on=['Reference', 'Amount'], how='outer', indicator=True)
    
    # Bank Side Adjustments
    dep_in_transit = recon[recon['_merge'] == 'right_only'] # In books, not in bank
    out_checks = dep_in_transit[dep_in_transit['Amount'] < 0]
    dep_in_transit = dep_in_transit[dep_in_transit['Amount'] > 0]
    
    # Book Side Adjustments
    stmt_only = recon[recon['_merge'] == 'left_only'] # In bank, not in books
    int_earned = stmt_only[stmt_only['Amount'] > 0]
    bank_charges = stmt_only[stmt_only['Amount'] < 0]

    # Step 4: Calculate Adjusted Balances
    adj_bank_bal = bank_bal + dep_in_transit['Amount'].sum() + out_checks['Amount'].sum()
    adj_book_bal = book_bal + int_earned['Amount'].sum() + bank_charges['Amount'].sum()
    
    return {
        "bank_bal": bank_bal,
        "book_bal": book_bal,
        "dep_in_transit": dep_in_transit,
        "out_checks": out_checks,
        "int_earned": int_earned,
        "bank_charges": bank_charges,
        "adj_bank": adj_bank_bal,
        "adj_book": adj_book_bal
    }

# --- 3. UI INTERFACE ---
st.title("Bank Reconciliation AI")
st.write("Professional 5-Step Reconciliation Engine by **GDP Consultants**")

with st.sidebar:
    st.header("Step-by-Step Guide")
    st.info("""
    1. **Gather** Statement & Records
    2. **Compare** Starting Balances
    3. **Identify** Outstanding Items
    4. **Adjust** Both Sides
    5. **Verify** Final Balance
    """)
    st.write("📧 info@taxcalculator.lk")

col1, col2 = st.columns(2)
with col1:
    bank_end_bal = st.number_input("Ending Balance per Bank Statement ($)", value=12500.0)
    stmt_file = st.file_uploader("Upload Bank Statement (CSV)", type=['csv'])
with col2:
    book_end_bal = st.number_input("Ending Balance per Cash Book ($)", value=11890.0)
    book_file = st.file_uploader("Upload Cash Book (CSV)", type=['csv'])

if st.button("🚀 Reconcile and Generate Statement"):
    if stmt_file and book_file:
        df_stmt = pd.read_csv(stmt_file)
        df_book = pd.read_csv(book_file)
        
        # Ensure 'Amount' column exists
        df_stmt['Amount'] = df_stmt['Debit'].fillna(0) - df_stmt['Credit'].fillna(0)
        df_book['Amount'] = df_book['Debit'].fillna(0) - df_book['Credit'].fillna(0)

        results = create_recon_statement(df_stmt, df_book, bank_end_bal, book_end_bal)

        # DISPLAY RESULTS
        st.divider()
        st.subheader("Final Bank Reconciliation Statement")
        
        c_stmt, c_book = st.columns(2)
        
        with c_stmt:
            st.markdown("### BANK SIDE")
            st.write(f"Balance per Bank: **${results['bank_bal']:,.2f}**")
            st.write(f"Add: Deposits in Transit: **${results['dep_in_transit']['Amount'].sum():,.2f}**")
            st.write(f"Less: Outstanding Checks: **(${abs(results['out_checks']['Amount'].sum()):,.2f})**")
            st.success(f"**Adjusted Bank Balance: ${results['adj_bank']:,.2f}**")

        with c_book:
            st.markdown("### BOOK SIDE")
            st.write(f"Balance per Cash Book: **${results['book_bal']:,.2f}**")
            st.write(f"Add: Interest/Direct Deposits: **${results['int_earned']['Amount'].sum():,.2f}**")
            st.write(f"Less: Bank Charges/NSF: **(${abs(results['bank_charges']['Amount'].sum()):,.2f})**")
            st.success(f"**Adjusted Book Balance: ${results['adj_book']:,.2f}**")

        if round(results['adj_bank'], 2) == round(results['adj_book'], 2):
            st.balloons()
            st.success("✅ Reconciliation Successful! Both sides match exactly.")
        else:
            st.error("⚠️ Discrepancy Found. Please review the unrecorded items.")
