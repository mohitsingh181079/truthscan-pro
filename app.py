import streamlit as st
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="TruthScan Pro", page_icon="✅", layout="wide")

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
    if len(jd_text.strip()) < 10:
        return 0.0
    resume_keywords = ["experience", "education", "skills", "project", "resume", "objective", "work", "university"]
    if not any(word in resume_text.lower() for word in resume_keywords):
        return -1
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([resume_text.lower(), jd_text.lower()])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return score * 100

st.title("✅ TruthScan Pro - Resume Truth Scanner")
st.markdown("---")

st.subheader("1. Paste Job Description (JD)")
jd_text = st.text_area("JD", height=180, placeholder="e.g., Data Analyst with Python, SQL, Power BI...", label_visibility="collapsed")

st.subheader("2. Upload Resumes (Max 3 PDFs)")
uploaded_files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

if uploaded_files:
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
        if score == -1:
            st.error(f"**{file.name}** - ❌ Fake / Irrelevant File (Not a Resume)")
        elif score < 35:
            st.error(f"**{file.name}** - ❌ Fake / Irrelevant - Only {score:.0f}% match")
        else:
            st.success(f"**{file.name}** - ✅ Genuine Resume - {score:.0f}% Match")