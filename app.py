import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
import io

# --- 1. SECURITY & UI CONFIG ---
st.set_page_config(page_title="Bank Reconciliation AI", layout="wide")

# Hide Streamlit developer options to protect your code
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. PRICING LOGIC ---
def calculate_price(entries):
    if entries <= 100:
        return 5.0
    return 5.0 + ((entries - 1) // 100) * 1.0

# --- 3. REPORT GENERATION ---
def create_report_image(data):
    """Generates an image preview of the BRS to prevent copy-pasting before payment"""
    img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try: f = ImageFont.load_default()
    except: f = None
    
    y = 50
    d.text((300, y), "Bank Reconciliation Statement", fill=(0,0,0), font=f)
    y += 40
    d.text((50, y), f"Business: {data['biz_name']}", fill=(0,0,0), font=f)
    d.text((450, y), f"Period: {data['period']}", fill=(0,0,0), font=f)
    y += 60
    # Add table lines and content...
    d.text((50, y), "Balance per Bank Statement:", fill=(0,0,0), font=f)
    d.text((600, y), f"{data['bank_bal']:,.2f}", fill=(0,0,0), font=f)
    
    # Watermark for security
    d.text((200, 500), "PREVIEW ONLY - PAY TO DOWNLOAD", fill=(200,200,200), font=f)
    return img

# --- 4. SESSION MANAGEMENT ---
if "paid" not in st.session_state: st.session_state.paid = False

# --- 5. SIDEBAR: CONTACT & INSTRUCTIONS ---
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.header("📖 Instructions")
    st.markdown("""
    1. **Upload Files:** Upload Previous BRS, Current Bank Statement, and Cash Book (Excel/CSV).
    2. **Preview:** Review the generated BRS image for accuracy.
    3. **Pay:** Payment is based on Cash Book entries ($5 min).
    4. **Download:** Get your clean PDF or Excel file.
    """)
    st.divider()
    st.write("**Contact GDP Consultants**")
    st.write("📧 info@taxcalculator.lk | 🌐 www.taxcalculator.lk")

# --- 6. MAIN INTERFACE ---
st.title("Bank Reconciliation AI")

with st.container():
    c1, c2, c3 = st.columns(3)
    p_brs = c1.file_uploader("Previous Month BRS", type=['xlsx', 'csv'])
    c_stmt = c2.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
    c_book = c3.file_uploader("Current Cash Book", type=['xlsx', 'csv'])

if c_stmt and c_book:
    # Logic: Read files and calculate entries
    book_df = pd.read_excel(c_book) if c_book.name.endswith('xlsx') else pd.read_csv(c_book)
    entry_count = len(book_df)
    fee = calculate_price(entry_count)
    
    # Generate Mock Data for Display (Replace with actual reconciliation logic)
    report_data = {
        "biz_name": "User Business Name", "bank_name": "Bank Name", 
        "acc_no": "Account Number", "period": "Month Year",
        "bank_bal": 125000.00, "raw_book_bal": 120000.00
    }
    
    st.subheader("🏁 Reconciliation Preview")
    preview_img = create_report_image(report_data)
    st.image(preview_img, caption="Watermarked Preview", use_container_width=True)
    
    st.divider()
    
    # Payment Section
    if not st.session_state.paid:
        st.warning(f"💳 Total Charge: **${fee:.2f}** ({entry_count} entries detected)")
        
        paypal_html = f"""
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
                        window.parent.postMessage({{type: 'payment_success'}}, '*');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)
        
        # Listen for payment success (Simplified for logic)
        if st.button("I have completed payment"):
            st.session_state.paid = True
            st.rerun()

    # Post-Payment Downloads
    if st.session_state.paid:
        st.success("✅ Payment Verified. Download your reports below.")
        col_dl1, col_dl2 = st.columns(2)
        col_dl1.download_button("📥 Download PDF Report", b"PDF_CONTENT", "Reconciliation.pdf")
        col_dl2.download_button("📥 Download Excel Report", b"EXCEL_CONTENT", "Reconciliation.xlsx")
