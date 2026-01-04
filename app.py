import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
import io

# --- 1. ADMIN & SECURITY CONFIG ---
st.set_page_config(page_title="Bank Reconciliation AI", layout="wide", page_icon="🏦")

# Security: Hide "View Source", "Deploy", and Streamlit Menu
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .main {background-color: #f9f9f9;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. COMMERCIAL LOGIC ---
def calculate_price(entries):
    """USD 5 for first 100, then USD 1 for every 100 extra"""
    if entries <= 100: return 5.0
    return 5.0 + ((entries - 1) // 100) * 1.0

def generate_secure_preview(data):
    """Generates a detailed image preview (Standard BRS Format)"""
    img = Image.new('RGB', (1000, 1400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Header Section
    y = 60
    d.text((350, y), f"{data.get('biz_name', 'BUSINESS NAME')}", fill=(0,0,0))
    y += 40
    d.text((380, y), "Bank Reconciliation Statement", fill=(0,0,0))
    y += 60
    
    # Details
    d.text((100, y), f"Bank: {data.get('bank', 'N/A')}", fill=(0,0,0))
    d.text((650, y), f"Period: {data.get('period', 'N/A')}", fill=(0,0,0))
    y += 30
    d.text((100, y), f"Account No: {data.get('acc_no', 'N/A')}", fill=(0,0,0))
    y += 70

    # Part A: Adjusted Cash Book
    d.text((100, y), "Part A: Adjusted Cash Book Balance", fill=(0,0,0))
    y += 40
    d.text((120, y), "Unadjusted Balance per Cash Book", fill=(0,0,0))
    d.text((800, y), f"{data['raw_book_bal']:,.2f}", fill=(0,0,0))
    y += 30
    for item in data['unadjusted_entries']:
        d.text((140, y), f" - {item['desc']} ({item['ref']})", fill=(50,50,50))
        d.text((800, y), f"{item['amt']:,.2f}", fill=(0,0,0))
        y += 30
    y += 10
    d.text((120, y), "ADJUSTED CASH BOOK BALANCE", fill=(0,0,0))
    d.text((800, y), f"{data['adj_book_bal']:,.2f}", fill=(0,0,0))
    y += 60

    # Part B: Reconciliation
    d.text((100, y), "Part B: Reconciliation to Bank Statement", fill=(0,0,0))
    y += 40
    d.text((120, y), "Balance per Bank Statement", fill=(0,0,0))
    d.text((800, y), f"{data['bank_bal']:,.2f}", fill=(0,0,0))
    y += 40
    d.text((120, y), "Add: Unrealised Deposits (Lodgements not cleared)", fill=(0,0,0))
    y += 30
    for dep in data['transit']:
        d.text((140, y), f" - {dep['date']} | {dep['ref']}", fill=(50,50,50))
        d.text((800, y), f"{dep['amt']:,.2f}", fill=(0,0,0))
        y += 30
    y += 20
    d.text((120, y), "Less: Unpresented Cheques", fill=(0,0,0))
    y += 30
    for chq in data['unpresented']:
        d.text((140, y), f" - {chq['date']} | {chq['ref']}", fill=(50,50,50))
        d.text((800, y), f"({chq['amt']:,.2f})", fill=(0,0,0))
        y += 30

    # Watermark
    d.text((250, 700), "PREVIEW ONLY - SECURE PAYMENT REQUIRED", fill=(210,210,210))
    return img

# --- 3. UI & SIDEBAR ---
with st.sidebar:
    try: st.image("logo-removebg-preview.png")
    except: st.warning("Logo file missing on GitHub")
    
    st.header("📖 Instructions")
    st.markdown("""
    1. **Upload Files:** Upload Prev BRS, Current Statement, and Cash Book.
    2. **Review Image:** Verify the watermarked preview for accuracy.
    3. **Payment:** Fee is calculated based on entry count.
    4. **Download:** Get your final PDF/Excel upon payment.
    """)
    st.divider()
    st.write("**GDP Consultants**")
    st.write("📧 info@taxcalculator.lk")
    st.write("🌐 [www.taxcalculator.lk](http://www.taxcalculator.lk)")

# --- 4. MAIN WORKFLOW ---
st.title("Bank Reconciliation AI")
st.caption("Professional BRS Automation powered by GDP Consultants")

c1, c2, c3 = st.columns(3)
prev_f = c1.file_uploader("Previous Month BRS", type=['xlsx', 'csv'])
stmt_f = c2.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
book_f = c3.file_uploader("Current Cash Book", type=['xlsx', 'csv'])

if stmt_f and book_f:
    # Read files
    try:
        book_df = pd.read_excel(book_f) if book_f.name.endswith('xlsx') else pd.read_csv(book_f)
        entry_count = len(book_df)
        fee = calculate_price(entry_count)
        
        # (AI LOGIC: Matching & Adjusting occurs here)
        # Placeholder data for report generation
        report_data = {
            "biz_name": "ABC PRIVATE LIMITED", "bank": "COMMERCIAL BANK", "acc_no": "9900881122",
            "period": "December 2025", "raw_book_bal": 45000.00, "adj_book_bal": 44850.00, "bank_bal": 41000.00,
            "unadjusted_entries": [{"desc": "Bank Charges", "ref": "SVC", "amt": -150.00}],
            "transit": [{"date": "2025-12-31", "ref": "DEP-101", "amt": 5000.00}],
            "unpresented": [{"date": "2025-12-25", "ref": "CHQ-504", "amt": 1150.00}]
        }

        st.divider()
        st.subheader("🏁 Automated BRS Preview")
        preview = generate_secure_preview(report_data)
        st.image(preview, use_container_width=True)

        # Payment Block
        st.info(f"🧾 Entries: {entry_count} | **Total Service Fee: USD {fee:.2f}**")
        
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
                        alert('Payment Verified! Downloading reports...');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_btn, height=500)

    except Exception as e:
        st.error(f"Error reading data: {e}")
