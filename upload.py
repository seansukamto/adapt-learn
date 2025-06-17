import streamlit as st
from utils.database import DatabaseManager
from utils.adaptive_logic import AdaptiveEngine

db = DatabaseManager()
adaptive_engine = AdaptiveEngine()

# ✅ Only try to access secrets; do not use os or env
try:
    key = st.secrets["OPENAI_API_KEY"]
except Exception:
    key = None

if key:
    from utils.ai_engine import AIEngine
    ai_engine = AIEngine()
else:
    ai_engine = None

def show():
    st.subheader("📄 Upload Content for Quiz Generation")

    if not ai_engine:
        st.warning("⚠️ Quiz generation requires an OpenAI API key.")
        st.info("Please add it in `.streamlit/secrets.toml` as `OPENAI_API_KEY = \"your-key\"`.")
        return

    uploaded_file = st.file_uploader("Upload a text file or document", type=["txt", "pdf", "docx"])

    if uploaded_file:
        def extract_file_content(file):
            if file.name.endswith(".txt"):
                return file.read().decode("utf-8")
            elif file.name.endswith(".pdf"):
                import PyPDF2
                reader = PyPDF2.PdfReader(file)
                return "".join(page.extract_text() for page in reader.pages)
            elif file.name.endswith(".docx"):
                import docx
                doc = docx.Document(file)
                return "\n".join(paragraph.text for paragraph in doc.paragraphs)
            else:
                raise ValueError("Unsupported file format.")

        with st.spinner("Processing file..."):
            content = extract_file_content(uploaded_file)
        st.success("✅ File uploaded successfully!")

        if st.button("Generate Quiz"):
            quiz_questions = ai_engine.generate_quiz_questions(content)
            st.session_state.quiz_questions = quiz_questions
            st.session_state.quiz_attempts = []
            st.success("🎯 Quiz generated! Head over to the Quiz page to begin.")
        