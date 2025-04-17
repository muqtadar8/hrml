import streamlit as st
import random
import sqlite3
from ui_components import display_metrics_dashboard
from utils import display_match_score, display_application_status
from database import get_applications_by_employer, get_applications_by_user

def dashboard_view():
    st.markdown("## Dashboard")
    
    # Different dashboard for employers vs job seekers
    if st.session_state.is_admin:
        employer_dashboard()
    else:
        candidate_dashboard()

def employer_dashboard():
    # Get employer metrics
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM jobs WHERE posted_by = ?", (st.session_state.user,))
    job_count = c.fetchone()[0]
    
    c.execute("""
        SELECT COUNT(*) FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE j.posted_by = ?
    """, (st.session_state.user,))
    application_count = c.fetchone()[0]
    
    c.execute("""
        SELECT AVG(match_score) FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE j.posted_by = ?
    """, (st.session_state.user,))
    avg_score = c.fetchone()[0] or 0
    
    # Most needed skill (simulated for demo)
    skills = ["Python", "Communication", "JavaScript", "Leadership"]
    top_skill = random.choice(skills)
    
    # Display metrics
    metrics = {
        "job_count": job_count,
        "application_count": application_count,
        "avg_score": avg_score,
        "top_skill": top_skill
    }
    display_metrics_dashboard(employer=True, metrics=metrics)
    
    # Recent applications
    st.markdown("### Recent Applications")
    
    applications = get_applications_by_employer(st.session_state.user)
    
    if applications:
        # Show most recent applications
        recent_apps = applications[:5]
        for app in recent_apps:
            with st.expander(f"{app[1]} - {app[2]} (Match: {app[6]:.1f}%)"):
                st.markdown(f"**Status:** {display_application_status(app[9])}", unsafe_allow_html=True)
                st.markdown(f"**Application Date:** {app[8].split()[0] if app[8] else 'N/A'}")
                st.markdown(f"**Match Score:** {display_match_score(app[6])}", unsafe_allow_html=True)
                
                # Create two columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Skills:**")
                    st.write(app[4])
                with col2:
                    st.markdown("**Experience:**")
                    st.write(app[5])
                    
                st.markdown("**Match Analysis:**")
                st.write(app[7])
    else:
        st.info("No applications yet. Your job listings will appear here once candidates apply.")
    
    # Job posting summary
    st.markdown("### Your Job Listings")
    c.execute("SELECT id, title, created_at FROM jobs WHERE posted_by = ? ORDER BY created_at DESC LIMIT 5", 
             (st.session_state.user,))
    jobs = c.fetchall()
    
    if jobs:
        for job in jobs:
            c.execute("SELECT COUNT(*) FROM applications WHERE job_id = ?", (job[0],))
            app_count = c.fetchone()[0]
            
            st.markdown(f"- **{job[1]}** - {app_count} applications - Posted: {job[2].split()[0] if job[2] else 'N/A'}")
    else:
        st.info("You haven't posted any jobs yet. Go to 'Post Job' to create your first listing.")

def candidate_dashboard():
    # Get candidate metrics
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    
    c.execute("""
        SELECT COUNT(*) FROM applications 
        WHERE username = ?
    """, (st.session_state.user,))
    application_count = c.fetchone()[0]
    
    c.execute("""
        SELECT COUNT(DISTINCT job_id) FROM applications 
        WHERE username = ?
    """, (st.session_state.user,))
    unique_jobs = c.fetchone()[0]
    
    c.execute("""
        SELECT AVG(match_score) FROM applications
        WHERE username = ?
    """, (st.session_state.user,))
    avg_score = c.fetchone()[0] or 0
    
    c.execute("""
        SELECT MAX(match_score) FROM applications
        WHERE username = ?
    """, (st.session_state.user,))
    max_score = c.fetchone()[0] or 0
    
    # Display metrics
    metrics = {
        "application_count": application_count,
        "unique_jobs": unique_jobs,
        "avg_score": avg_score,
        "max_score": max_score
    }
    display_metrics_dashboard(employer=False, metrics=metrics)
    
    # Show recent applications
    st.markdown("### Your Job Applications")
    
    applications = get_applications_by_user(st.session_state.user)
    
    if applications:
        # Create columns for the application cards
        col1, col2 = st.columns(2)
        
        # Split applications between columns
        for i, app in enumerate(applications[:6]):
            with (col1 if i % 2 == 0 else col2):
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(f"**{app[1]}**")
                    st.markdown(f"Employer: {app[2]}")
                    st.markdown(f"Status: {display_application_status(app[6])}", unsafe_allow_html=True)
                    st.markdown(f"Match Score: {display_match_score(app[3])}", unsafe_allow_html=True)
                    st.markdown(f"Applied: {app[5].split()[0] if app[5] else 'N/A'}")
                    
                    # View details button
                    if st.button("View Details", key=f"view_app_{app[0]}"):
                        st.session_state.view_application = app[0]
                        st.session_state.view_job_id = app[7]
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("You haven't applied to any jobs yet. Browse available jobs to start applying.")
    
    # Recommended jobs
    st.markdown("### Recommended Jobs")
    
    # In a real application, you'd use AI to recommend jobs based on past applications
    # For demo purposes, just showing some random jobs
    c.execute("SELECT id, title, description, posted_by, requirements, salary_range, location, job_type, created_at FROM jobs ORDER BY created_at DESC LIMIT 10")
    jobs = c.fetchall()
    
    if jobs:
        random_jobs = random.sample(jobs, min(3, len(jobs)))
        
        for job in random_jobs:
            with st.expander(f"{job[1]} - {job[6]}"):
                st.markdown(f"**Job Type:** {job[7]}")
                st.markdown(f"**Salary:** {job[5]}")
                st.markdown(f"**Description:** {job[2][:200]}..." if len(job[2]) > 200 else f"**Description:** {job[2]}")
                
                if st.button("View Full Job", key=f"view_job_{job[0]}"):
                    st.session_state.view_job = job[0]
                    st.rerun()
    else:
        st.info("No jobs available at the moment. Check back later for new opportunities.")