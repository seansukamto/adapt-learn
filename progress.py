
import streamlit as st
from utils.database import DatabaseManager
from utils.adaptive_logic import AdaptiveEngine
import random
from config.settings import APP_CONFIG

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

db = DatabaseManager()
adaptive_engine = AdaptiveEngine()

def show():
    st.header("📈 Detailed Progress Analytics")
    stats = db.get_user_stats(st.session_state.user_id)
    acc = stats['correct_answers']/max(stats['total_questions'],1)*100
    fig = go.Figure(go.Indicator(mode="gauge+number", value=acc,
                                 gauge={'axis':{'range':[0,100]}}))
    st.plotly_chart(fig, use_container_width=True)
