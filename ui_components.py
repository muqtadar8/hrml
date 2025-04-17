import streamlit as st
from utils import display_match_score, display_application_status

def display_job_card(job, show_apply_button=True):
    """Display a job listing card"""
    with st.expander(f"💼 {job[1]}", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {job[1]}")
            st.markdown(f"**Posted by:** {job[3]}")
            
            if job[5]:  # Salary range
                st.markdown(f"**Salary:** {job[5]}")
            
            if job[6]:  # Location
                st.markdown(f"**Location:** {job[6]}")
                
            if job[7]:  # Job type
                st.markdown(f"**Type:** {job[7]}")
            
            st.markdown("### Job Description")
            st.write(job[2])
            
            if job[4]:  # Requirements
                st.markdown("### Requirements")
                st.write(job[4])
        
        with col2:
            # Format date
            date_str = job[8].split()[0] if job[8] else "N/A"
            st.markdown(f"**Posted:** {date_str}")
            
            if show_apply_button and not st.session_state.is_admin:
                if st.button(f"Apply Now", key=f"apply_{job[0]}"):
                    st.session_state.selected_job = job[0]
                    st.rerun()

def display_metrics_dashboard(employer=True, metrics=None):
    """Display metrics dashboard for employers or candidates"""
    st.markdown("### Dashboard")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if employer:
        # Check if metrics data was passed
        if metrics:
            job_count = metrics.get("job_count", 0)
            application_count = metrics.get("application_count", 0)
            avg_score = metrics.get("avg_score", 0)
            top_skill = metrics.get("top_skill", "N/A")
        else:
            job_count = 0
            application_count = 0
            avg_score = 0
            top_skill = "N/A"
        
        # Display employer metrics
        with col1:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{job_count}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Active Jobs</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{application_count}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Applications</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{avg_score:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Average Match Score</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{top_skill}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Most Sought Skill</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Check if metrics data was passed
        if metrics:
            application_count = metrics.get("application_count", 0)
            unique_jobs = metrics.get("unique_jobs", 0)
            avg_score = metrics.get("avg_score", 0)
            max_score = metrics.get("max_score", 0)
        else:
            application_count = 0
            unique_jobs = 0
            avg_score = 0
            max_score = 0
        
        # Display candidate metrics
        with col1:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{application_count}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Applications</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{unique_jobs}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Jobs Applied</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{avg_score:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Average Match</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{max_score:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Highest Match</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)