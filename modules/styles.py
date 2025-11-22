import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        .stApp {
            background-color: #0e1117;
            color: #e0e0e0;
        }
        .metric-card {
            background-color: #1e2127;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .news-card {
            background-color: #1e2127;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        h1, h2, h3 {
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
