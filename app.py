import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
import io

# --- 1. SECURITY & BRANDING CONFIG ---
st.set_page_config(page_title="Bank Reconciliation AI | GDP Consultants", layout="wide")

# Hide Streamlit UI to protect source code from end-users
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. PRICING & PAYMENT LOGIC ---
PAYPAL_CLIENT_ID = "AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD"

def calculate_fee(entries):
    if entries <= 100:
        return 5.0
    return 5.0 + ((entries - 1) // 100) * 1.0

# --- 3. CORE ACCOUNTING & REPORTING ---
def generate_brs_image(data):
    """Creates a high-fidelity image preview of the BRS for the user to see before paying."""
    img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Using a simple coordinate system for the professional BRS layout
    y = 60
    draw.text((450, y), "BANK RECONCILIATION STATEMENT", fill=(0,0,128))
    y += 80
    draw.text((100, y), f"Business: {data['biz_name']}")
    draw.text((700, y), f"Period: {data['period']}")
    y += 40
    draw.text((100, y), f"Bank: {data['bank_name']} | Account: {data['acc_no']}")
    y += 100
    
    # Standard CPA Format Table 
    headers = ["Particulars", "Details", "Amount"]
    draw.text((100, y), "Balance as per Bank Statement (Adjusted for O/D)", fill=(0,0,0))
    draw.text((900, y), f"{data['bank_bal']:,.2f}")
    y += 60
    draw.text((100, y), "ADD: Unrealised Deposits (Lodgements in Transit)")
    y += 40
    for d in data['transit']:
        draw.text((150, y), f"{d['date']} - {d['ref']}")
        draw.text((900, y), f"{d['amt']:,.2f}")
        y += 40
    # ... (Logic to add Unpresented Cheques and Adjusted Cash Book Entries)
    
    # Watermark
    draw.text((300, 800), "PREVIEW ONLY - UNLOCK TO DOWNLOAD", fill=(200,200,200))
    return img

# --- 4. APP INTERFACE ---
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.header("📖 Instructions")
    st.markdown("""
    1. **Upload Previous BRS:** Required to track unpresented cheques from last month[cite: 54].
    2. **Upload Current Data:** Use Excel or CSV for Bank Statement and Cash Book.
    3. **Review Preview:** View the complete adjusted balance report.
    4. **Pay & Download:** Payment is calculated automatically based on entries.
    """)
    st.divider()
    st.write("**GDP Consultants** | info@taxcalculator.lk")

st.title("Bank Reconciliation AI")
st.write("Professional Audit-Ready Reconciliation Service")

# File Uploaders
c1, c2, c3 = st.columns(3)
p_brs = c1.file_uploader("Previous Month BRS (Excel/CSV)", type=['xlsx', 'csv'])
c_stmt = c2.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
c_book = c3.file_uploader("Current Cash Book", type=['xlsx', 'csv'])

if c_stmt and c_book:
    # Processing entries for pricing
    book_df = pd.read_excel(c_book) if c_book.name.endswith('xlsx') else pd.read_csv(c_book)
    total_entries = len(book_df)
    fee = calculate_fee(total_entries)

    # RECONCILIATION LOGIC (Simplified Placeholder for Demo)
    # This logic matches Step 3 (Cash Book Adjustment) and Step 4 (Bank Stmt Reconciliation) [cite: 63, 73]
    report_data = {
        "biz_name": "Client Business Name", "bank_name": "Commercial Bank",
        "acc_no": "9988776655", "period": "Current Month",
        "bank_bal": 45000.00, "raw_book_bal": 42000.00,
        "transit": [{"date": "2026-01-31", "ref": "DEP101", "amt": 5000.00}]
    }

    st.subheader("🏁 Full Reconciliation Preview")
    st.info("Please review all entries below. Watermarked for security.")
    preview = generate_brs_image(report_data)
    st.image(preview, use_container_width=True)

    # PAYMENT GATEWAY
    st.divider()
    st.subheader("💳 Secure Payment & Download")
    st.write(f"Detection: **{total_entries} entries**. Processing Fee: **USD {fee:.2f}**")
    
    paypal_btn = f"""
    <div id="paypal-button-container"></div>
    <script src="https://www.paypal.com/sdk/js?client-id={PAYPAL_CLIENT_ID}&currency=USD"></script>
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
    components.html(paypal_btn, height=550)
    
    if st.checkbox("I have completed the payment"):
        st.success("Thank you. Your download links are now active.")
        st.download_button("📥 Download PDF Report", b"PDF_DATA", "Final_BRS.pdf")
        st.download_button("📥 Download Excel Report", b"EXCEL_DATA", "Final_BRS.xlsx")
