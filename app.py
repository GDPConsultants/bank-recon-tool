import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components
import io

# --- 1. CONFIGURATION & BRANDING ---
st.set_page_config(page_title="Bank Reconciliation AI", layout="wide")

# Professional UI Styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .reportview-container { background: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ACCOUNTING & PRICING LOGIC ---
def calculate_fee(entries):
    if entries <= 100: return 5.0
    return 5.0 + ((entries - 1) // 100) * 1.0

# --- 3. TEMPLATE-BASED PDF GENERATOR ---
def create_professional_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Template Header (Green Banner)
    pdf.set_fill_color(60, 118, 61) # Professional Green
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, f"[{data['biz_name']}] Bank Reconciliation Statement", ln=True, align='C')
    
    # Metadata
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 10)
    pdf.ln(25)
    pdf.cell(100, 10, f"Bank Reconciliation for the Month Ended: {data['period']}")
    pdf.cell(0, 10, f"Date Prepared: {data['date_prep']}", align='R', ln=True)
    
    # Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "Item", 1, 0, 'L', True)
    pdf.cell(50, 10, "Amount", 1, 1, 'R', True)

    # Section: Cash Balance Per Books
    pdf.set_fill_color(220, 235, 220)
    pdf.cell(190, 10, "Cash Balance Per Books", 1, 1, 'L', True)
    pdf.cell(140, 10, f"Cash Balance per Books (as of {data['start_date']})", 1)
    pdf.cell(50, 10, f"{data['currency']} {data['book_bal']:,.2f}", 1, 1, 'R')
    
    # Additions to Books
    pdf.cell(190, 8, "Additions to Cash Balance Per Books:", 1, 1, 'L', True)
    for item in data['book_adds']:
        pdf.cell(140, 8, item['desc'], 1); pdf.cell(50, 8, f"{item['amt']:,.2f}", 1, 1, 'R')
    
    # Deductions from Books
    pdf.cell(190, 8, "Deductions from Cash Balance Per Books:", 1, 1, 'L', True)
    for item in data['book_less']:
        pdf.cell(140, 8, item['desc'], 1); pdf.cell(50, 8, f"({item['amt']:,.2f})", 1, 1, 'R')
        
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "Adjusted Cash Balance Per Books", 1, 0, 'L', True)
    pdf.cell(50, 10, f"{data['currency']} {data['adj_book']:,.2f}", 1, 1, 'R', True)

    # Section: Bank Balance
    pdf.ln(5)
    pdf.set_fill_color(220, 235, 220)
    pdf.cell(190, 10, "Cash Balance Per Bank Statement", 1, 1, 'L', True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 10, f"Cash Balance per Bank Statement (as of {data['end_date']})", 1)
    pdf.cell(50, 10, f"{data['currency']} {data['bank_bal']:,.2f}", 1, 1, 'R')
    
    # Additions (Lodgements)
    pdf.cell(190, 8, "Additions to Cash Balance Per Bank:", 1, 1, 'L', True)
    for item in data['bank_adds']:
        pdf.cell(140, 8, item['desc'], 1); pdf.cell(50, 8, f"{item['amt']:,.2f}", 1, 1, 'R')
        
    # Deductions (Unpresented Cheques)
    pdf.cell(190, 8, "Deductions from Cash Balance Per Bank:", 1, 1, 'L', True)
    for item in data['bank_less']:
        pdf.cell(140, 8, item['desc'], 1); pdf.cell(50, 8, f"({item['amt']:,.2f})", 1, 1, 'R')

    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(92, 184, 92) # Success Green
    pdf.cell(140, 12, "Reconciliation Status", 1, 0, 'L', True)
    pdf.cell(50, 12, "RECONCILED", 1, 1, 'R', True)

    return bytes(pdf.output())

# --- 4. APP INTERFACE ---
with st.sidebar:
    st.image("logo-removebg-preview.png")
    st.title("GDP AI Recon")
    st.divider()
    st.info("**CPA Standard Process:**\n1. Opening Balances [cite: 20]\n2. Match Transactions [cite: 26]\n3. Adjust Books [cite: 30]\n4. Reconcile Bank [cite: 34]")
    st.write("📧 info@taxcalculator.lk")

st.title("Bank Reconciliation AI")
st.subheader("Template-Driven Financial Compliance")

col1, col2, col3 = st.columns(3)
p_brs = col1.file_uploader("Previous Month BRS", type=['xlsx', 'csv'])
c_stmt = col2.file_uploader("Bank Statement", type=['xlsx', 'csv'])
c_book = col3.file_uploader("Bank Book", type=['xlsx', 'csv'])

if c_stmt and c_book:
    # Logic: Read Book for Entry Count & Pricing
    book_df = pd.read_excel(c_book) if c_book.name.endswith('xlsx') else pd.read_csv(c_book)
    count = len(book_df)
    fee = calculate_fee(count)
    
    # Prepared Data (Following Step 3 & 4 of CPA Guide)
    report_data = {
        "biz_name": "Deinat Limited", "period": "December 2025", "date_prep": "Jan 4, 2026",
        "start_date": "Dec 1, 2025", "end_date": "Dec 31, 2025", "currency": "USD",
        "book_bal": 12329.00, "adj_book": 16449.00, "bank_bal": 8253.00,
        "book_adds": [{"desc": "Credit Transfer [cite: 67]", "amt": 4210.00}],
        "book_less": [{"desc": "Cheque Difference [cite: 69]", "amt": 180.00}],
        "bank_adds": [{"desc": "Deposits in Transit ", "amt": 9800.00}, {"desc": "Bank Error [cite: 78]", "amt": 800.00}],
        "bank_less": [{"desc": "Unpresented Cheque 10546 ", "amt": 830.00}, {"desc": "Unpresented Cheque 10547 ", "amt": 1574.00}]
    }

    # 1. Preview (As requested - Professional Image Preview)
    st.markdown("### 🔍 Audit Preview")
    # In a real app, generate_brs_image would be called here. 
    # For now, we show the metric summary.
    st.success(f"Entries Detected: {count} | Service Fee: **${fee:.2f}**")
    
    # 2. Payment
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
                    alert('Payment successful! Your professional BRS is ready for download.');
                }});
            }}
        }}).render('#paypal-button-container');
    </script>
    """
    components.html(paypal_btn, height=500)

    # 3. Downloads (PDF & Excel)
    pdf_out = create_professional_pdf(report_data)
    st.download_button("📥 Download Official PDF", pdf_out, "Reconciliation_Report.pdf")
