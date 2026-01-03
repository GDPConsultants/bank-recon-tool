import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import streamlit.components.v1 as components
from io import BytesIO

# --- 1. BRANDING & UI PROTECTION ---
st.set_page_config(
    page_title="Bank Reconciliation AI", 
    layout="wide", 
    page_icon="logo-removebg-preview.png"
)

# HIDE SOURCE CODE & STREAMLIT BRANDING
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# SIDEBAR: Logo & Contact Info
st.sidebar.image("logo-removebg-preview.png", use_container_width=True)
st.sidebar.title("Bank Reconciliation AI")
st.sidebar.markdown("""
---
### 📞 Support & Inquiries
**GDP Consultants** 📧 [info@taxcalculator.lk](mailto:info@taxcalculator.lk)  
🌐 [www.taxcalculator.lk](http://www.taxcalculator.lk)
""")

# --- 2. CONFIG & SECRETS ---
# Use Streamlit Secrets for these to keep them hidden from GitHub!
API_KEY = st.secrets["INTERNAL_API_KEY"]
MODEL_ID = st.secrets["INTERNAL_MODEL_ID"]
ACCESS_PASSWORD = "ReconPro2026"

# --- 3. SESSION STATE ---
if "reconcile_count" not in st.session_state: st.session_state.reconcile_count = 0
if "authenticated" not in st.session_state: st.session_state.authenticated = False

# --- 4. PROTECTED APP GATEWAY ---
if st.session_state.reconcile_count >= 1 and not st.session_state.authenticated:
    st.title("🔓 Premium Access Required")
    st.info("You've used your free trial. Please unlock the full version to continue.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Pay via PayPal")
        # Replace 'YOUR_CLIENT_ID' with the one you provided earlier
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
        pwd_input = st.text_input("Enter Access Key:", type="password")
        if st.button("Unlock Unlimited Access"):
            if pwd_input == ACCESS_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
    st.stop()

# --- 5. MAIN USER DASHBOARD ---
st.title("🏦 Bank Reconciliation AI")

# USER INSTRUCTIONS & VIDEO
with st.expander("🎥 View Video Tutorial & Instructions", expanded=True):
    col_v, col_i = st.columns([2, 1])
    with col_v:
        # Placeholder for your video - Replace with your actual hosted video link or local file
        st.video("https://www.youtube.com/watch?v=yVV_t_Tewvs") 
    with col_i:
        st.markdown("""
        **Simple 3-Step Process:**
        1. **Upload:** Statement (PDF/Excel) & Bank Book (Excel).
        2. **Process:** AI extracts and matches data automatically.
        3. **Report:** Preview results and download your PDF.
        """)

# UPLOADER SECTION
u1, u2 = st.columns(2)
with u1:
    stmt_file = st.file_uploader("Bank Statement", type=['pdf', 'xlsx', 'csv'])
with u2:
    book_file = st.file_uploader("Bank Book", type=['xlsx', 'csv'])

if st.button("🚀 Run AI Reconciliation"):
    if stmt_file and book_file:
        st.session_state.reconcile_count += 1
        with st.spinner("AI is processing your financial records..."):
            # (Your logic for conversion and matching continues here)
            st.success("Analysis Complete!")
    else:
        st.error("Please provide both documents.")
