import streamlit as st
import pandas as pd
from thefuzz import fuzz
import streamlit.components.v1 as components
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="ReconPro Sri Lanka", layout="wide")
ACCESS_PASSWORD = "ReconPro2026"  # The password you give customers after they pay

# --- PAYPAL & AUTHENTICATION UI ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🏦 Bank Reconciliation Pro")
    st.subheader("Automate your accounting in seconds.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.write("### 1. Pay to Unlock")
        st.write("Get instant access for just $10.00 USD.")
        # PayPal Button Component
        paypal_html = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id=AaXH1xGEvvmsTOUgFg_vWuMkZrAtD0HLzas87T-Hhzn0esGcceV0J9lGEg-ptQlQU0k89J3jyI8MLzQD&currency=USD"></script>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '10.00' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        alert('Success! Your Access Key is: {ACCESS_PASSWORD}');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)

    with col_b:
        st.write("### 2. Enter Access Key")
        pwd_input = st.text_input("Enter the key you received after payment:", type="password")
        if st.button("Unlock Tool"):
            if pwd_input == ACCESS_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Key. Please complete the PayPal payment.")
    st.stop()

# --- ACTUAL TOOL CODE (Runs only after payment) ---
st.title("✅ ReconPro Dashboard")
st.sidebar.success("Account Active")

with st.sidebar:
    st.header("Format Guide")
    st.write("Upload CSV files with these columns:")
    st.code("Date, Description, Reference, Debit, Credit")
    st.markdown("[Convert PDF to CSV Here](https://nanonets.com/bank-statement-converter)")

# File Uploaders
up1, up2 = st.columns(2)
with up1:
    stmt_file = st.file_uploader("Upload Bank Statement", type="csv")
with up2:
    book_file = st.file_uploader("Upload Bank Book", type="csv")

if stmt_file and book_file:
    df_stmt = pd.read_csv(stmt_file)
    df_book = pd.read_csv(book_file)

    # Calculate net amount
    df_stmt['Amount'] = df_stmt['Debit'].fillna(0) - df_stmt['Credit'].fillna(0)
    df_book['Amount'] = df_book['Debit'].fillna(0) - df_book['Credit'].fillna(0)

    # Reconciliation Logic
    recon = pd.merge(df_stmt, df_book, on=['Reference', 'Amount'], how='outer', indicator=True, suffixes=('_Bank', '_Book'))
    
    matched = recon[recon['_merge'] == 'both']
    missing_book = recon[recon['_merge'] == 'left_only']
    missing_bank = recon[recon['_merge'] == 'right_only']

    # Show results
    st.write("### Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Perfect Matches", len(matched))
    c2.metric("Missing in Book", len(missing_book))
    c3.metric("Pending in Bank", len(missing_bank))

    # Download Report
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        matched.to_excel(writer, sheet_name='Matched', index=False)
        missing_book.to_excel(writer, sheet_name='Unrecorded', index=False)
    
    st.download_button("📥 Download Full Report", output.getvalue(), "Recon_Report.xlsx")
