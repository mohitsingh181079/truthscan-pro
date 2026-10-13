import streamlit as st
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="TruthScan Pro", page_icon="✅", layout="wide")

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "Mmoo@2026#Secure")
LICENSE_KEY = st.secrets.get("LICENSE_KEY", "Mmoo@2026#Secure")

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return ""

def get_match_score(resume_text, jd_text):
    # Rule 1: JD is too short like "King" -> 0% Fake
    if len(jd_text.strip()) < 10:
        return 0.0

    # Rule 2: File is not a resume
    resume_keywords = ["experience", "education", "skills", "project", "resume", "objective", "work", "university"]
    if not any(word in resume_text.lower() for word in resume_keywords):
        return -1

    # Rule 3: Real Matching Logic
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([resume_text.lower(), jd_text.lower()])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return score * 100

with st.sidebar:
    st.header("🔑 Pro License")
    user_license = st.text_input("Enter License Key", type="password")
    license_ok = False
    if not user_license:
        st.warning("Please enter License Key to start")
    elif user_license!= LICENSE_KEY and user_license!= ADMIN_PASSWORD:
        st.error("❌ Invalid License Key")
    else:
        st.success("✅ Pro License Activated")
        license_ok = True

st.title("✅ TruthScan Pro - Resume Truth Scanner")
st.markdown("---")

st.subheader("1. Paste Job Description (JD)")
jd_text = st.text_area("JD", height=180, placeholder="Type any JD here. If wrong JD, it will show Fake...", label_visibility="collapsed")

st.subheader("2. Upload Resumes (Max 3 PDFs)")
uploaded_files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

if uploaded_files:
    if not license_ok:
        st.error("Please enter valid License Key in sidebar.")
        st.stop()
    if len(uploaded_files) > 3:
        st.error("❌ Max 3 files only")
        st.stop()
    if not jd_text.strip():
        st.warning("⚠️ Paste JD first")
        st.stop()

    st.divider()
    st.subheader("3. Results")

    for file in uploaded_files:
        resume_text = extract_text_from_pdf(file)
        if not resume_text.strip():
            st.error(f"**{file.name}** - ❌ Empty PDF")
            continue

        score = get_match_score(resume_text, jd_text)

        # FINAL DECISION - This is what you asked for
        if score == -1:
            st.error(f"**{file.name}** - ❌ Fake / Irrelevant File (Not a Resume)")
        elif score < 35: # < 35% means JD is WRONG for this resume
            st.error(f"**{file.name}** - ❌ Fake / Irrelevant - Only {score:.0f}% match. JD does not match this resume.")
        else: # >= 35% means JD is CORRECT
            st.success(f"**{file.name}** - ✅ Genuine Resume - {score:.0f}% Match with JD")