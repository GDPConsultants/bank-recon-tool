import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
import streamlit.components.v1 as components
from io import BytesIO

# --- 1. BRANDING & SECURITY CONFIGURATION ---
st.set_page_config(
    page_title="Bank Reconciliation AI", 
    layout="wide", 
    page_icon="logo-removebg-preview.png"
)

# Hiding "View Source", GitHub Link, and Main Menu for security
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            #GithubIcon {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Adding your logo to the sidebar
st.logo("logo-removebg-preview.png", icon_image="logo-removebg-preview.png")

# --- 2. NANONETS & PASSWORD SETTINGS ---
NANONETS_API_KEY = "YOUR_API_KEY"
MODEL_ID = "YOUR_MODEL_ID"
ACCESS_PASSWORD = "ReconPro2026"

def convert_pdf_to_csv(uploaded_file):
    url = f'https://app.nanonets.com/api/v2/OCR/Model/{MODEL_ID}/LabelFile/'
    data = {'file': uploaded_file}
    response = requests.post(url, auth=requests.auth.HTTPBasicAuth(NANONETS_API_KEY, ''), files=data)
    return pd.DataFrame(response.json()['result'][0]['prediction']) if response.status_code == 200 else None

# --- 3. SESSION STATE & PAYWALL ---
if "reconcile_count" not in st.session_state: st.session_state.reconcile_count = 0
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if st.session_state.reconcile_count >= 1 and not st.session_state.authenticated:
    st.title("🔒 Bank Reconciliation AI - Premium")
    st.image("logo-removebg-preview.png", width=150)
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Upgrade to Unlimited")
        paypal_html = f"YOUR_PAYPAL_BUTTON_CODE_HERE" # Insert your button code
        components.html(paypal_html, height=450)
    with col_b:
        pwd_input = st.text_input("Access Key:", type="password")
        if st.button("Unlock"):
            if pwd_input == ACCESS_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
    st.stop()

# --- 4. MAIN INTERFACE ---
st.image("logo-removebg-preview.png", width=100)
st.title("Bank Reconciliation AI")

col1, col2 = st.columns(2)
with col1:
    stmt_file = st.file_uploader("Bank Statement (PDF/XLSX/CSV)", type=['pdf', 'xlsx', 'csv'])
with col2:
    book_file = st.file_uploader("Bank Book (XLSX/CSV)", type=['xlsx', 'csv'])

if st.button("🚀 Run AI Reconciliation"):
    if stmt_file and book_file:
        st.session_state.reconcile_count += 1
        # (Processing Logic here)
        st.success("Reconciliation Complete!")
