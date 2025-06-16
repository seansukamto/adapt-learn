
import streamlit as st
import streamlit.components.v1 as components

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

from utils.database import DatabaseManager
from utils.ai_engine import AIEngine
from utils.adaptive_logic import AdaptiveEngine
from config.settings import APP_CONFIG

st.set_page_config(
    page_title="AdaptLearn - AI-Powered Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None
if 'quiz_state' not in st.session_state:
    st.session_state.quiz_state = {}

@st.cache_resource
def initialize_components():
    db = DatabaseManager()
    ai_engine = AIEngine()
    adaptive_engine = AdaptiveEngine()
    return db, ai_engine, adaptive_engine

db, ai_engine, adaptive_engine = initialize_components()

# ---- UI helpers ----------------------------------------------------------

def show_user_login():
    st.subheader("👤 Student Login")
    users = db.get_all_users()
    user_names = [u["name"] for u in users]
    option = st.radio("Choose option:", ["Select existing student", "Create new student"])
    if option == "Select existing student" and user_names:
        sel = st.selectbox("Select your name:", user_names, key="login_select")
        if st.button("Login"):
            user_id = next(u["id"] for u in users if u["name"] == sel)
            st.session_state.user_id = user_id
            st.rerun()
    elif option == "Create new student":
        new_name = st.text_input("Enter your name:")
        style = st.selectbox("Preferred learning style:",
                             ["Visual", "Auditory", "Kinesthetic", "Mixed"])
        if st.button("Create Account") and new_name:
            uid = db.create_user(new_name, style)
            st.session_state.user_id = uid
            st.success(f"Welcome, {new_name}!")
            st.rerun()

def nav_menu():
    user = db.get_user(st.session_state.user_id)
    st.write(f"👋 Welcome, **{user['name']}**")
    st.write(f"Learning Style: {user['learning_style']}")
    page = st.selectbox("Choose section:",
                        ["📊 Dashboard", "📚 Learn", "🧩 Quiz", "📈 Progress", "⚙️ Settings"])
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    return page

# ---- Pages ---------------------------------------------------------------

def page_welcome():
    c1, c2 = st.columns([2, 1])
    with c1:
        st.header("Welcome to AdaptLearn!")
        st.markdown("""
        ### 🚀 Features
        - **Adaptive Difficulty** – questions scale with your mastery  
        - **Personalised Content** – matches your learning style  
        - **Analytics Dashboard** – visualise your progress  
        - **AI‑Generated** – dynamic explanations & quizzes  
        """)
        st.info("👈 Log in via the sidebar to begin")
    with c2:
        st.image("https://via.placeholder.com/300x200/4CAF50/FFFFFF?text=AI+Learning")

def page_dashboard():
    st.header("📊 Your Learning Dashboard")
    stats = db.get_user_stats(st.session_state.user_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Questions", stats["total_questions"])
    c2.metric("Correct", stats["correct_answers"])
    c3.metric("Accuracy", f"{stats['correct_answers']/max(stats['total_questions'],1)*100:.1f}%")
    c4.metric("Current Level", stats["current_level"])

    # Daily streak counter
    streak_data = db.get_user_streak_data(st.session_state.user_id)
    streak_count = streak_data["streak_count"]
    last_login_date = streak_data["last_login_date"]
    today = datetime.now().date()

    if last_login_date != today:
        st.warning("You haven't logged in today! Make sure to log in daily to maintain your streak.")
    else:
        st.success(f"🎉 Daily Streak: {streak_count} days")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Progress Over Time")
        data = db.get_user_progress_data(st.session_state.user_id)
        if data:
            df = pd.DataFrame(data)
            fig = px.line(df, x="date", y="accuracy", title="Accuracy by Day")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet – take some quizzes!")

    with c2:
        st.subheader("Subject Performance")
        sub = db.get_subject_stats(st.session_state.user_id)
        if sub:
            df = pd.DataFrame(sub)
            fig = px.bar(df, x="subject", y="accuracy", title="Accuracy by Subject")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No quizzes taken yet.")

def page_learn():
    st.header("📚 Learning Hub")

    subjects = APP_CONFIG["subjects"]
    subj = st.selectbox("Subject", list(subjects.keys()))
    topic = st.selectbox("Topic", subjects[subj])

    # --- Webcam drag-and-drop interaction ---
    st.subheader("🖐️ Drag the Boxes with Your Hand (via Webcam)")

    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        video, canvas {
          position: absolute;
          top: 0;
          left: 0;
        }
        #wrapper {
          position: relative;
          width: 640px;
          height: 480px;
        }
      </style>
    </head>
    <body>
    <div id="wrapper">
      <video id="video" width="640" height="480" autoplay playsinline muted></video>
      <canvas id="canvas" width="640" height="480"></canvas>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>

    <script>
      const video = document.getElementById("video");
      const canvas = document.getElementById("canvas");
      const ctx = canvas.getContext("2d");

      let draggingBox = null;
      let merged = false;

      let boxes = [
        { id: 1, x: 100, y: 200, size: 80, color: 'blue' },
        { id: 2, x: 400, y: 200, size: 80, color: 'yellow' }
      ];

      function drawScene(landmarks) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        for (const box of boxes) {
          ctx.fillStyle = box.color;
          ctx.fillRect(box.x, box.y, box.size, box.size);
        }

        if (landmarks) {
          for (const point of landmarks) {
            ctx.beginPath();
            ctx.arc(point.x * canvas.width, point.y * canvas.height, 5, 0, 2 * Math.PI);
            ctx.fillStyle = "red";
            ctx.fill();
          }
        }
      }

      function isPinching(landmarks) {
        const dx = landmarks[4].x - landmarks[8].x;
        const dy = landmarks[4].y - landmarks[8].y;
        return Math.sqrt(dx * dx + dy * dy) < 0.05;
      }

      function checkCollision(boxA, boxB) {
        return (
          boxA.x < boxB.x + boxB.size &&
          boxA.x + boxA.size > boxB.x &&
          boxA.y < boxB.y + boxB.size &&
          boxA.y + boxA.size > boxB.y
        );
      }

      function mergeBoxes() {
        const b1 = boxes[0], b2 = boxes[1];
        const minX = Math.min(b1.x, b2.x);
        const minY = Math.min(b1.y, b2.y);
        const maxX = Math.max(b1.x + b1.size, b2.x + b2.size);
        const maxY = Math.max(b1.y + b1.size, b2.y + b2.size);

        boxes = [{
          id: "merged",
          x: minX,
          y: minY,
          size: Math.max(maxX - minX, maxY - minY),
          color: "green"
        }];
        merged = true;
      }

      function updateDragging(landmarks) {
        const x = landmarks[8].x * canvas.width;
        const y = landmarks[8].y * canvas.height;

        if (draggingBox && isPinching(landmarks)) {
          draggingBox.x = x - draggingBox.size / 2;
          draggingBox.y = y - draggingBox.size / 2;
        } else {
          draggingBox = null;
          if (!merged && isPinching(landmarks)) {
            for (let box of boxes) {
              if (
                x >= box.x && x <= box.x + box.size &&
                y >= box.y && y <= box.y + box.size
              ) {
                draggingBox = box;
                break;
              }
            }
          }
        }

        if (!merged && boxes.length === 2 && checkCollision(boxes[0], boxes[1])) {
          mergeBoxes();
        }
      }

      const hands = new Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });

      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5,
      });

      hands.onResults((results) => {
        if (results.multiHandLandmarks.length > 0) {
          const landmarks = results.multiHandLandmarks[0];
          updateDragging(landmarks);
          drawScene(landmarks);
        } else {
          drawScene(null);
          draggingBox = null;
        }
      });

      const camera = new Camera(video, {
        onFrame: async () => await hands.send({ image: video }),
        width: 640,
        height: 480,
      });
      camera.start();
    </script>
    </body>
    </html>
    """, height=500)

    # --- Content generation from subject/topic ---
    st.subheader("🎯 Personalised Learning Content")
    if st.button("Generate Content"):
        lvl = db.get_user_topic_level(st.session_state.user_id, subj, topic)
        with st.spinner("Generating personalised lesson…"):
            content = ai_engine.generate_learning_content(subj, topic, lvl)
        st.markdown(content, unsafe_allow_html=True)
        if st.button("Take Quiz"):
            st.session_state.quiz_topic = {"subject": subj, "topic": topic}
            st.switch_page("🧩 Quiz")

    # --- File Upload & Quiz Generation ---
    st.subheader("📄 Upload Content for Quiz Generation")
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
        st.success("File uploaded successfully!")

        if st.button("Generate Quiz"):
            quiz_questions = ai_engine.generate_quiz_questions(content)
            st.session_state.quiz_questions = quiz_questions
            st.session_state.quiz_attempts = []
            st.success("Quiz generated! Navigate to the Quiz page to start.")

    # --- Retest Functionality ---
    if st.session_state.get("quiz_attempts"):
        st.subheader("🔁 Retest on Incorrect Questions")
        if st.button("Retest"):
            incorrect_questions = [
                attempt["question"] for attempt in st.session_state.quiz_attempts if not attempt["is_correct"]
            ]
            if incorrect_questions:
                retest_questions = ai_engine.generate_similar_questions(incorrect_questions)
                st.session_state.quiz_questions = retest_questions
                st.success("Retest questions generated! Navigate to the Quiz page to start.")
            else:
                st.info("No incorrect questions to retest.")



def page_quiz():
    st.header("🧩 Adaptive Quiz")
    if "quiz_topic" not in st.session_state:
        st.info("Select a topic in Learn first.")
        return
    info = st.session_state.quiz_topic
    st.subheader(f"{info['subject']} – {info['topic']}")
    level = db.get_user_topic_level(st.session_state.user_id, info["subject"], info["topic"])
    qs = st.session_state.quiz_state

    # init state
    if not qs:
        st.session_state.quiz_state = {"n": 0, "correct": 0, "level": level, "q": None}
        qs = st.session_state.quiz_state

    if qs["q"] is None:
        qs["q"] = ai_engine.generate_question(info["subject"], info["topic"], qs["level"])

    q = qs["q"]
    st.write(f"**Q{qs['n']+1}:** {q['question']}")
    ans = st.radio("Answer:", q["options"])
    if st.button("Submit"):
        correct = (ans == q["correct_answer"])
        qs["n"] += 1
        if correct:
            qs["correct"] += 1
            st.success("Correct!")
        else:
            st.error(f"Wrong. Correct: {q['correct_answer']}")
            st.info(q.get("explanation",""))
        # record
        db.record_quiz_answer(st.session_state.user_id, info["subject"], info["topic"],
                              q["question"], ans, q["correct_answer"], correct, qs["level"])
        qs["level"] = adaptive_engine.adjust_difficulty(qs["level"], correct, qs["n"], qs["correct"])
        qs["q"] = None
        st.rerun()

    if qs["n"] >= 10 and st.button("Finish"):
        acc = qs["correct"]/qs["n"]*100
        st.write(f"Finished {qs['n']} questions with {acc:.1f}% accuracy.")
        st.session_state.quiz_state = {}

def page_progress():
    st.header("📈 Detailed Progress Analytics")
    stats = db.get_user_stats(st.session_state.user_id)
    acc = stats['correct_answers']/max(stats['total_questions'],1)*100
    fig = go.Figure(go.Indicator(mode="gauge+number", value=acc,
                                 gauge={'axis':{'range':[0,100]}}))
    st.plotly_chart(fig, use_container_width=True)

def page_settings():
    st.header("⚙️ Settings")
    user = db.get_user(st.session_state.user_id)
    with st.form("settings"):
        name = st.text_input("Name", user["name"])
        style = st.selectbox("Learning Style", APP_CONFIG["learning_styles"],
                             index=APP_CONFIG["learning_styles"].index(user["learning_style"]))
        if st.form_submit_button("Save"):
            db.update_user_settings(st.session_state.user_id, {"name": name, "learning_style": style})
            st.success("Saved!")
            st.rerun()

def extract_file_content(uploaded_file) -> str:
    """
    Extracts text content from the uploaded file.
    Supports .txt, .pdf, and .docx formats.
    """
    try:
        if uploaded_file.name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".pdf"):
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            return "".join(page.extract_text() for page in reader.pages)
        elif uploaded_file.name.endswith(".docx"):
            import docx
            doc = docx.Document(uploaded_file)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        else:
            raise ValueError("Unsupported file format.")
    except Exception as e:
        raise ValueError(f"Error processing file: {e}")
    
# ---- Main ---------------------------------------------------------------

def main():
    with st.sidebar:
        if st.session_state.user_id is None:
            show_user_login()
        else:
            page = nav_menu()

    if st.session_state.user_id is None:
        page_welcome()
    else:
        if page == "📊 Dashboard":
            page_dashboard()
        elif page == "📚 Learn":
            page_learn()
        elif page == "🧩 Quiz":
            page_quiz()
        elif page == "📈 Progress":
            page_progress()
        elif page == "⚙️ Settings":
            page_settings()

if __name__ == "__main__":
    main()
