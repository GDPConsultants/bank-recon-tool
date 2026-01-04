import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
import streamlit.components.v1 as components
from io import BytesIO

# --- 1. CONFIGURATION & PAYPAL ---
CLIENT_ID = "AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD"
# Secret should be kept in streamlit secrets, not hardcoded in production

st.set_page_config(page_title="Bank Reconciliation AI", layout="wide")

# UI Styling & Security
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .price-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #d1d5db; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---
def calculate_fee(entries):
    """Calculates fee: $5 min for <100, then $1 per 100 entries"""
    if entries <= 100:
        return 5.00
    return 5.00 + math.ceil((entries - 100) / 100) * 1.00

def get_business_branding(df):
    """Extracts business name if found in top rows, else generic"""
    try: return str(df.iloc[0,0]) if not df.empty else "Client Business"
    except: return "Client Business"

# --- 3. REPORT GENERATORS ---
def create_pdf_report(data, branding_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"{branding_name}", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Bank Reconciliation Statement", ln=True, align='C')
    pdf.ln(10)
    
    # BRS Details following CPA Step 4 [cite: 81]
    pdf.set_font("Arial", '', 11)
    pdf.cell(140, 10, "Closing Balance per Bank Statement", 1)
    pdf.cell(50, 10, f"{data['bank_bal']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 10, "Add: Unrealised Deposits", 1)
    pdf.cell(50, 10, f"{data['transit']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 10, "Less: Unpresented Cheques", 1)
    pdf.cell(50, 10, f"({data['outstanding']:,.2f})", 1, ln=True)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 10, "Adjusted Balance", 1)
    pdf.cell(50, 10, f"{data['reconciled']:,.2f}", 1, ln=True)
    
    return bytes(pdf.output())

# --- 4. APP FLOW ---
if "paid" not in st.session_state: st.session_state.paid = False

st.title("Bank Reconciliation AI")
st.write("Professional Audit Reporting with Pay-Per-Use")

# Side Instruction [cite: 19]
with st.sidebar:
    st.header("Step-by-Step Guide")
    st.write("1. Upload Current Month Files")
    st.write("2. Review Free Preview")
    st.write("3. Pay Dynamic Fee to Download")
    st.divider()
    st.write("Support: info@taxcalculator.lk")

# File Uploads
c1, c2 = st.columns(2)
with c1:
    stmt_file = st.file_uploader("Bank Statement (Excel/CSV)", type=['xlsx', 'csv'])
with c2:
    book_file = st.file_uploader("Bank Book (Excel/CSV)", type=['xlsx', 'csv'])

if stmt_file and book_file:
    # Load data
    df_book = pd.read_excel(book_file) if book_file.name.endswith('.xlsx') else pd.read_csv(book_file)
    entry_count = len(df_book)
    fee = calculate_fee(entry_count)
    biz_name = get_business_branding(df_book)
    
    # Preview Section
    st.subheader("📋 Reconciliation Preview (Unadjusted)")
    st.info(f"Detected **{entry_count}** entries in Bank Book. Total Fee: **${fee:.2f}**")
    
    # Mock analysis for preview
    preview_data = {"bank_bal": 10000.0, "transit": 2500.0, "outstanding": 1200.0, "reconciled": 11300.0}
    st.dataframe(df_book.head(5), use_container_width=True)

    # Payment Section
    if not st.session_state.paid:
        st.markdown(f"""
        <div class="price-card">
            <h3>Download Full BRS Report</h3>
            <p>Your report is ready. Please pay <b>${fee:.2f}</b> to download PDF and Excel formats with <b>{biz_name}</b> branding.</p>
        </div>
        """, unsafe_allow_html=True)
        
        paypal_html = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID}&currency=USD"></script>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{fee:.2f}' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        window.parent.postMessage({{type: 'payment_success'}}, '*');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)
        
        # Simulated payment capture (In production, use a webhook or button check)
        if st.button("I have completed the payment"):
             st.session_state.paid = True
             st.rerun()

    # Download Section
    if st.session_state.paid:
        st.success(f"Payment Verified! Branding Applied: {biz_name}")
        
        # PDF Generation
        pdf_bytes = create_pdf_report(preview_data, biz_name)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📥 Download BRS (PDF)", pdf_bytes, f"{biz_name}_BRS.pdf", "application/pdf")
        with col_dl2:
            # Excel Export
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_book.to_excel(writer, index=False, sheet_name='Reconciliation')
            st.download_button("📥 Download BRS (Excel)", output.getvalue(), f"{biz_name}_BRS.xlsx")

else:
    st.warning("Please upload files to see the preview and price.")
