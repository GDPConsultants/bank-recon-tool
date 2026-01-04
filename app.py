import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io
import xlsxwriter

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

# --- 2. CORE CALCULATIONS ---
def calculate_price(entries):
    if entries <= 100:
        return 5.0
    return 5.0 + ((entries - 1) // 100) * 1.0

def create_brs_image(data):
    """Generates a high-resolution image of the ACTUAL BRS results for preview."""
    img = Image.new('RGB', (850, 1100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Simple lines and headers
    d.rectangle([20, 20, 830, 1080], outline=(0, 0, 0), width=2)
    y = 60
    d.text((300, y), "BANK RECONCILIATION STATEMENT", fill=(0,0,0))
    y += 50
    d.text((50, y), f"Business: {data['biz_name']}")
    d.text((50, y+20), f"Bank: {data['bank_name']} | Account: {data['acc_no']}")
    d.text((550, y), f"Period: {data['period']}")
    y += 80

    # BRS Content
    content = [
        ("Balance as per Bank Statement", f"{data['currency']} {data['bank_bal']:,.2f}"),
        ("ADD: Unrealised Deposits", ""),
    ]
    for item in data['unrealised']:
        content.append((f"   Ref: {item['ref']} ({item['date']})", f"{item['amt']:,.2f}"))
    
    content.append(("LESS: Unpresented Cheques", ""))
    for item in data['unpresented']:
        content.append((f"   Chq: {item['ref']} ({item['date']})", f"({item['amt']:,.2f})"))
    
    content.append(("Adjusted Bank Balance", f"{data['currency']} {data['final_bal']:,.2f}"))

    for label, val in content:
        d.text((70, y), label, fill=(0,0,0))
        d.text((650, y), val, fill=(0,0,0))
        y += 30

    # WATERMARK
    d.text((150, 500), "PREVIEW ONLY - PAYMENT REQUIRED", fill=(220,220,220))
    
    # Save to buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def create_pdf_report(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Bank Reconciliation Statement", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Business: {data['biz_name']}", ln=True)
    pdf.cell(0, 10, f"Balance: {data['currency']} {data['final_bal']:,.2f}", ln=True)
    return bytes(pdf.output())

# --- 3. MAIN APP INTERFACE ---
st.title("Bank Reconciliation AI")
st.write("Professional Audit Automation | Powered by GDP Consultants")

with st.sidebar:
    st.header("📞 Contact Details")
    st.write("GDP Consultants")
    st.write("Email: info@taxcalculator.lk")
    st.write("Web: www.taxcalculator.lk")
    st.divider()
    st.info("Pricing: $5 for first 100 entries, +$1 per 100 thereafter.")

# File Uploaders
col_up1, col_up2, col_up3 = st.columns(3)
prev_month = col_up1.file_uploader("Previous BRS (Excel/CSV)", type=['xlsx', 'csv'])
curr_stmt = col_up2.file_uploader("Bank Statement (Excel/CSV)", type=['xlsx', 'csv'])
curr_book = col_up3.file_uploader("Cash Book (Excel/CSV)", type=['xlsx', 'csv'])

if curr_stmt and curr_book:
    # 1. Process Data
    try:
        book_df = pd.read_excel(curr_book) if curr_book.name.endswith('xlsx') else pd.read_csv(curr_book)
        entry_count = len(book_df)
        fee = calculate_price(entry_count)
        
        # --- PLACEHOLDER RECONCILIATION DATA (Replace with your logic) ---
        report_data = {
            "biz_name": "Sample Client Ltd", "bank_name": "Commercial Bank",
            "acc_no": "9988776655", "period": "Dec 2025", "currency": "USD",
            "bank_bal": 8253.00, "final_bal": 16449.00,
            "unrealised": [{"ref": "LODG-1", "date": "31/12", "amt": 9800.00}],
            "unpresented": [{"ref": "10546", "date": "22/12", "amt": 830.00}]
        }

        # 2. Show Image Preview
        st.subheader("🏁 Completed Reconciliation Preview")
        img_preview = create_brs_image(report_data)
        st.image(img_preview, caption="Verify details before payment.")

        # 3. Monetization Section
        st.divider()
        st.error(f"💳 Service Fee: ${fee:.2f} (Detected {entry_count} entries)")
        
        # PayPal Button
        paypal_btn = f"""
            <div id="paypal-button-container"></div>
            <script src="https://www.paypal.com/sdk/js?client-id=AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD&currency=USD"></script>
            <script>
                paypal.Buttons({{
                    createOrder: function(data, actions) {{
                        return actions.order.create({{ purchase_units: [{{ amount: {{ value: '{fee}' }} }}] }});
                    }},
                    onApprove: function(data, actions) {{
                        return actions.order.capture().then(function(details) {{
                            alert('Transaction completed by ' + details.payer.name.given_name);
                        }});
                    }}
                }}).render('#paypal-button-container');
            </script>
        """
        st.components.v1.html(paypal_btn, height=550)
        
        # 4. Download (Unlocked after Manual Confirmation or API Hook)
        if st.checkbox("I have successfully paid and want to download"):
            st.success("Reports Unlocked")
            pdf_data = create_pdf_report(report_data)
            st.download_button("📥 Download PDF", pdf_data, "BRS_Report.pdf", "application/pdf")

    except Exception as e:
        st.error(f"System Error: {str(e)}")
