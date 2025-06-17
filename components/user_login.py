# import streamlit as st
# from utils.database import DatabaseManager

# db = DatabaseManager()

# def show_user_login():
#     st.subheader("👤 Student Login")
#     users = db.get_all_users()
#     user_names = [u["name"] for u in users]
#     option = st.radio("Choose option:", ["Select existing student", "Create new student"])
#     if option == "Select existing student" and user_names:
#         sel = st.selectbox("Select your name:", user_names, key="login_select")
#         if st.button("Login"):
#             user_id = next(u["id"] for u in users if u["name"] == sel)
#             st.session_state.user_id = user_id
#             st.rerun()
#     elif option == "Create new student":
#         new_name = st.text_input("Enter your name:")
#         style = st.selectbox("Preferred learning style:",
#                              ["Visual", "Auditory", "Kinesthetic", "Mixed"])
#         if st.button("Create Account") and new_name:
#             uid = db.create_user(new_name, style)
#             st.session_state.user_id = uid
#             st.success(f"Welcome, {new_name}!")
#             st.rerun()
        
import streamlit as st
from utils.database import DatabaseManager

db = DatabaseManager()

def show_user_login():
    st.markdown("## 👋 Welcome to AdaptLearn")
    st.markdown("Please log in or create a new student account to begin.")

    users = db.get_all_users()
    user_names = [u["name"] for u in users]

    option = st.radio("Choose option:", ["Select existing student", "Create new student"])

    if option == "Select existing student":
        if user_names:
            sel = st.selectbox("Select your name:", user_names, key="login_select")
            if st.button("Login"):
                user_id = next(u["id"] for u in users if u["name"] == sel)
                st.session_state.user_id = user_id
                st.rerun()
        else:
            st.info("No users found. Please create a new student.")
    else:
        new_name = st.text_input("Enter your name:")

        if new_name:
            st.markdown("#### Help us determine your preferred learning style:")

            q1 = st.radio("When trying to remember something, what helps you most?", 
                        ["Seeing diagrams, charts, or colors", 
                        "Listening to explanations or discussing it", 
                        "Doing hands-on activities or writing it out", 
                        "A mix of the above"], key="q1")

            q2 = st.radio("In a classroom, you prefer the teacher to:",
                        ["Draw or show slides while explaining", 
                        "Talk it through and tell stories", 
                        "Let you try it yourself with examples", 
                        "Combine visuals, speech, and practice"], key="q2")

            q3 = st.radio("How do you study for a test?", 
                        ["Rewriting notes and highlighting them", 
                        "Listening to recordings or reading out loud", 
                        "Using flashcards or physically acting it out", 
                        "Using different methods depending on the topic"], key="q3")

            q4 = st.radio("What’s your go-to when you're confused about a new concept?",
                        ["Look for videos, infographics, or visual summaries", 
                        "Ask someone to explain it to you", 
                        "Try to solve a related problem or experiment with it", 
                        "Depends on how it's presented"], key="q4")

            if st.button("Create Account"):
                # Infer learning style
                answers = [q1, q2, q3, q4]
                counts = {"Visual": 0, "Auditory": 0, "Kinesthetic": 0, "Mixed": 0}
                for ans in answers:
                    if "diagram" in ans or "Draw" in ans or "video" in ans or "highlighting" in ans:
                        counts["Visual"] += 1
                    elif "Listen" in ans or "Talk" in ans or "recordings" in ans or "explain" in ans:
                        counts["Auditory"] += 1
                    elif "hands-on" in ans or "try it" in ans or "acting" in ans or "solve" in ans:
                        counts["Kinesthetic"] += 1
                    else:
                        counts["Mixed"] += 1
                
                inferred_style = max(counts, key=counts.get)
                uid = db.create_user(new_name, inferred_style)
                st.session_state.user_id = uid
                st.success(f"Welcome, {new_name}! Your learning style is likely: **{inferred_style}**")
                st.rerun()
