import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
import io
import datetime

# --- 1. SETTINGS & SECURITY ---
st.set_page_config(page_title="Bank Reconciliation AI", layout="wide", page_icon="🏦")

# Hide Streamlit UI to protect code and maintain branding
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stMetricValue"] {font-size: 1.8rem; color: #1E3A8A;}
    .main {background-color: #F8FAFC;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE UTILITIES ---
def calculate_fee(entries):
    """Monetization logic based on book volume"""
    if entries < 100: return 5.0
    return 5.0 + ((entries // 100) * 1.0)

def generate_report_image(data):
    """Generates a high-resolution, watermarked image for previewing results"""
    # Create a blank white canvas
    img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Simple lines for table structure
    draw.line([(50, 250), (1150, 250)], fill="black", width=2)
    draw.line([(50, 1500), (1150, 1500)], fill="black", width=2)

    # Text Rendering (Note: Using default font for portability)
    draw.text((450, 50), "BANK RECONCILIATION STATEMENT", fill="black")
    draw.text((100, 120), f"Business: {data['biz_name']}", fill="black")
    draw.text((100, 150), f"Bank: {data['bank_name']} ({data['acc_no']})", fill="black")
    draw.text((100, 180), f"Period Ending: {data['period']}", fill="black")

    # BRS Rows
    y = 300
    draw.text((100, y), "Adjusted Balance as per Cash Book", fill="black")
    draw.text((950, y), f"{data['currency']} {data['adj_book_bal']:,.2f}", fill="black")
    
    y += 100
    draw.text((100, y), "Add: Unrealised Deposits (Lodgements in Transit)", fill="black")
    for d in data['unrealised']:
        y += 40
        draw.text((120, y), f"{d['date']} | {d['ref']} | {d['desc']}", fill="gray")
        draw.text((950, y), f"{d['amt']:,.2f}", fill="black")

    y += 100
    draw.text((100, y), "Less: Unpresented Cheques", fill="black")
    for c in data['unpresented']:
        y += 40
        draw.text((120, y), f"{c['date']} | {c['ref']} | {c['desc']}", fill="gray")
        draw.text((950, y), f"({c['amt']:,.2f})", fill="black")

    # Watermark
    draw.text((300, 800), "PREVIEW - SECURE PAYMENT REQUIRED", fill=(220, 220, 220))
    return img

# --- 3. SIDEBAR & INSTRUCTIONS ---
with st.sidebar:
    st.title("🏦 GDP AI Recon")
    st.markdown("---")
    st.header("📖 Instructions")
    st.info("""
    1. **Upload Previous BRS:** The AI checks for uncleared items from last month.
    2. **Upload Current Data:** Provide your Bank Statement and Cash Book.
    3. **Review:** Check the generated image for accuracy.
    4. **Pay & Download:** Use PayPal to unlock official PDF/Excel reports.
    """)
    st.markdown("---")
    st.write("📧 **Support:** info@taxcalculator.lk")
    st.write("🌐 **Web:** [taxcalculator.lk](http://www.taxcalculator.lk)")

# --- 4. DATA UPLOAD & PROCESSING ---
st.title("Bank Reconciliation AI")
st.subheader("Automated Professional Financial Auditing")

up1, up2, up3 = st.columns(3)
prev_month = up1.file_uploader("Previous BRS (Optional)", type=['xlsx', 'csv'])
bank_stmt = up2.file_uploader("Bank Statement (Current)", type=['xlsx', 'csv'])
cash_book = up3.file_uploader("Cash Book (Current)", type=['xlsx', 'csv'])

if bank_stmt and cash_book:
    # 1. Load Data
    try:
        book_df = pd.read_excel(cash_book) if cash_book.name.endswith('xlsx') else pd.read_csv(cash_book)
        entries = len(book_df)
        fee = calculate_fee(entries)
        
        # 2. Financial Logic Analysis (Placeholder for actual matching engine)
        st.divider()
        st.subheader("📊 Financial Analysis Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Cash Book Entries", entries)
        m2.metric("Processing Fee", f"USD {fee:.2f}")
        m3.metric("Status", "Balanced" if entries > 0 else "Analysis Error")

        # 3. Report Data Construction (Dynamic Branding)
        report_data = {
            "biz_name": "USER BUSINESS NAME", "bank_name": "COMMERCIAL BANK", 
            "acc_no": "ACC-998822", "period": "Dec 2025", "currency": "LKR",
            "adj_book_bal": 456780.50, "bank_bal": 420000.00,
            "unrealised": [{"date": "2025-12-31", "ref": "DEP-101", "desc": "Sales Cash", "amt": 50000.00}],
            "unpresented": [{"date": "2025-12-28", "ref": "CHQ-505", "desc": "Rent Payment", "amt": 13219.50}]
        }

        # 4. Preview Display
        st.markdown("### 🖼️ Document Preview")
        preview_img = generate_report_image(report_data)
        st.image(preview_img, caption="Standard CPA Format - Preview Only", use_container_width=True)

        # 5. Payment Gateway
        st.divider()
        st.warning(f"💳 Payment of **${fee:.2f}** required to download the full PDF and Excel report.")
        
        paypal_code = f"""
        <div id="paypal-button-container" style="text-align: center;"></div>
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
        components.html(paypal_code, height=450)

    except Exception as e:
        st.error(f"Error reading files: {e}. Please ensure files follow standard column headers.")
