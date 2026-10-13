import streamlit as st
import PyPDF2
import random, string
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="TruthScan PRO", page_icon="🔍", layout="centered")

CODES_FILE = "codes.json"
if os.path.exists(CODES_FILE):
    with open(CODES_FILE, "r") as f:
        try:
            ALL_CODES = json.load(f)
        except:
            ALL_CODES = {}
else:
    ALL_CODES = {}

if "TRUTHS-PRO-UALF8T" not in ALL_CODES:
    ALL_CODES["TRUTHS-PRO-UALF8T"] = {"limit": 100, "expiry": "2026-11-12", "plan": "PRO", "used": 0}

def save_codes():
    with open(CODES_FILE, "w") as f:
        json.dump(ALL_CODES, f, indent=2)

def generate_code(plan):
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"TRUTHS-{plan}-{suffix}"
    if plan == "PRO":
        ALL_CODES[code] = {"limit": 100, "expiry": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "plan": "PRO", "used": 0}
    elif plan == "AGENCY":
        ALL_CODES[code] = {"limit": 9999, "expiry": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"), "plan": "AGENCY", "used": 0}
    else:
        ALL_CODES[code] = {"limit": 3, "expiry": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), "plan": "FREE", "used": 0}
    save_codes()
    return code

# --- USER APP ---
st.title("🔍 TruthScan PRO")
jd = st.text_area("Paste Job Description")
files = st.file_uploader("Upload Resumes", type="pdf", accept_multiple_files=True)
license_key = st.text_input("Enter Your License Key (FREE users leave empty)")

plan = "FREE"
limit = 3
if license_key in ALL_CODES:
    d = ALL_CODES[license_key]
    if datetime.now() <= datetime.strptime(d["expiry"], "%Y-%m-%d") and d["used"] < d["limit"]:
        plan = d["plan"]
        limit = d["limit"]
        st.success(f"✅ {plan} Active | {d['used']}/{d['limit']} | Expiry: {d['expiry']}")

if st.button("🚀 Scan Resumes", type="primary", use_container_width=True):
    if files:
        for pdf in files:
            reader = PyPDF2.PdfReader(pdf)
            text = "".join([p.extract_text() or "" for p in reader.pages]).lower()
            is_fake = any(x in text for x in ["chemical bonding", "class notes", "ncert"]) or len(text) < 300
            st.write(f"**{pdf.name}**")
            st.error("❌ Fake / Irrelevant") if is_fake else st.success("✅ Correct Resume")
        if license_key in ALL_CODES:
            ALL_CODES[license_key]["used"] += len(files)
            save_codes()

# Pricing
st.divider()
st.subheader("💰 Pricing Plans")
a,b,c = st.columns(3)
a.write("**FREE - ₹0** - 3 scans")
b.write("**PRO - ₹499** - 100 scans")
c.write("**AGENCY - ₹3999** - Unlimited")
st.markdown("LinkedIn: https://www.linkedin.com/in/mohit-singh-6a9815415")

# --- ADMIN PANEL - ONLY FOR YOU ---
params = st.query_params
if params.get("admin") == "true":
    st.divider()
    st.subheader("Admin Panel - Code Generator")
    x,y,z = st.columns(3)
    with x:
        if st.button("Generate PRO (100/30 Days)"):
            st.code(generate_code("PRO"))
    with y:
        if st.button("Generate AGENCY (Unlimited)"):
            st.code(generate_code("AGENCY"))
    with z:
        if st.button("Generate FREE (3/30 Days)"):
            st.code(generate_code("FREE"))

    st.subheader("All Generated Codes")
    st.json(ALL_CODES)