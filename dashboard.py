
import streamlit as st
from utils.database import DatabaseManager
from utils.adaptive_logic import AdaptiveEngine
import random
from config.settings import APP_CONFIG


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

db = DatabaseManager()
adaptive_engine = AdaptiveEngine()

def show():
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
        if streak_count == 1:
          st.success(f"🎉 Daily Streak: {streak_count} day")
        else:
          st.success(f"🎉 Daily Streak: {streak_count} days")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Progress Over Time")
        data = db.get_user_progress_data(st.session_state.user_id)
        if data:
            # df = pd.DataFrame(data)
            # fig = px.line(df, x="date", y="accuracy", title="Accuracy by Day")
            # st.plotly_chart(fig, use_container_width=True)
            df = pd.DataFrame(data)

            # Clean and trim data
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df = df.sort_values("date").tail(3)

            # Ensure percentage scale
            if df["accuracy"].max() <= 1:
                df["accuracy"] = df["accuracy"] * 100

            # Plot line chart
            fig = px.line(df, x="date", y="accuracy", title="Accuracy by Day")

            # Lock view: remove zoom, pan, autoscale, and fix Y-axis to 0–100
            fig.update_layout(
                yaxis_title="Accuracy (%)",
                yaxis=dict(range=[0, 100]),
                xaxis=dict(
                    tickformat="%b %d",  # e.g., Jun 16
                    tickvals=df["date"],
                    tickmode="array"
                ),
                margin=dict(r=10, l=40, t=60, b=40),
                dragmode=False,
                showlegend=False
            )

            # Disable modebar tools
            fig.update_layout(modebar=dict(remove=["zoom", "pan", "select", "lasso2d", "autoScale", "resetScale"]))

            # Hide the modebar entirely (optional)
            # fig.showlegend = False
            # fig.update_layout(showlegend=False, modebar_remove=["zoom", "pan", "select", "lasso2d"])

            # Render
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        else:
            st.info("No data yet – take some quizzes!")


    with c2:
        st.subheader("Subject Performance")
        sub = db.get_subject_stats(st.session_state.user_id)
        if sub:
            df = pd.DataFrame(sub)

            # Ensure accuracy is in percentage scale
            if df["accuracy"].max() <= 1:
                df["accuracy"] = df["accuracy"] * 100

            # Plot bar chart
            fig = px.bar(df, x="subject", y="accuracy", title="Accuracy by Subject")

            # Lock Y-axis and remove interactions
            fig.update_layout(
                yaxis_title="Accuracy (%)",
                yaxis=dict(range=[0, 100]),
                dragmode=False,
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No quizzes taken yet.")
    