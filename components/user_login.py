import streamlit as st
from utils.database import DatabaseManager


db = DatabaseManager()

def show_user_login():
    # st.image("components/logo.png", width=100)

    # st.markdown("## 👋 Welcome to AdaptAdept!")
    # st.markdown("Please log in or create a new student account to begin.")
    col1, col2 = st.columns([1, 13])  # Adjust width ratio as needed

    with col1:
        st.image("components/logo.png", width=100)

    with col2:
        st.markdown("## 👋 Welcome to AdaptAdept!")
        st.markdown("Please log in or create a new student account to begin.")

    users = db.get_all_users()
    user_names = [u["name"] for u in users]

    option = st.radio("Choose option:", ["Select existing account", "Create new account"])

    if option == "Select existing account":
        if user_names:
            sel = st.selectbox("Select your name:", user_names, key="login_select")
            if st.button("Login"):
                user_id = next(u["id"] for u in users if u["name"] == sel)
                st.session_state.user_id = user_id
                st.rerun()
        else:
            st.info("No users found. Please create a new student.")
    
    elif option == "Create new account":
        # Phase 1: collect name and style
        if "new_user_created" not in st.session_state:
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
                    st.session_state.new_user_created = {
                        "name": new_name,
                        "style": inferred_style,
                        "user_id": uid
                    }
                    st.rerun()

        # Phase 2: confirmation screen
        elif st.session_state.get("new_user_created"):
            info = st.session_state.new_user_created
            st.success(f"🎉 Welcome, {info['name']}! Your inferred learning style is **{info['style']}**.")
            st.markdown("You can always change this later in **Settings**.")
            if st.button("Start Learning!"):
                st.session_state.user_id = info["user_id"]
                del st.session_state.new_user_created
                st.rerun()
