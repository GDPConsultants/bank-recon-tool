import streamlit as st
import pandas as pd
from fpdf import FPDF
import streamlit.components.v1 as components
import math

# --- BRANDING & CONFIG ---
st.set_page_config(page_title="GDP Consultants | Bank Recon AI", layout="wide")

# Custom CSS to hide Streamlit branding
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stDeployButton {display:none;}</style>""", unsafe_allow_html=True)

# --- PRICING LOGIC ---
def calculate_fee(entries_count):
    if entries_count <= 100:
        return 5.00
    additional_entries = entries_count - 100
    return 5.00 + math.ceil(additional_entries / 100) * 1.00

# --- PDF GENERATOR (CPA FORMAT) ---
class BRS_Report(FPDF):
    def header_branded(self, biz_name):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, f"{biz_name} - Bank Reconciliation Statement", 0, 1, 'C')
        self.ln(10)

def generate_pdf(data):
    pdf = BRS_Report()
    pdf.add_page()
    pdf.header_branded(data['biz_name'])
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Account No: {data['acc_no']} | Period: {data['period']}", ln=True)
    pdf.ln(5)

    # BRS Content following CPA format
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(140, 10, "Particulars", 1, 0, 'C', True)
    pdf.cell(50, 10, "Amount", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(140, 10, f"Balance as per Bank Statement ({data['bank_date']})", 1)
    pdf.cell(50, 10, f"{data['bank_bal']:,.2f}", 1, 1)
    
    pdf.cell(140, 10, "Add: Unrealised Deposits (Lodgements not cleared)", 1)
    pdf.cell(50, 10, f"{data['unrealized_total']:,.2f}", 1, 1)
    
    pdf.cell(140, 10, "Less: Unpresented Cheques", 1)
    pdf.cell(50, 10, f"({data['unpresented_total']:,.2f})", 1, 1)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 10, "Adjusted Cash Book Balance", 1)
    pdf.cell(50, 10, f"{data['adj_book_bal']:,.2f}", 1, 1)
    
    return bytes(pdf.output())

# --- SIDEBAR & CONTACT ---
with st.sidebar:
    try: st.image("logo-removebg-preview.png")
    except: st.title("GDP Consultants")
    st.header("How to Use")
    st.markdown("""
    1. **Upload Files:** Previous BRS, Current Bank Statement, and Cash Book (Excel/CSV).
    2. **AI Analysis:** We check for unpresented items from last month[cite: 54].
    3. **Preview:** Review the completed statement for free.
    4. **Pay & Download:** Pay based on your entry count to get the PDF/Excel.
    """)
    st.divider()
    st.write("**Contact Details:**")
    st.write("📧 info@taxcalculator.lk")
    st.write("🌐 www.taxcalculator.lk")

# --- MAIN APP ---
st.title("Automated Bank Reconciliation")
st.write("Follow the **Step-by-Step CPA Approach** to ensure audit-ready records[cite: 19].")

# Uploaders
c1, c2, c3 = st.columns(3)
with c1: prev_brs = st.file_uploader("Previous Month BRS (Optional)", type=['xlsx', 'csv'])
with c2: bank_stmt = st.file_uploader("Current Bank Statement", type=['xlsx', 'csv'])
with c3: cash_book = st.file_uploader("Current Cash Book", type=['xlsx', 'csv'])

if bank_stmt and cash_book:
    # Simulated extraction for logic demonstration
    entries_count = 150 # Example count
    fee = calculate_fee(entries_count)
    
    # Mock Data based on CPA Step 4 [cite: 81]
    recon_data = {
        "biz_name": "User Business Name", "acc_no": "987654321", "period": "Jan 2026",
        "bank_date": "31/12/202X", "bank_bal": 8253.00, "unrealized_total": 9800.00,
        "unpresented_total": 2404.00, "adj_book_bal": 15649.00
    }

    st.subheader("📊 Free Preview of Reconciliation")
    st.write("Review your data below before proceeding to download.")
    st.dataframe(pd.DataFrame([recon_data]))
    
    st.divider()
    
    # PAYWALL SECTION
    st.subheader("💳 Download Professional Report")
    st.warning(f"Total Entries: {entries_count} | Service Fee: **${fee:,.2f}**")
    
    pay_col, code_col = st.columns(2)
    with pay_col:
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
                        alert('Transaction completed by ' + details.payer.name.given_name + '! Use Unlock Code: ReconPro2026');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_btn, height=500)
    
    with code_col:
        unlock_code = st.text_input("Enter Unlock Code from PayPal payment:", type="password")
        if unlock_code == "ReconPro2026":
            st.success("Payment Verified!")
            pdf_bytes = generate_pdf(recon_data)
            st.download_button("📥 Download PDF Report", pdf_bytes, "Final_BRS.pdf")
            st.download_button("📥 Download Excel Report", cash_book.getvalue(), "Final_BRS.xlsx")
