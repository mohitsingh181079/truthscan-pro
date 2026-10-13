import streamlit as st
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="TruthScan Pro", page_icon="✅", layout="centered")

# --- RESPONSIVE CSS FOR MOBILE + LAPTOP ---
st.markdown("""
<style>
    /* Mobile + Laptop dono pe button bada */
   .stButton > button {
        height: 55px;
        font-size: 18px!important;
        font-weight: bold;
        border-radius: 10px;
    }
    /* Text area bada */
   .stTextArea textarea {
        font-size: 16px!important;
    }
    /* Mobile pe extra padding */
    @media (max-width: 768px) {
       .block-container {
            padding-top: 1rem!important;
        }
    }
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
    if len(jd_text.strip()) < 10:
        return 0.0
    resume_keywords = ["experience", "education", "skills", "project", "resume", "objective", "work", "university"]
    if not any(word in resume_text.lower() for word in resume_keywords):
        return -1
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text.lower(), jd_text.lower()])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return score * 100
    except:
        return 0.0

st.title("✅ TruthScan Pro")
st.caption("Resume Truth Scanner - Mobile & Laptop Ready")
st.divider()

# 1. JD BOX
st.subheader("1. Paste Job Description (JD)")
jd_text = st.text_area("JD", height=180, placeholder="e.g., Data Analyst with Python, SQL, Power BI, 2+ years experience...", label_visibility="collapsed")

st.write("")

# 2. UPLOAD - MAX 10
st.subheader("2. Upload Resumes (Max 10 PDFs)")
uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed", help="You can select up to 10 PDF files")

if uploaded_files:
    st.info(f"📁 {len(uploaded_files)} file(s) selected")

st.write("")
st.write("")

# 3. ENTER BUTTON - ALAG SE - MOBILE + LAPTOP DONO PE BADA
check_button = st.button("🔍 ENTER - CHECK RESUMES", type="primary", use_container_width=True)

if check_button:
    if not jd_text.strip():
        st.warning("⚠️ Pehle Job Description paste karo")
        st.stop()
    if not uploaded_files:
        st.warning("⚠️ Pehle kam se kam 1 resume upload karo")
        st.stop()
    if len(uploaded_files) > 10:
        st.error(f"❌ Max 10 files allowed. Tumne {len(uploaded_files)} upload kiye hai")
        st.stop()

    st.divider()
    st.subheader("3. Results")

    progress = st.progress(0)
    for i, file in enumerate(uploaded_files):
        resume_text = extract_text_from_pdf(file)
        if not resume_text.strip():
            st.error(f"**{file.name}** - ❌ Could not read PDF")
        else:
            score = get_match_score(resume_text, jd_text)
            if score == -1:
                st.error(f"**{file.name}** - ❌ Fake / Not a Resume")
            elif score < 35:
                st.error(f"**{file.name}** - ❌ Fake / Low Match - {score:.0f}%")
            else:
                st.success(f"**{file.name}** - ✅ Genuine - {score:.0f}% Match")
        progress.progress((i+1)/len(uploaded_files))