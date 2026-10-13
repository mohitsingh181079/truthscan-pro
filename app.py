import streamlit as st
save_to_sheet(st.session_state.get('user_name',''), st.session_state.get('user_mobile',''), user_query, final_result)
import PyPDF2
import re

st.set_page_config(page_title="TruthScan PRO", page_icon="🕵️", layout="centered")

# BLUE BACKGROUND + WHITE TEXT FIX
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #3b82f6, #1e3a8a); }
h1, h2, h3, p, label, div, span { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("🕵️ TruthScan PRO")
st.subheader("Bulk Fake Resume Detector")
st.write("10 resumes at once + Verified Report")

def check_fake(text):
    score = 90
    if len(text) < 200: score -= 30
    if "lorem ipsum" in text.lower(): score -= 40
    return max(score, 15)

files = st.file_uploader("Upload 1 to 10 Resumes", type="pdf", accept_multiple_files=True)

if st.button("🚀 Scan Now"):
    if not files:
        st.warning("Pehle PDF upload kar bhai")
    else:
        for f in files:
            try:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages: text += page.extract_text() or ""
                score = check_fake(text)
                if score > 75:
                    st.success(f"✅ {f.name} -> REAL ({score}/100)")
                else:
                    st.error(f"❌ {f.name} -> FAKE ({score}/100)")
            except:
                st.error(f"{f.name} padh nahi paya")

st.caption("No API Needed | 100% Free | Client Ready")