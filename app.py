import streamlit as st
import PyPDF2

st.set_page_config(page_title="TruthScan PRO", page_icon="🔍", layout="centered")

if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

FREE_LIMIT = 3

st.title("🔍 TruthScan PRO - Bulk Fake Resume Detector")
st.caption("India's first AI tool to detect fake resumes in bulk")
st.divider()

st.info(f"Scans Used: {st.session_state.scan_count}/{FREE_LIMIT} Free scans left")

jd_text = st.text_area("📄 Paste Job Description (JD)", height=120)
uploaded_files = st.file_uploader("📤 Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)

if st.button("🚀 Scan Resumes", type="primary", use_container_width=True):
    if not jd_text:
        st.warning("Please paste Job Description.")
    elif not uploaded_files:
        st.warning("Please upload resumes.")
    else:
        num_files = len(uploaded_files)
        if st.session_state.scan_count + num_files > FREE_LIMIT:
            st.error(f"🔒 FREE Limit Over! You used {st.session_state.scan_count}/{FREE_LIMIT}")
            st.markdown("""
            ### 🚀 Upgrade to Continue
            **You have finished your 3 free scans.**
            
            **PRO - ₹499 / month** - 100 Scans
            **AGENCY - ₹3999 / month** - Unlimited Scans
            
            **Contact to Buy:** https://www.linkedin.com/in/mohit-singh-6a9815415
            """)
            st.stop()

        for pdf_file in uploaded_files:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join([p.extract_text() or "" for p in reader.pages]).lower()
            is_fake = any(k in text for k in ["chemical bonding", "class notes", "ncert", "chapter", "syllabus"]) or len(text) < 250
            
            st.divider()
            st.write(f"**File: {pdf_file.name}**")
            if is_fake:
                st.error("❌ Fake / Irrelevant Resume")
            else:
                st.success("✅ Correct / Relevant Resume")
        
        st.session_state.scan_count += num_files
        st.balloons()

st.divider()
st.subheader("💰 Pricing Plans")
c1, c2, c3 = st.columns(3)
c1.markdown("**FREE - ₹0**\n\n3 scans / month")
c2.markdown("**PRO - ₹499**\n\n100 scans / month")
c3.markdown("**AGENCY - ₹3999**\n\nUnlimited Scans")

st.divider()
st.subheader("📞 Get PRO Access")
st.markdown("DM on LinkedIn: https://www.linkedin.com/in/mohit-singh-6a9815415")
st.caption("Built with ❤️ in India | TruthScan PRO v1.0")