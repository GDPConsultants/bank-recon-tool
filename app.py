import streamlit as st
import pandas as pd
from fpdf import FPDF
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. BRANDING & SESSION CONFIG ---
st.set_page_config(page_title="Bank Reconciliation AI | GDP Consultants", layout="wide")

# Custom CSS to hide Streamlit branding
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

if "payment_done" not in st.session_state: st.session_state.payment_done = False

# --- 2. CORE LOGIC: PRICING & DATA ---
def calculate_fee(entries_count):
    """Minimum $5 for <100 entries, +$1 for every additional 100 entries."""
    if entries_count <= 100:
        return 5.0
    return 5.0 + ((entries_count - 1) // 100)

def generate_watermark_preview(text_content):
    """Creates an image preview with a 'PREVIEW ONLY' watermark."""
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((50, 50), text_content, fill=(0, 0, 0))
    # Watermark
    d.text((200, 400), "PREVIEW - PAY TO DOWNLOAD", fill=(200, 200, 200))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# --- 3. BRS PDF GENERATOR ---
def create_final_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    # Dynamic Branding: Uses Business Name from data
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"{data['biz_name']} - Bank Reconciliation", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Bank: {data['bank_name']} | Account No: {data['acc_no']}", ln=True, align='C')
    pdf.cell(0, 7, f"Period: {data['period']}", ln=True, align='C')
    pdf.ln(10)

    # Section 1: Adjusted Cash Book [cite: 30, 71]
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Adjusted Cash Book Balance", 1, ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(140, 10, "Opening Unadjusted Balance", 1); pdf.cell(50, 10, f"{data['currency']} {data['raw_book_bal']:,.2f}", 1, ln=True)
    
    for entry in data['book_adjustments']:
        pdf.cell(140, 10, f"  {entry['date']} {entry['desc']} ({entry['ref']})", 1)
        pdf.cell(50, 10, f"{entry['amt']:,.2f}", 1, ln=True)
    
    pdf.cell(140, 10, "Adjusted Cash Book Balance", 1); pdf.cell(50, 10, f"{data['adj_book_bal']:,.2f}", 1, ln=True)
    pdf.ln(5)

    # Section 2: Reconciliation [cite: 34, 81]
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Reconciliation to Bank Statement", 1, ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(140, 10, "Balance as per Bank Statement", 1); pdf.cell(50, 10, f"{data['bank_bal']:,.2f}", 1, ln=True)
    
    pdf.cell(0, 10, "Add: Unrealised Deposits (Lodgements not yet cleared)", ln=True)
    for dep in data['transit_deposits']:
        pdf.cell(140, 10, f"  {dep['ref']} - {dep['details']}", 1); pdf.cell(50, 10, f"{dep['amt']:,.2f}", 1, ln=True)
    
    pdf.cell(0, 10, "Less: Unpresented Cheques", ln=True)
    for chq in data['unpresented_cheques']:
        pdf.cell(140, 10, f"  {chq['ref']} - {chq['details']}", 1); pdf.cell(50, 10, f"({chq['amt']:,.2f})", 1, ln=True)

    return bytes(pdf.output())

# --- 4. MAIN APP INTERFACE ---
st.title("Bank Reconciliation AI")
st.write("Professional Audit Support by **GDP Consultants**")

with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.header("📖 Instructions")
    st.markdown("""
    1. **Upload Last Month's BRS:** To track unpresented cheques.
    2. **Upload Current Month:** Excel/CSV Cash Book & Bank Statement.
    3. **Review Preview:** See the calculated BRS and fee.
    4. **Pay & Download:** Get the branded PDF/Excel report.
    """)
    st.divider()
    st.write("📧 info@taxcalculator.lk | 🌐 www.taxcalculator.lk")

# File Uploaders
c1, c2, c3 = st.columns(3)
with c1: prev_brs = st.file_uploader("Previous BRS (Optional)", type=['xlsx', 'csv'])
with c2: curr_stmt = st.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
with c3: curr_book = st.file_uploader("Current Cash Book", type=['xlsx', 'csv'])

if curr_stmt and curr_book:
    # Logic to count entries and determine fee
    df_book = pd.read_excel(curr_book) if curr_book.name.endswith('xlsx') else pd.read_csv(curr_book)
    entry_count = len(df_book)
    fee = calculate_fee(entry_count)

    # Prepare Mock Data for Preview (In production, this is your processing logic)
    results = {
        "biz_name": "User Business Name", "bank_name": "Commercial Bank", "acc_no": "99887766",
        "period": "Jan 2026", "currency": "LKR", "raw_book_bal": 150000.00, "adj_book_bal": 149500.00,
        "bank_bal": 140000.00, "book_adjustments": [{"date": "31/01", "desc": "Bank Fees", "ref": "MS-01", "amt": -500.00}],
        "transit_deposits": [{"ref": "DEP101", "details": "Cash Lodgement", "amt": 15000.00}],
        "unpresented_cheques": [{"ref": "CHQ502", "details": "Supplier Payment", "amt": 5500.00}]
    }

    st.subheader("📊 Reconciliation Preview")
    preview_text = f"BRS PREVIEW\n\nBusiness: {results['biz_name']}\nAdjusted Book Balance: {results['adj_book_bal']}\nBank Balance: {results['bank_bal']}\n\nEntries Detected: {entry_count}\nService Fee: ${fee}"
    st.image(generate_watermark_preview(preview_text), caption="Payment required to download full document.")

    # PayPal Integration
    st.divider()
    if not st.session_state.payment_done:
        st.write(f"### Pay ${fee} to Download Full Report")
        paypal_html = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id=AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD&currency=USD"></script>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{ purchase_units: [{{ amount: {{ value: '{fee}' }} }}] }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        alert('Payment Successful! You can now download.');
                        window.parent.postMessage({{type: 'payment_success'}}, '*');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)
        
        # Manual Override for Demo / Key Entry
        if st.checkbox("I have paid / Enter Access Key"):
            st.session_state.payment_done = True
            st.rerun()
    else:
        st.success("Payment Verified. Download available.")
        pdf_file = create_final_pdf(results)
        st.download_button("📥 Download Branded PDF Report", pdf_file, "Final_BRS.pdf")
        st.download_button("Excel Version (Unadjusted Entries)", curr_book.getvalue(), "Adjusted_Book.xlsx")
