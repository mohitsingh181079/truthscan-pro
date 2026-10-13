
import streamlit as st
import PyPDF2
import random, string
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="TruthScan PRO", page_icon="🔍", layout="centered")

# --- DATABASE FILE ---
CODES_FILE = "codes.json"
if os.path.exists(CODES_FILE):
    with open(CODES_FILE, "r") as f:
        ALL_CODES = json.load(f)
else:
    ALL_CODES = {
        "TRUTHS-PRO-UALF8T": {"limit": 100, "expiry": "2026-11-12", "plan": "PRO", "used": 0}
    }

def save_codes():
    with open(CODES_FILE, "w") as f:
        json.dump(ALL_CODES, f, indent=2)

def generate_code(plan):
    prefix = f"TRUTHS-{plan}-"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = prefix + suffix

    if plan == "PRO":
        ALL_CODES[code] = {"limit": 100, "expiry": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "plan": "PRO", "used": 0}
    elif plan == "AGENCY":
        ALL_CODES[code] = {"limit": 9999, "expiry": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"), "plan": "AGENCY", "used": 0}
    else: # FREE
        ALL_CODES[code] = {"limit": 3, "expiry": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "plan": "FREE", "used": 0}

    save_codes()
    return code

# --- SESSION ---
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

st.title("🔍 TruthScan PRO")
st.divider()

# --- MAIN APP ---
jd = st.text_area("Paste Job Description")
files = st.file_uploader("Upload Resumes", type="pdf", accept_multiple_files=True)
license_key = st.text_input("Enter Your License Key")

# Check license
plan = "FREE"
limit = 3
if license_key in ALL_CODES:
    data = ALL_CODES[license_key]
    expiry = datetime.strptime(data["expiry"], "%Y-%m-%d")
    if datetime.now() > expiry:
        st.error("❌ Code Expired")
    elif data["used"] >= data["limit"]:
        st.error("❌ Limit Over")
    else:
        plan = data["plan"]
        limit = data["limit"]
        st.success(f"✅ {plan} Activated - {limit} scans, Expiry: {data['expiry']}")

if st.button("🚀 Scan Resumes", type="primary", use_container_width=True):
    if files:
        if st.session_state.scan_count + len(files) > limit and plan == "FREE" and license_key not in ALL_CODES:
            st.error(f"🔒 FREE limit 3 over. Buy PRO.")
            st.stop()

        for pdf in files:
            reader = PyPDF2.PdfReader(pdf)
            text = "".join([p.extract_text() or "" for p in reader.pages]).lower()
            is_fake = any(x in text for x in ["class notes", "chemical bonding", "ncert", "chapter"])
            st.write(f"**{pdf.name}**")
            st.error("❌ Fake / Irrelevant") if is_fake else st.success("✅ Correct Resume")

        if license_key in ALL_CODES:
            ALL_CODES[license_key]["used"] += len(files)
            save_codes()

# --- PRICING ---
st.divider()
st.subheader("💰 Pricing Plans")
c1, c2, c3 = st.columns(3)
c1.markdown("**FREE - ₹0**\n3 scans / month")
c2.markdown("**PRO - ₹499**\n100 scans / month")
c3.markdown("**AGENCY - ₹3999**\nUnlimited Scans")

st.markdown("Contact Founder on LinkedIn: https://www.linkedin.com/in/mohit-singh-6a9815415")
st.write("DM for PRO Access")
st.caption("Built with ❤️ in India | TruthScan PRO v1.0")

# --- ADMIN PANEL (YE TERA WALA HAI) ---
st.divider()
st.subheader("Admin Panel - Code Generator")

admin_pass = st.text_input("Admin Password", type="password")
if admin_pass == "mohit123": # tu password change kar sakta hai
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate PRO (100/30 Days)"):
            code = generate_code("PRO")
            st.success(code)
    with col2:
        if st.button("Generate AGENCY (Unlimited)"):
            code = generate_code("AGENCY")
            st.success(code)
    with col3:
        if st.button("Generate FREE (3/30 Days)"):
            code = generate_code("FREE")
            st.success(code)

    st.subheader("All Generated Codes")
    st.json(ALL_CODES)
