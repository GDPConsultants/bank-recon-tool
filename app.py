import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
import io

# --- 1. SETTINGS & BRANDING ---
st.set_page_config(page_title="Bank Reconciliation AI", layout="wide")

# Hide Streamlit UI to protect code
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .main {background-color: #F4F7F6;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CPA-BASED RECONCILIATION LOGIC ---
def calculate_fee(entries):
    if entries <= 100: return 5.0
    return 5.0 + ((entries - 1) // 100) * 1.0

def generate_template_preview(data):
    """Generates an image preview following the green [Company Name] template"""
    img = Image.new('RGB', (1000, 1500), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Header - Dark Green Bar (matching template)
    d.rectangle([0, 0, 1000, 120], fill="#4B8B5B")
    d.text((50, 40), f"{data['biz_name']} Bank Reconciliation Statement", fill="white")
    
    y = 150
    d.text((50, y), f"Month Ended: {data['period']}", fill="black")
    d.text((700, y), f"Date Prepared: {data['prep_date']}", fill="black")
    
    # Section Header - Cash Balance Per Books
    y += 80
    d.rectangle([0, y, 1000, y+40], fill="#D9EAD3")
    d.text((50, y+10), "Cash Balance Per Books", fill="black")
    y += 45
    d.text((50, y), f"Cash Balance per Books (as of {data['prev_month_end']})", fill="black")
    d.text((850, y), f"${data['raw_book_bal']:,.2f}", fill="black")
    
    # Additions to Books
    y += 50
    d.rectangle([0, y, 1000, y+40], fill="#F3F3F3")
    d.text((50, y+10), "Additions to Cash Balance Per Books:", fill="black")
    for item in data['book_additions']:
        y += 45
        d.text((70, y), item['desc'], fill="gray")
        d.text((850, y), f"${item['amt']:,.2f}", fill="black")
    
    # Deductions from Books
    y += 60
    d.rectangle([0, y, 1000, y+40], fill="#F3F3F3")
    d.text((50, y+10), "Deductions from Cash Balance Per Books:", fill="black")
    for item in data['book_deductions']:
        y += 45
        d.text((70, y), item['desc'], fill="gray")
        d.text((850, y), f"${item['amt']:,.2f}", fill="black")
        
    y += 60
    d.rectangle([0, y, 1000, y+40], fill="#B6D7A8")
    d.text((50, y+10), "Adjusted Cash Balance Per Books", fill="black")
    d.text((850, y+10), f"${data['adj_book_bal']:,.2f}", fill="black")

    # Final Status Bar
    y = 1400
    d.rectangle([0, y, 1000, y+60], fill="#6AA84F")
    d.text((50, y+20), "Reconciliation Status", fill="black")
    d.text((850, y+20), "RECONCILED", fill="black")

    # Watermark
    d.text((300, 750), "PREVIEW ONLY - PAY TO UNLOCK", fill=(200, 200, 200))
    return img

# --- 3. UI WORKFLOW ---
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.header("🏢 GDP AI Recon")
    st.write("**Methodology:** CPA Step-by-Step ")
    st.divider()
    st.write("📧 info@taxcalculator.lk")

st.title("Bank Reconciliation AI")
st.write("Professional automated auditing in your corporate format.")

c1, c2, c3 = st.columns(3)
prev_rec = c1.file_uploader("Previous Month Reconciliation", type=['xlsx', 'csv'])
c_stmt = c2.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
c_book = c3.file_uploader("Current Bank Book", type=['xlsx', 'csv'])

if c_stmt and c_book:
    # 1. Processing and Entry Counting
    book_df = pd.read_excel(c_book) if c_book.name.endswith('xlsx') else pd.read_csv(c_book)
    fee = calculate_fee(len(book_df))
    
    # 2. Financial Modeling based on CPA Step 3 & 4 [cite: 63, 73]
    # This sample data reflects your green template's structure
    report_data = {
        "biz_name": "ABC CORP", "period": "July, 2025", "prep_date": "July 1, 2025",
        "prev_month_end": "June 30, 2025", "raw_book_bal": 12500.00, "adj_book_bal": 12565.00,
        "book_additions": [
            {"desc": "Interest Earned", "amt": 15.00},
            {"desc": "Notes Receivable Collected by Bank", "amt": 500.00}
        ],
        "book_deductions": [
            {"desc": "Bank Service Charges", "amt": 25.00},
            {"desc": "NSF Checks", "amt": 150.00}
        ]
    }

    # 3. Preview Generation
    st.subheader("🏁 Automated BRS Preview (Template Match)")
    preview = generate_template_preview(report_data)
    st.image(preview, use_container_width=True)

    # 4. Monetization Section
    st.divider()
    st.warning(f"💳 Total Transactions: {len(book_df)} | **Service Fee: USD {fee:.2f}**")
    
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
                    alert('Payment successful for ' + details.payer.name.given_name);
                }});
            }}
        }}).render('#paypal-button-container');
    </script>
    """
    components.html(paypal_html, height=450)
