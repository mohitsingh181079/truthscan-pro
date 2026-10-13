
import streamlit as st
import PyPDF2
import random
import string
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="TruthScan PRO", page_icon="🔍", layout="centered")

# --- License Storage ---
CODES_FILE = "codes.json"
if os.path.exists(CODES_FILE):
    with open(CODES_FILE, "r") as f:
        try:
            ALL_CODES = json.load(f)
        except:
            ALL_CODES = {}
else:
    ALL_CODES = {}

# Default test code
if "TRUTHS-PRO-UALF8T" not in ALL_CODES:
    ALL_CODES["TRUTHS-PRO-UALF8T"] = {
        "limit": 100,
        "expiry": "2026-11-13",
        "plan": "PRO",
        "used": 0
    }

def save_codes():
    with open(CODES_FILE, "w") as f:
        json.dump(ALL_CODES, f, indent=2)

def generate_code(plan):
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"TRUTHS-{plan}-{suffix}"
    if plan == "PRO":
        expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        ALL_CODES[code] = {"limit": 100, "expiry": expiry, "plan": "PRO", "used": 0}
    elif plan == "AGENCY":
        expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        ALL_CODES[code] = {"limit": 9999, "expiry": expiry, "plan": "AGENCY", "used": 0}
    else:
        expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        ALL_CODES[code] = {"limit": 3, "expiry": expiry, "plan": "FREE", "used": 0}
    save_codes()
    return code

# --- UI ---
st.title("🔍 TruthScan PRO - Bulk Fake Resume Detector")
st.caption("India's first AI tool to detect fake resumes in bulk")
st.divider()

jd_text = st.text_area("📄 Paste Job Description (JD)", height=150)
uploaded_files = st.file_uploader("📤 Upload Resumes", type=["pdf"], accept_multiple_files=True)
license_key = st.text_input("Enter Your License Key (FREE users leave empty)")

# --- Validate License ---
plan = "FREE"
limit = 3
is_valid = False
message = ""

if license_key in ALL_CODES:
    data = ALL_CODES[license_key]
    expiry_date = datetime.strptime(data["expiry"], "%Y-%m-%d")
    if datetime.now() <= expiry_date and data["used"] < data["limit"]:
        plan = data["plan"]
        limit = data["limit"]
        is_valid = True
        message = f"✅ {plan} Active | Used: {data['used']}/{limit} | Expiry: {data['expiry']}"
        st.success(message)
    else:
        st.error("❌ License Expired or Limit Reached")
elif license_key == "":
    st.info("FREE Plan: 3 scans / month available")
else:
    st.error("❌ Invalid License Key")

# --- Scan Button ---
if st.button("🚀 Scan Resumes", type="primary", use_container_width=True):
    if not jd_text:
        st.warning("Please paste Job Description")
    elif not uploaded_files:
        st.warning("Please upload at least 1 PDF")
    else:
        if not is_valid and len(uploaded_files) > 3:
            st.error("🔒 FREE Limit: Only 3 scans per month. Buy PRO to continue.")
            st.stop()

        for pdf in uploaded_files:
            try:
                reader = PyPDF2.PdfReader(pdf)
                text = "".join([p.extract_text() or "" for p in reader.pages]).lower()
                is_fake = any(k in text for k in ["chemical bonding", "ncert", "class notes", "chapter"]) or len(text) < 300
                st.write(f"**{pdf.name}**")
                if is_fake:
                    st.error("❌ Fake / Irrelevant")
                else:
                    st.success("✅ Genuine Resume")
            except Exception as e:
                st.error(f"Error reading {pdf.name}")

        if is_valid:
            ALL_CODES[license_key]["used"] += len(uploaded_files)
            save_codes()
        st.balloons()

# --- PRICING PLANS WITH MONTH ---
st.divider()
st.subheader("💰 Pricing Plans")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**FREE - ₹0**")
    st.write("3 scans / month")
    st.write("30 Days Validity")

with col2:
    st.markdown("**PRO - ₹499**")
    st.write("100 scans / month")
    st.write("30 Days Validity")

with col3:
    st.markdown("**AGENCY - ₹3999**")
    st.write("Unlimited scans / month")
    st.write("30 Days Validity")

st.markdown("LinkedIn: https://www.linkedin.com/in/mohit-singh-6a9815415")

# --- ADMIN PANEL ---
query_params = st.query_params
if query_params.get("admin") == "true":
    st.divider()
    st.subheader("Admin Panel - Code Generator")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Generate PRO (100/30 Days)"):
            code = generate_code("PRO")
            st.code(code)
            st.success("PRO Code Generated")
    with c2:
        if st.button("Generate AGENCY (Unlimited)"):
            code = generate_code("AGENCY")
            st.code(code)
            st.success("AGENCY Code Generated")
    with c3:
        if st.button("Generate FREE (3/30 Days)"):
            code = generate_code("FREE")
            st.code(code)
            st.success("FREE Code Generated")

    st.write("All Codes Database:")
    st.json(ALL_CODES)
