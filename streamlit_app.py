
import streamlit as st
import dashboard, learn, quiz, upload, progress, settings
from components.user_login import show_user_login
from components.navbar import nav_menu

def main():
    st.set_page_config(page_title="AdaptAdept", page_icon="🎓", layout="wide")

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    page = None 

    if st.session_state.user_id is None:
        show_user_login()
        return

    with st.sidebar:
        page = nav_menu()

    if st.session_state.user_id is None:
        # page_welcome()
        st.markdown("## 👋 Welcome to AdaptLearn! Please log in to get started.")
    else:
        if page == "📊 Dashboard":
            # page_dashboard()
            dashboard.show()
        elif page == "📚 Learn":
            # page_learn()
            learn.show()
        elif page == "🧩 Quiz":
            # page_quiz()
            quiz.show()
        elif page == "📤 Upload":
            upload.show()
        elif page == "📈 Progress":
            # page_progress()
            progress.show()
        elif page == "⚙️ Settings":
            # page_settings()
            settings.show()

if __name__ == "__main__":
    main()
