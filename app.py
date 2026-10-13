import streamlit as st
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="TruthScan Pro", page_icon="✅", layout="centered")

st.markdown("""
<style>
 .stButton > button { height: 55px; font-size: 18px!important; font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

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
    jd_text = jd_text.strip().lower()
    resume_lower = resume_text.lower()

    if len(jd_text) < 2:
        return 0.0

    # 1. Resume hi nahi hai to Fake
    resume_keywords = ["experience", "education", "skills", "project", "resume", "objective", "work", "university", "summary"]
    if not any(word in resume_lower for word in resume_keywords):
        return -1

    # 2. NAYA LOGIC - Agar JD ka ek bhi shabd resume me hai to seedha Genuine (Numpy ke liye)
    jd_words = jd_text.split()
    # Single skill like "Numpy" -> check direct
    for word in jd_words:
        if len(word) >= 3 and word in resume_lower:
            return 90.0 # Direct mil gaya to 90%

    # 3. TF-IDF se detailed match
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
        tfidf = vectorizer.fit_transform([resume_lower, jd_text])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return score * 100
    except:
        return 0.0

st.title("✅ TruthScan Pro")
st.divider()

st.subheader("1. Paste Job Description (JD)")
jd_text = st.text_area("JD", height=180, placeholder="e.g., Data Analyst with Python, SQL, Power BI...", label_visibility="collapsed")

st.write("")
st.subheader("2. Upload Resumes (Max 10 PDFs)")
uploaded_files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

if uploaded_files:
    st.info(f"📁 {len(uploaded_files)} file(s) selected")

st.write("")
check_button = st.button("🔍 ENTER - CHECK RESUMES", type="primary", use_container_width=True)

if check_button:
    if not jd_text.strip():
        st.warning("⚠️ JD likho pehle")
        st.stop()
    if not uploaded_files:
        st.warning("⚠️ Resume upload karo")
        st.stop()
    if len(uploaded_files) > 10:
        st.error(f"❌ Max 10 files. Tumne {len(uploaded_files)} kiye")
        st.stop()

    st.divider()
    st.subheader("3. Results")
    for file in uploaded_files:
        resume_text = extract_text_from_pdf(file)
        if not resume_text.strip():
            st.error(f"**{file.name}** - ❌ PDF Read Nahi Hua")
            continue
        score = get_match_score(resume_text, jd_text)
        if score == -1:
            st.error(f"**{file.name}** - ❌ Fake / Not a Resume")
        elif score < 25:
            st.error(f"**{file.name}** - ❌ Fake / Low Match - {score:.0f}%")
        else:
            st.success(f"**{file.name}** - ✅ Genuine - {score:.0f}% Match")