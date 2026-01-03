import streamlit as st
import pandas as pd
from thefuzz import fuzz
import streamlit.components.v1 as components
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="ReconPro Sri Lanka", layout="wide")
ACCESS_PASSWORD = "ReconPro2026" 

# --- SESSION STATE INITIALIZATION ---
if "reconcile_count" not in st.session_state:
    st.session_state.reconcile_count = 0  # Tracks trial attempts
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- TRIAL & PAYMENT GATE ---
# If they used their 1 trial and aren't paid, show the paywall
if st.session_state.reconcile_count >= 1 and not st.session_state.authenticated:
    st.warning("⚠️ Your free trial attempt has ended.")
    st.title("🔐 Unlock Unlimited Reconciliations")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### 1. Pay via PayPal")
        # Your PayPal Button
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
        components.html(paypal_html, height=450)

    with col_b:
        st.write("### 2. Enter Access Key")
        pwd_input = st.text_input("Enter the key from your receipt:", type="password")
        if st.button("Unlock Unlimited Access"):
            if pwd_input == ACCESS_PASSWORD:
                st.session_state.authenticated = True
                st.success("Access Granted! You can now use the tool as much as you like.")
                st.rerun()
            else:
                st.error("Invalid Key.")
    st.stop()

# --- THE TOOL ---
st.title("🏦 Bank Reconciliation Tool")
if not st.session_state.authenticated:
    st.info(f"🎁 Free Trial Active: You have used {st.session_state.reconcile_count}/1 free attempts.")

up1, up2 = st.columns(2)
with up1:
    stmt_file = st.file_uploader("Upload Bank Statement (CSV)", type="csv")
with up2:
    book_file = st.file_uploader("Upload Bank Book (CSV)", type="csv")

if st.button("Run Reconciliation"):
    if stmt_file and book_file:
        # Increment trial counter
        st.session_state.reconcile_count += 1
        
        # Load and Process Data
        df_stmt = pd.read_csv(stmt_file)
        df_book = pd.read_csv(book_file)
        
        # Net Amount Calculation
        df_stmt['Amount'] = df_stmt['Debit'].fillna(0) - df_stmt['Credit'].fillna(0)
        df_book['Amount'] = df_book['Debit'].fillna(0) - df_book['Credit'].fillna(0)

        # Merge Logic
        recon = pd.merge(df_stmt, df_book, on=['Reference', 'Amount'], how='outer', indicator=True, suffixes=('_Bank', '_Book'))
        
        # Display Results
        st.write("### Results Preview")
        st.dataframe(recon[recon['_merge'] == 'both'].head(10)) # Show first 10 matches
        
        # Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            recon[recon['_merge'] == 'both'].to_excel(writer, sheet_name='Matched', index=False)
            recon[recon['_merge'] == 'left_only'].to_excel(writer, sheet_name='Missing_In_Book', index=False)
        
        st.download_button("📥 Download Full Report", output.getvalue(), "Recon_Report.xlsx")
        
        if not st.session_state.authenticated:
            st.warning("This was your 1 free trial. To run more, please subscribe.")
    else:
        st.error("Please upload both files first.")
