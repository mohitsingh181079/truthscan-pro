import streamlit as st
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIG ---
st.set_page_config(page_title="TruthScan Pro", page_icon="✅", layout="wide")

# Secrets - Make sure you have this in Streamlit Secrets
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "Mmoo@2026#Secure")
LICENSE_KEY = st.secrets.get("LICENSE_KEY", "Mmoo@2026#Secure")

# --- FUNCTIONS ---

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
    # FIX for "King" bug
    if len(jd_text.strip()) < 10:
        return 0.0

    # Check if file is actually a resume
    resume_keywords = ["experience", "education", "skills", "project", "resume", "objective"]
    if not any(word in resume_text.lower() for word in resume_keywords):
        return -1 # -1 means Not a Resume / Question Paper

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text.lower(), jd_text.lower()])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return score * 100
    except:
        return 0.0

# --- UI ---

st.title("✅ TruthScan Pro - Resume Truth Scanner")

# Sidebar - License
with st.sidebar:
    st.header("🔑 Pro License")
    user_license = st.text_input("Enter License Key", type="password")
    jd_text = st.text_area("Paste Job Description (JD)", height=200, placeholder="e.g., Data Analyst with Python, SQL, Power BI...")

    if not user_license:
        st.warning("Please enter License Key to start")
        st.stop()

    if user_license!= LICENSE_KEY and user_license!= ADMIN_PASSWORD:
        st.error("❌ Invalid License Key")
        st.stop()

    st.success("✅ Pro License Activated")

# Main - Upload
uploaded_files = st.file_uploader("Upload Resumes (Max 3)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    if len(uploaded_files) > 3:
        st.error("❌ Free Limit Reached! Max 3 files allowed at once.")
        st.stop()

    if not jd_text:
        st.warning("⚠️ Please paste Job Description in sidebar first")
        st.stop()

    st.divider()
    st.subheader("Results")

    for file in uploaded_files:
        resume_text = extract_text_from_pdf(file)

        if not resume_text:
            st.error(f"**{file.name}** - ❌ Could not read PDF")
            continue

        score = get_match_score(resume_text, jd_text)

        if score == -1:
            st.error(f"**{file.name}** - ❌ Fake / Irrelevant (Not a Resume - looks like Question Paper/Notes)")
        elif score < 25:
            st.error(f"**{file.name}** - ❌ Fake / Irrelevant - Only {score:.0f}% match with JD '{jd_text}'")
        else:
            st.success(f"**{file.name}** - ✅ Genuine Resume - {score:.0f}% Match")