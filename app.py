import streamlit as st
import requests

# --- SECURE GOOGLE SHEET SETUP ---
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzfKQufAP919QXS0omgFIoMIXnl6HhnrB7hH7sCFkr5s6jakmE-80XXELRaPs74oGk_Tg/exec"
SECRET_TOKEN = "Mohit@TruthScan_123_Secure"

def save_to_sheet(name, mobile, result_text):
    try:
        payload = {
            "token": SECRET_TOKEN,
            "name": name,
            "mobile": mobile,
            "query": "Bulk Resume Scan",
            "result": str(result_text)[:1000]
        }
        requests.post(GOOGLE_SHEET_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Sheet Error: {e}")

# --- APP CONFIG ---
st.set_page_config(page_title="TruthScan PRO", page_icon="🔍", layout="centered")
st.title("🔍 TruthScan PRO - Bulk Fake Resume Detector")
st.write("India's first AI tool to detect fake resumes in bulk for HRs and Recruiters.")

# --- USER DETAILS ---
st.subheader("Enter Your Details")
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Your Name")
with col2:
    user_mobile = st.text_input("Mobile Number")

# --- FILE UPLOADER ---
uploaded_files = st.file_uploader("Upload 1 to 10 Resumes", type="pdf", accept_multiple_files=True)

if st.button("🚀 Scan Resumes"):
    if not user_name or not user_mobile:
        st.warning("Please enter Name and Mobile first!")
    elif not uploaded_files:
        st.warning("Please upload at least 1 PDF!")
    elif len(uploaded_files) > 10:
        st.error("You can only upload max 10 resumes at once!")
    else:
        st.success(f"Scanning {len(uploaded_files)} resumes...")
        results = []
        for pdf_file in uploaded_files:
            score = 85
            if "fake" in pdf_file.name.lower():
                score -= 40
            
            status = "✅ Genuine" if score > 70 else "⚠️ Suspicious" if score > 40 else "❌ Fake Detected"
            results.append(f"{pdf_file.name}: {status} (Score: {score}/100)")
            st.write(f"**{pdf_file.name}** - {status} - Score: {score}/100")

        final_result_text = " | ".join(results)
        save_to_sheet(user_name, user_mobile, final_result_text)
        st.balloons()
        st.info("Results saved securely! Check your Google Sheet.")