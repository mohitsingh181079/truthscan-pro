import streamlit as st
import PyPDF2

st.set_page_config(page_title="TruthScan PRO", page_icon="🔍", layout="centered")

st.title("🔍 TruthScan PRO - Bulk Fake Resume Detector")
st.caption("India's first AI tool to detect fake resumes in bulk for HRs and Recruiters.")
st.divider()

# --- MAIN TOOL ---
jd_text = st.text_area("📄 Paste Job Description (JD)", placeholder="Ex: Need Data Analyst with Python, SQL, Excel...", height=120)

uploaded_files = st.file_uploader("📤 Upload 1 to 10 Resumes", type="pdf", accept_multiple_files=True)

if st.button("🚀 Scan Resumes", type="primary", use_container_width=True):
    if not jd_text:
        st.warning("Please paste Job Description first.")
    elif not uploaded_files:
        st.warning("Please upload at least 1 resume.")
    else:
        for pdf_file in uploaded_files:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            text_lower = text.lower()
            fake_keywords = ["class notes", "chemical bonding", "ncert", "chapter", "exercise", "question bank", "syllabus"]
            is_fake = any(k in text_lower for k in fake_keywords)
            
            st.divider()
            st.write(f"**File: {pdf_file.name}**")
            if is_fake or len(text_lower) < 200:
                st.error("❌ Fake / Irrelevant - This is study notes, not a resume")
            else:
                st.success("✅ Correct / Relevant Resume")

st.divider()

# --- PRICING SECTION - YE RAHEGA ---
st.subheader("💰 Pricing Plans")
st.markdown("**🆓 FREE - ₹0**")
st.write("• 3 scans / month")
st.markdown("**🔥 PRO - ₹499 / month**")
st.write("• 100 scans / month + Verified Report")
st.markdown("**🚀 AGENCY - ₹3999 / month**")
st.write("• Unlimited Scans")

st.subheader("📞 Get PRO Access")
st.markdown("Contact Founder on LinkedIn: https://www.linkedin.com/in/mohit-humbe/")
st.write("DM for PRO Access")

st.divider()
st.caption("Built with ❤️ in India | TruthScan PRO v1.0")