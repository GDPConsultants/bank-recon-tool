# 🏦 Bank Reconciliation AI

**Bank Reconciliation AI** is a professional-grade automation tool designed to streamline financial accounting. Using advanced AI (Nanonets), it extracts data from PDF bank statements and matches them against your internal bank book records in seconds.

---

## ✨ Key Features
* **Multi-Format Support:** Upload Bank Statements in **PDF, XLSX, or CSV**.
* **AI Extraction:** Powered by **Nanonets OCR** to accurately read scanned or digital PDF statements.
* **Smart Matching:** Uses **Exact** and **Fuzzy Logic** to pair transactions even with minor description typos.
* **One-Trial System:** Allow users to try the tool once before requiring a premium unlock.
* **Secure Paywall:** Integrated **PayPal** payment gateway for global access.
* **Professional Reports:** Export finalized reconciliations as branded **PDF Reports**.

---

## 🛠️ Setup Instructions

### 1. Prerequisites
* A **Nanonets** account ([app.nanonets.com](https://app.nanonets.com)) to get your API Key and Model ID.
* A **PayPal Developer** account to get your Client ID for payments.

### 2. File Structure
Ensure your GitHub repository has the following files:
* `app.py`: The main application code.
* `requirements.txt`: List of Python dependencies.
* `logo-removebg-preview.png`: Your brand logo.
* `.streamlit/config.toml`: Custom UI settings to hide developer menus.

### 3. Deployment
1. Connect your **Private GitHub Repository** to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Add your **Secret Keys** (Nanonets API Key) in the Streamlit "Secrets" settings rather than hardcoding them for maximum security.
3. Deploy!

---

## 🔑 Administrative Details
* **Current Access Key:** `ReconPro2026` 
* **Trial Limit:** 1 Attempt (Session-based)
* **Payment Amount:** $10.00 USD (Adjustable in `app.py`)

---

## 📖 User Instructions
1. **Upload Files:** Drag and drop your Bank Statement (left) and Bank Book (right).
2. **Processing:** Wait for the AI to parse the PDF data.
3. **Review:** Check the "Results Preview" to see matched and missing items.
4. **Export:** Click "Download Official PDF Report" to save your results.
5. **Unlock:** If you have used your trial, follow the PayPal prompts to receive your Access Key.

---

## 🛡️ Security & Privacy
This repository is configured to hide "View Source" and GitHub links from end-users. For full protection, always keep this repository **Private** on GitHub.

---
© 2026 Bank Reconciliation AI. All rights reserved.
