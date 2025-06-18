import streamlit as st
from utils.database import DatabaseManager
from utils.adaptive_logic import AdaptiveEngine

db = DatabaseManager()
adaptive_engine = AdaptiveEngine()

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
            st.session_state.quiz_submitted = False

        if "quiz_questions" in st.session_state and st.session_state.quiz_questions:
            st.header("🧪 Quiz")
            user_answers = []
            correct_count = 0

            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}:** {q['question']}")
                selected = st.radio("Choose an answer:", q["options"], key=f"q_{i}")
                user_answers.append((selected, q))
                st.markdown("---")

            if st.button("Submit Answers") and not st.session_state.get("quiz_submitted", False):
                st.session_state.quiz_submitted = True
                st.session_state.quiz_answers = user_answers  # Save for result display

        if st.session_state.get("quiz_submitted", False):
            st.subheader("📊 Results")
            correct_count = 0
            for i, (user_ans, q) in enumerate(st.session_state.quiz_answers):
                st.markdown(f"**Q{i+1}:** {q['question']}")
                if user_ans == q["correct_answer"]:
                    st.success(f"✅ Correct! ({user_ans})")
                    correct_count += 1
                else:
                    st.error(f"❌ Incorrect. You chose {user_ans}. Correct: {q['correct_answer']}")
                    st.info(f"💡 {q['explanation']}")
            st.markdown(f"### 🧠 Your Score: **{correct_count}/{len(st.session_state.quiz_questions)}** ({(correct_count/len(st.session_state.quiz_questions))*100:.1f}%)")
