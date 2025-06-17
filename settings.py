
import streamlit as st
from utils.database import DatabaseManager
from utils.adaptive_logic import AdaptiveEngine
import random
from config.settings import APP_CONFIG

db = DatabaseManager()
adaptive_engine = AdaptiveEngine()

def show():
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