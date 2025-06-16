
import streamlit as st
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

    # charts
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
    if st.button("Generate Content"):
        lvl = db.get_user_topic_level(st.session_state.user_id, subj, topic)
        with st.spinner("Generating personalised lesson…"):
            content = ai_engine.generate_learning_content(subj, topic, lvl)
        st.markdown(content, unsafe_allow_html=True)
        if st.button("Take Quiz"):
            st.session_state.quiz_topic = {"subject": subj, "topic": topic}
            st.switch_page("🧩 Quiz")

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
