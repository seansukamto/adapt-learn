import streamlit as st
from utils.database import DatabaseManager

db = DatabaseManager()

def nav_menu():
    st.image("components/logo.png", use_container_width=True)

    user = db.get_user(st.session_state.user_id)
    st.write(f"👋 Welcome, **{user['name']}**")
    st.write(f"Learning Style: {user['learning_style']}")
    page = st.selectbox("Choose section:", ["📊 Dashboard", "📚 Learn", "🧩 Quiz", "📤 Upload", "📈 Progress", "⚙️ Settings"])
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    return page