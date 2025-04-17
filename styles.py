import streamlit as st

def load_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            font-weight: 700;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #424242;
            font-weight: 600;
        }
        .card {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .metric-container {
            background-color: #f7f7f7;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1E88E5;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #757575;
        }
        .match-high {
            color: #4CAF50;
            font-weight: 700;
        }
        .match-medium {
            color: #FF9800;
            font-weight: 700;
        }
        .match-low {
            color: #F44336;
            font-weight: 700;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #757575;
            font-size: 0.8rem;
        }
        .progress-container {
            width: 100%;
            margin-bottom: 20px;
        }
        .help-text {
            font-size: 0.85rem;
            color: #757575;
            font-style: italic;
        }
    </style>
    """, unsafe_allow_html=True)