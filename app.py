import streamlit as st
import PyPDF2
import random, string
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="TruthScan PRO", page_icon="🔍", layout="centered")

# --- DATABASE ---
CODES_FILE = "codes.json"

# Load existing codes or create default
if os.path.exists(CODES_FILE):
    with open(CODES_FILE, "r") as f:
        try:
            ALL_CODES = json.load(f)
        except:
            ALL_CODES = {}
else:
    ALL_CODES = {}

# Ensure at least one default code for demo like your screenshot
if "TRUTHS-PRO-UALF8T" not in ALL_CODES:
    ALL_CODES["TRUTHS-PRO-UALF8T"] = {"limit": 100, "expiry": "2026-11-12", "plan": "PRO", "used": 0}

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

# --- MAIN APP UI ---
st.title("🔍 TruthScan PRO - Bulk Fake Resume Detector")

jd_text = st.text_area("Paste Job Description")
uploaded_files = st.file_uploader("Upload Resumes", type="pdf", accept_multiple_files=True)
license_key = st.text_input("Enter Your License Key")

# Check License
current_plan = "FREE"
current_limit = 3
if license_key in ALL_CODES:
    data = ALL_CODES[license_key]
    exp_date = datetime.strptime(data["expiry"], "%Y-%m-%d")
    if datetime.now() > exp_date:
        st.error(f"❌ Code Expired on {data['expiry']}")
    elif data["used"] >= data["limit"]:
        st.error(f"❌ Limit Over - {data['used']}/{data['limit']} used")
    else:
        current_plan = data["plan"]
        current_limit = data["limit"]
        st.success(f"✅ {current_plan} Active - {data['used']}/{data['limit']} used | Expiry: {data['expiry']}")

if st.button("🚀 Scan Resumes", type="primary", use_container_width=True):
    if not uploaded_files:
        st.warning("Please upload PDFs")
    else:
        for pdf_file in uploaded_files:
            try:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                lower_text = text.lower()

                # Fake detection
                fake_keywords = ["chemical bonding", "class notes", "ncert", "chapter", "syllabus", "physics", "biology", "question bank"]
                is_fake = any(k in lower_text for k in fake_keywords) or len(lower_text) < 300

                st.divider()
                st.write(f"**File: {pdf_file.name}**")
                if is_fake:
                    st.error("❌ Fake / Irrelevant - This is study notes, not a resume")
                else:
                    st.success("✅ Correct / Relevant Resume")
            except Exception as e:
                st.error(f"Error reading {pdf_file.name}: {e}")

        if license_key in ALL_CODES:
            ALL_CODES[license_key]["used"] += len(uploaded_files)
            save_codes()

# --- PRICING ---
st.divider()
st.subheader("💰 Pricing Plans")
col1, col2, col3 = st.columns(3)
col1.markdown("**FREE - ₹0**\n\n3 scans / month")
col2.markdown("**PRO - ₹499**\n\n100 scans / month")
col3.markdown("**AGENCY - ₹3999**\n\nUnlimited Scans")

st.markdown("Contact Founder on LinkedIn: https://www.linkedin.com/in/mohit-singh-6a9815415")
st.write("DM for PRO Access")
st.caption("Built with ❤️ in India | TruthScan PRO v1.0")

# --- ADMIN PANEL - EXACTLY LIKE YOUR SCREENSHOT ---
st.divider()
# This panel will ONLY show when you open with?admin=true
params = st.query_params
if params.get("admin") == "true":
    st.subheader("Admin Panel - Code Generator")

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Generate PRO (100/30 Days)"):
            new_code = generate_code("PRO")
            st.success(new_code)
            st.code(new_code)
    with b2:
        if st.button("Generate AGENCY (Unlimited)"):
            new_code = generate_code("AGENCY")
            st.success(new_code)
            st.code(new_code)
    with b3:
        if st.button("Generate FREE (3/30 Days)"):
            new_code = generate_code("FREE")
            st.success(new_code)
            st.code(new_code)

    st.subheader("All Generated Codes")
    st.json(ALL_CODES)