import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
import io

# --- 1. ADMIN & SECURITY CONFIG ---
st.set_page_config(page_title="Bank Reconciliation AI", layout="wide")

# Hide source code and Streamlit UI for users
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED ACCOUNTING LOGIC ---
def calculate_fee(entries):
    if entries < 100: return 5.0
    return 5.0 + ((entries // 100) * 1.0)

def generate_brs_image(data):
    """Creates a professional image-based preview of the BRS"""
    img = Image.new('RGB', (1000, 1400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Title & Branding
    y = 50
    d.text((350, y), f"{data['biz_name']}", fill=(0,0,0))
    y += 30
    d.text((380, y), "Bank Reconciliation Statement", fill=(0,0,0))
    y += 50
    
    d.text((50, y), f"Bank: {data['bank_name']}", fill=(0,0,0))
    d.text((700, y), f"Period: {data['period']}", fill=(0,0,0))
    y += 30
    d.text((50, y), f"Account No: {data['acc_no']}", fill=(0,0,0))
    y += 60

    # Part 1: Adjusted Cash Book
    d.text((50, y), "PART 1: ADJUSTED CASH BOOK BALANCE", fill=(0,0,0))
    y += 40
    d.text((60, y), "Unadjusted Balance per Cash Book", fill=(0,0,0))
    d.text((800, y), f"{data['currency']} {data['raw_book_bal']:,.2f}", fill=(0,0,0))
    y += 30
    
    for entry in data['book_adjustments']:
        d.text((80, y), f"{entry['date']} - {entry['desc']} ({entry['ref']})", fill=(0,0,0))
        d.text((800, y), f"{entry['amt']:,.2f}", fill=(0,0,0))
        y += 30
    
    y += 10
    d.text((60, y), "ADJUSTED CASH BOOK BALANCE", fill=(0,0,0))
    d.text((800, y), f"{data['currency']} {data['adj_book_bal']:,.2f}", fill=(0,0,0))
    y += 70

    # Part 2: Bank Reconciliation (Step 4 CPA Standard)
    d.text((50, y), "PART 2: RECONCILIATION TO BANK STATEMENT", fill=(0,0,0))
    y += 40
    d.text((60, y), "Balance per Bank Statement", fill=(0,0,0))
    d.text((800, y), f"{data['currency']} {data['bank_bal']:,.2f}", fill=(0,0,0))
    y += 40
    
    d.text((60, y), "Add: Unrealised Deposits (Lodgements not cleared)", fill=(0,0,0))
    y += 30
    for dep in data['transit_deposits']:
        d.text((80, y), f"{dep['date']} - {dep['ref']}", fill=(0,0,0))
        d.text((800, y), f"{dep['amt']:,.2f}", fill=(0,0,0))
        y += 30
        
    y += 20
    d.text((60, y), "Less: Unpresented Cheques", fill=(0,0,0))
    y += 30
    for chq in data['unpresented_cheques']:
        d.text((80, y), f"{chq['date']} - {chq['ref']}", fill=(0,0,0))
        d.text((800, y), f"({chq['amt']:,.2f})", fill=(0,0,0))
        y += 30

    # Final Watermark
    d.text((300, 700), "PREVIEW WATERMARK - PAY TO DOWNLOAD", fill=(200,200,200))
    return img

# --- 3. APP INTERFACE ---
st.title("Bank Reconciliation AI")
st.write("Professional Audit Reporting by **GDP Consultants**")

# Instruction Panel
with st.expander("📖 Instructions & Steps"):
    st.write("1. **Step 1:** Upload Previous Month's BRS to track unpresented items[cite: 20, 56].")
    st.write("2. **Step 2:** Upload Current Bank Statement & Bank Book (Excel/CSV).")
    st.write("3. **Step 3:** Review the Image Preview of your Adjusted Cash Book.")
    st.write("4. **Step 4:** Pay via PayPal to unlock the PDF and Excel downloads.")

# Uploaders
c1, c2, c3 = st.columns(3)
p_brs = c1.file_uploader("Previous Month BRS", type=['xlsx', 'csv'])
c_stmt = c2.file_uploader("Bank Statement", type=['xlsx', 'csv'])
c_book = c3.file_uploader("Bank Book", type=['xlsx', 'csv'])

if c_stmt and c_book:
    # 1. Processing (Simulated Logic)
    book_df = pd.read_excel(c_book) if c_book.name.endswith('xlsx') else pd.read_csv(c_book)
    fee = calculate_fee(len(book_df))
    
    # 2. Extract Details for Report
    report_data = {
        "biz_name": "ABC ENTERPRISES", "bank_name": "HSBC", "acc_no": "9988776655",
        "period": "December 2025", "currency": "USD",
        "raw_book_bal": 12450.00, "adj_book_bal": 11950.00, "bank_bal": 8250.00,
        "book_adjustments": [{"date": "2025-12-31", "desc": "Bank Fees", "ref": "DD", "amt": -500.00}],
        "transit_deposits": [{"date": "2025-12-31", "ref": "LODG-909", "amt": 5000.00}],
        "unpresented_cheques": [{"date": "2025-12-15", "ref": "CHQ-102", "amt": 1300.00}]
    }

    # 3. Show Preview
    st.subheader("🏁 Completed BRS Preview (Standard Format)")
    preview = generate_brs_image(report_data)
    st.image(preview, caption="Standard CPA-Format Reconciliation Preview")

    # 4. Payment Gateway
    st.divider()
    st.info(f"Total entries: {len(book_df)} | **Total Fee: ${fee:.2f}**")
    
    paypal_btn = f"""
    <div id="paypal-button-container"></div>
    <script src="https://www.paypal.com/sdk/js?client-id=AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD&currency=USD"></script>
    <script>
        paypal.Buttons({{
            createOrder: function(data, actions) {{
                return actions.order.create({{
                    purchase_units: [{{ amount: {{ value: '{fee:.2f}' }} }}]
                }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    alert('Transaction completed by ' + details.payer.name.given_name);
                }});
            }}
        }}).render('#paypal-button-container');
    </script>
    """
    components.html(paypal_btn, height=500)

# Sidebar Contact
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.write("**Contact GDP Consultants**")
    st.write("📧 info@taxcalculator.lk")
    st.write("🌐 [www.taxcalculator.lk](http://www.taxcalculator.lk)")
