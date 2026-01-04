import streamlit as st
import pandas as pd
from fpdf import FPDF
import streamlit.components.v1 as components
from io import BytesIO

# --- CONFIGURATION & BRANDING ---
st.set_page_config(page_title="GDP Consultants | Bank Reconciliation AI", layout="wide")

# Hide Streamlit Branding
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- PRICING LOGIC ---
def calculate_fee(entries):
    if entries <= 100:
        return 5.0
    else:
        additional_units = (entries - 101) // 100 + 1
        return 5.0 + (additional_units * 1.0)

# --- BRS PDF GENERATOR ---
class BRS_PDF(FPDF):
    def header(self):
        if hasattr(self, 'business_name'):
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, self.business_name, ln=True, align='C')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Bank Reconciliation Statement', ln=True, align='C')
        self.ln(5)

def generate_pdf(data):
    pdf = BRS_PDF()
    pdf.business_name = data.get('biz_name', 'Business Entity')
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Header Info
    pdf.cell(100, 7, f"Bank: {data.get('bank_name', 'N/A')}")
    pdf.cell(0, 7, f"Account No: {data.get('acc_no', 'N/A')}", ln=True)
    pdf.cell(0, 7, f"Period: {data.get('period', 'N/A')}", ln=True)
    pdf.ln(5)

    # 1. Adjusted Cash Book
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "1. Adjusted Cash Book Balance", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(140, 7, "Balance as per Cash Book (Unadjusted)", 1)
    pdf.cell(40, 7, f"{data['raw_book_bal']:,.2f}", 1, ln=True)
    
    for entry in data['book_adjustments']:
        pdf.cell(140, 7, f"   {entry['desc']} (Ref: {entry['ref']})", 1)
        pdf.cell(40, 7, f"{entry['amt']:,.2f}", 1, ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 7, "Adjusted Cash Book Balance", 1)
    pdf.cell(40, 7, f"{data['adj_book_bal']:,.2f}", 1, ln=True)
    pdf.ln(5)

    # 2. Bank Reconciliation
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "2. Reconciliation with Bank Statement", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(140, 7, "Balance as per Bank Statement", 1)
    pdf.cell(40, 7, f"{data['bank_stmt_bal']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 7, "Add: Unrealised Deposits (Lodgements not cleared)", 1, ln=True)
    for dep in data['unrealised']:
        pdf.cell(140, 7, f"   {dep['date']} - {dep['ref']} ({dep['desc']})", 1)
        pdf.cell(40, 7, f"{dep['amt']:,.2f}", 1, ln=True)

    pdf.cell(140, 7, "Less: Unpresented Cheques", 1, ln=True)
    for chq in data['unpresented']:
        pdf.cell(140, 7, f"   {chq['date']} - {chq['ref']} ({chq['desc']})", 1)
        pdf.cell(40, 7, f"({chq['amt']:,.2f})", 1, ln=True)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 7, "Reconciled Balance", 1)
    pdf.cell(40, 7, f"{data['adj_book_bal']:,.2f}", 1, ln=True)

    return bytes(pdf.output())

# --- MAIN UI ---
st.title("Bank Reconciliation AI")
st.sidebar.image("logo-removebg-preview.png")

# Step 1: Uploads
with st.container():
    st.subheader("Step 1: Upload Documents (Excel/CSV Only)")
    up_prev = st.file_uploader("Previous Month Reconciliation (Optional)", type=['xlsx', 'csv'])
    up_stmt = st.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
    up_book = st.file_uploader("Current Bank/Cash Book", type=['xlsx', 'csv'])

if up_stmt and up_book:
    # Read Files
    df_stmt = pd.read_excel(up_stmt) if up_stmt.name.endswith('xlsx') else pd.read_csv(up_stmt)
    df_book = pd.read_excel(up_book) if up_book.name.endswith('xlsx') else pd.read_csv(up_book)
    
    # Calculate Price
    entry_count = len(df_book)
    fee = calculate_fee(entry_count)
    
    # MOCK LOGIC for Demonstration (Replace with your matching algorithms)
    report_data = {
        "biz_name": "User Business Name",
        "bank_name": "Commercial Bank",
        "acc_no": "123456789",
        "period": "Month End 2024",
        "raw_book_bal": 50000.00,
        "adj_book_bal": 49850.00,
        "bank_stmt_bal": 45000.00,
        "book_adjustments": [{"desc": "Bank Charges", "ref": "SVC123", "amt": -150.00}],
        "unrealised": [{"date": "2024-02-28", "ref": "DEP99", "desc": "Customer Pmt", "amt": 8000.00}],
        "unpresented": [{"date": "2024-02-25", "ref": "CHQ501", "desc": "Rent", "amt": 3150.00}]
    }

    # PREVIEW SECTION
    st.divider()
    st.subheader("Step 2: Preview Reconciliation Results")
    st.write(f"**Entries Counted:** {entry_count} | **Total Fee:** ${fee:.2f}")
    
    c1, c2 = st.columns(2)
    c1.metric("Adjusted Book Balance", f"{report_data['adj_book_bal']:,.2f}")
    c2.metric("Bank Stmt Balance", f"{report_data['bank_stmt_bal']:,.2f}")
    
    # Step 3: Payment & Download
    st.divider()
    st.subheader("Step 3: Secure Payment to Download")
    
    paypal_id = "AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD"
    
    paypal_html = f"""
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
                    window.parent.postMessage({{ type: 'PAYMENT_SUCCESS' }}, '*');
                }});
            }}
        }}).render('#paypal-button-container');
    </script>
    """
    
    components.html(paypal_html, height=300)

    # Note: In a production app, use session_state to verify payment before showing download
    st.info("Once payment is confirmed, the download buttons below will activate.")
    
    pdf_file = generate_pdf(report_data)
    st.download_button("📄 Download PDF Report", pdf_file, "BRS_Report.pdf", "application/pdf")
    
    # Excel Export
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_book.to_excel(writer, sheet_name='Adjusted_Book')
    st.download_button("Excel Download", buffer.getvalue(), "BRS_Report.xlsx")
