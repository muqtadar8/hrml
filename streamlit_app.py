import streamlit as st


# Page configuration
st.set_page_config(
    page_title="HR Match Portal • AI-Powered Recruitment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
from views import auth, dashboard, employer, applicant, detail_views

from database import init_db
from styles import load_css
import os
# Apply custom CSS
load_css()

# Initialize database connection
conn = init_db()

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.selected_job = None

# Display header
def display_header():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<div class="main-header">🧠 HR Match Portal</div>', unsafe_allow_html=True)
        st.markdown('<div>AI-Powered Recruitment & Talent Matching</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.user:
            st.markdown(f"**{st.session_state.user}**")
            if st.session_state.is_admin:
                st.markdown("*Employer Account*")
            else:
                st.markdown("*Candidate Account*")

display_header()

# Sidebar navigation
if st.session_state.user:
    if st.session_state.is_admin:
        menu = ["Dashboard", "Post Job", "My Job Listings", "Applications", "Bulk Resume Analysis"]
    else:
        menu = ["Dashboard", "Browse Jobs", "My Applications"]
    
    choice = st.sidebar.selectbox("Navigation", menu)
    
    # Sidebar user info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Account**: {st.session_state.user}")
    st.sidebar.markdown(f"**Type**: {'Employer' if st.session_state.is_admin else 'Job Seeker'}")
    
    if st.sidebar.button("📤 Logout", type="primary"):
        st.session_state.user = None
        st.session_state.is_admin = False
        st.session_state.selected_job = None
        st.rerun()
else:
    st.sidebar.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
    st.sidebar.markdown("## HR Match Portal")
    st.sidebar.markdown("AI-powered recruitment solution")
    choice = st.sidebar.radio("", ["Login", "Register"])

# Route to the appropriate view based on user selection
if choice == "Login":
    auth.login_view()
elif choice == "Register":
    auth.register_view()
elif choice == "Dashboard":
    dashboard.dashboard_view()
elif choice == "Post Job" and st.session_state.is_admin:
    employer.post_job_view()
elif choice == "My Job Listings" and st.session_state.is_admin:
    employer.job_listings_view()
elif choice == "Applications" and st.session_state.is_admin:
    employer.applications_view()
elif choice == "Bulk Resume Analysis" and st.session_state.is_admin:
    employer.bulk_analysis_view()
elif choice == "Browse Jobs" and not st.session_state.is_admin:
    applicant.browse_jobs_view()
elif choice == "My Applications" and not st.session_state.is_admin:
    applicant.my_applications_view()

# Handle detail views
if hasattr(st.session_state, 'view_job'):
    detail_views.job_detail_view()

if hasattr(st.session_state, 'view_job_applications'):
    detail_views.job_applications_view()

if st.session_state.user and not st.session_state.is_admin and st.session_state.selected_job is not None:
    detail_views.application_form_view()

# Footer
st.markdown("""
<div class="footer">
    <p>HR Match Portal | Final Project by [Your Name] | Using Teapot AI Engine</p>
    <p>© 2025 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
