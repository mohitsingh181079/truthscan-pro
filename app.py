import streamlit as st
import requests
import re
from PyPDF2 import PdfReader

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

def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.lower()
    except:
        return ""

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

jd_text = st.text_area("Paste Job Description (JD)", placeholder="Ex: Need Data Analyst with Python, SQL, Excel, Power BI...")

uploaded_files = st.file_uploader("Upload 1 to 10 Resumes", type="pdf", accept_multiple_files=True)

if st.button("🚀 Scan Resumes"):
    if not user_name or not user_mobile:
        st.warning("Please enter Name and Mobile first!")
    elif not jd_text:
        st.warning("Please paste Job Description!")
    elif not uploaded_files:
        st.warning("Please upload at least 1 PDF!")
    elif len(uploaded_files) > 10:
        st.error("You can only upload max 10 resumes at once!")
    else:
        st.success(f"Analyzing {len(uploaded_files)} resume(s)...")
        results = []
        
        # Keywords for checking
        jd_keywords = re.findall(r'\w+', jd_text.lower())
        common_skills = ["python", "sql", "excel", "power bi", "tableau", "data analyst", "machine learning", "java", "react", "resume", "experience", "education", "project"]

        for pdf_file in uploaded_files:
            text = extract_text_from_pdf(pdf_file)
            
            if len(text) < 100:
                score = 10
                reason = "Not a valid resume / Scanned image or empty"
                status = "❌ Fake / Irrelevant"
            else:
                # Score logic
                matched = sum(1 for k in jd_keywords if len(k) > 3 and k in text)
                skill_matched = sum(1 for s in common_skills if s in text)
                
                score = min(95, (matched * 5) + (skill_matched * 8))
                
                # If JD is data analyst but PDF has class 10, cag, school
                irrelevant_words = ["class 10", "class 12", "cag", "school notes", "syllabus"]
                if any(w in text for w in irrelevant_words):
                    score = score - 50

                if score > 70:
                    status = "✅ Genuine"
                    reason = f"Matched {matched} JD keywords, {skill_matched} skills found"
                elif score > 40:
                    status = "⚠️ Suspicious"
                    reason = f"Low match: Only {matched} JD keywords"
                else:
                    status = "❌ Fake / Irrelevant"
                    reason = "Does not match JD, looks like notes or fake"

            score = max(5, score)
            final_line = f"{pdf_file.name}: {status} (Score: {score}/100) - {reason}"
            results.append(final_line)
            
            if "Genuine" in status:
                st.success(final_line)
            elif "Suspicious" in status:
                st.warning(final_line)
            else:
                st.error(final_line)

        final_result_text = " | ".join(results)
        save_to_sheet(user_name, user_mobile, final_result_text)
        st.balloons()
        st.info("Results saved securely! Check your Google Sheet.")