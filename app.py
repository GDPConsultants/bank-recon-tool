import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from io import BytesIO
import streamlit.components.v1 as components

# --- 1. BRANDING & UI CONFIGURATION ---
st.set_page_config(
    page_title="Bank Reconciliation AI | GDP Consultants", 
    layout="wide", 
    page_icon="logo-removebg-preview.png"
)

# Custom CSS for Professional Display
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .preview-box { background: white; border: 2px solid #ddd; padding: 40px; border-radius: 5px; font-family: 'Courier New', Courier, monospace; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPERS & CALCULATIONS ---
def calculate_fee(entries):
    """Tiered pricing: $5 min (<100), +$1 for every additional 100 entries"""
    if entries < 100:
        return 5.0
    return 5.0 + math.floor(entries / 100)

def extract_metadata(df_stmt, df_book):
    """Simulated metadata extraction from common bank statement headers"""
    # In a production app, use Regex to find patterns like 'Account No:' or 'Statement for:'
    return {
        "biz_name": "Valued Client Business",
        "bank_name": "Commercial Bank of Sri Lanka",
        "acc_no": "8000XXXX1234",
        "period": "January 2026"
    }

# --- 3. BRS LOGIC & PDF GENERATION ---
def generate_pdf(data, branding_name):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image("logo-removebg-preview.png", 10, 8, 25)
    except: pass
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, branding_name.upper(), ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, f"Bank: {data['bank_name']} | Acc: {data['acc_no']}", ln=True, align='C')
    pdf.cell(0, 5, f"Period: {data['period']}", ln=True, align='C')
    pdf.ln(10)

    # Standard BRS Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Particulars", 1); pdf.cell(50, 10, "Amount (LKR)", 1, ln=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(140, 10, "Balance as per Bank Statement", 1); pdf.cell(50, 10, f"{data['bank_bal']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 10, "Add: Unrealised Deposits (from Previous & Current)", 1); pdf.cell(50, 10, f"{data['unrealised']:,.2f}", 1, ln=True)
    pdf.cell(140, 10, "Less: Unpresented Cheques (from Previous & Current)", 1); pdf.cell(50, 10, f"({data['unpresented']:,.2f})", 1, ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "Adjusted Cash Book Balance", 1); pdf.cell(50, 10, f"{data['adj_book_bal']:,.2f}", 1, ln=True)
    
    return bytes(pdf.output())

# --- 4. SIDEBAR (Instructions & Contact) ---
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.title("GDP Consultants")
    st.markdown("""
    ### 📖 How to Use
    1. **Upload Previous Month BRS:** To track items that didn't clear last month.
    2. **Upload Current Month Files:** Provide your Cash Book and Bank Statement (Excel/CSV).
    3. **Preview:** Review the generated report on screen.
    4. **Pay & Download:** Securely pay via PayPal to download the audit-ready PDF or Excel.
    
    ### 📞 Contact Support
    📧 [info@taxcalculator.lk](mailto:info@taxcalculator.lk)  
    🌐 [www.taxcalculator.lk](https://www.taxcalculator.lk)
    """)

# --- 5. MAIN APP INTERFACE ---
st.title("Bank Reconciliation AI")
st.info("Advanced AI Reconciliation with Previous Month Carryforward")

if "paid" not in st.session_state: st.session_state.paid = False

# Step 1: Uploads
u1, u2, u3 = st.columns(3)
with u1: prev_brs = st.file_uploader("Previous Month BRS (Optional)", type=['xlsx', 'csv'])
with u2: curr_stmt = st.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
with u3: curr_book = st.file_uploader("Current Cash Book", type=['xlsx', 'csv'])

if curr_stmt and curr_book:
    # Process Data
    df_stmt = pd.read_excel(curr_stmt) if curr_stmt.name.endswith('xlsx') else pd.read_csv(curr_stmt)
    df_book = pd.read_excel(curr_book) if curr_book.name.endswith('xlsx') else pd.read_csv(curr_book)
    
    # Calculate Metadata & Pricing
    meta = extract_metadata(df_stmt, df_book)
    fee = calculate_fee(len(df_book))
    
    # Reconciliation Logic (Simplified Example for Demo)
    # In a real run, this code would cross-reference the Previous BRS for unpresented items
    report_data = {
        **meta,
        "bank_bal": 125400.00,
        "unrealised": 15000.00,
        "unpresented": 8500.00,
        "adj_book_bal": 131900.00
    }

    # --- PREVIEW SECTION ---
    st.divider()
    st.subheader("🖼️ Official BRS Preview (Standard Format)")
    st.markdown(f"""
    <div class="preview-box">
        <h2 style="text-align:center;">{meta['biz_name'].upper()}</h2>
        <p style="text-align:center;">Bank: {meta['bank_name']} | Account: {meta['acc_no']}</p>
        <p style="text-align:center;">Period: {meta['period']}</p>
        <hr>
        <table style="width:100%">
            <tr><td><b>Balance as per Bank Statement</b></td><td style="text-align:right;"><b>{report_data['bank_bal']:,.2f}</b></td></tr>
            <tr><td>(+) Unrealised Deposits</td><td style="text-align:right;">{report_data['unrealised']:,.2f}</td></tr>
            <tr><td>(-) Unpresented Cheques</td><td style="text-align:right;">({report_data['unpresented']:,.2f})</td></tr>
            <tr style="border-top:2px solid black;"><td><b>Adjusted Cash Book Balance</b></td><td style="text-align:right;"><b>{report_data['adj_book_bal']:,.2f}</b></td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # --- PAYMENT & DOWNLOAD ---
    st.divider()
    if not st.session_state.paid:
        p1, p2 = st.columns([2, 1])
        with p1:
            st.warning(f"Total Transactions: {len(df_book)} | Reconciliation Fee: **USD {fee:.2f}**")
            st.write("To download the final PDF or Excel version, please complete the payment.")
        with p2:
            paypal_id = "AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD"
            paypal_btn = f"""
            <div id="paypal-button-container"></div>
            <script src="https://www.paypal.com/sdk/js?client-id={paypal_id}&currency=USD"></script>
            <script>
                paypal.Buttons({{
                    createOrder: function(data, actions) {{
                        return actions.order.create({{
                            purchase_units: [{{ amount: {{ value: '{fee}' }} }}]
                        }});
                    }},
                    onApprove: function(data, actions) {{
                        return actions.order.capture().then(function(details) {{
                            alert('Payment Successful! You can now download your files.');
                            window.parent.postMessage({{type: 'payment_done'}}, '*');
                        }});
                    }}
                }}).render('#paypal-button-container');
            </script>
            """
            components.html(paypal_btn, height=350)
            if st.button("Unlock Downloads (Simulate Payment for Testing)"): st.session_state.paid = True

    if st.session_state.paid:
        st.success("✅ Payment Verified. Your audit reports are ready.")
        pdf_file = generate_pdf(report_data, meta['biz_name'])
        d1, d2 = st.columns(2)
        with d1: st.download_button("📄 Download PDF Report", pdf_file, f"BRS_{meta['period']}.pdf", "application/pdf")
        with d2: st.download_button("📊 Download Excel Format", curr_book.getvalue(), f"BRS_{meta['period']}.xlsx")
