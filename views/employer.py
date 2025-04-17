import streamlit as st
import pandas as pd
import altair as alt
import time
from database import post_job, get_job_by_id, update_job_status, get_applications_by_job
from ai_engine import process_bulk_resumes
from utils import display_match_score, display_application_status

def post_job_view():
    st.markdown("## Post a New Job")
    
    with st.form("job_form"):
        job_title = st.text_input("Job Title")
        
        col1, col2 = st.columns(2)
        with col1:
            job_location = st.text_input("Location")
            job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Remote", "Internship"])
        with col2:
            job_salary = st.text_input("Salary Range (e.g., $60K-80K)")
        
        st.markdown("### Job Description")
        st.markdown('<div class="help-text">Provide a detailed description of the role, responsibilities, and company information.</div>', unsafe_allow_html=True)
        job_desc = st.text_area("", height=150,key="jd")
        
        st.markdown("### Job Requirements")
        st.markdown('<div class="help-text">List required skills, experience, education, and qualifications. These will be used by our AI to match candidates.</div>', unsafe_allow_html=True)
        job_requirements = st.text_area("", height=150,key="jr")
        
        submit_button = st.form_submit_button("Post Job", type="primary")
    
    if submit_button:
        if job_title and job_desc and job_requirements:
            job_id = post_job(
                job_title, 
                job_desc, 
                st.session_state.user, 
                job_requirements, 
                job_salary, 
                job_location, 
                job_type
            )
            st.success(f"✅ Job posted successfully! Job ID: {job_id}")
        else:
            st.error("⚠️ Job title, description and requirements are required fields.")

def job_listings_view():
    st.markdown("## My Job Listings")
    
    # Get jobs posted by this employer
    import sqlite3
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""SELECT id, title, description, posted_by, requirements, 
                salary_range, location, job_type, created_at FROM jobs 
                WHERE posted_by=? ORDER BY created_at DESC""", 
              (st.session_state.user,))
    employer_jobs = c.fetchall()
    
    if not employer_jobs:
        st.info("You haven't posted any jobs yet. Go to 'Post Job' to create your first listing.")
    else:
        # Create tabs for each job
        job_titles = [job[1] for job in employer_jobs]
        tabs = st.tabs(job_titles)
        
        for i, tab in enumerate(tabs):
            with tab:
                job = employer_jobs[i]
                
                # Job details
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {job[1]}")
                    st.markdown(f"**Location:** {job[6] or 'Not specified'}")
                    st.markdown(f"**Type:** {job[7] or 'Not specified'}")
                    st.markdown(f"**Salary:** {job[5] or 'Not specified'}")
                    st.markdown(f"**Posted:** {job[8].split()[0] if job[8] else 'N/A'}")
                    
                    st.markdown("### Description")
                    st.write(job[2])
                    
                    st.markdown("### Requirements")
                    st.write(job[4])
                
                with col2:
                    # Application statistics
                    c.execute("SELECT COUNT(*) FROM applications WHERE job_id = ?", (job[0],))
                    app_count = c.fetchone()[0]
                    
                    c.execute("SELECT AVG(match_score) FROM applications WHERE job_id = ?", (job[0],))
                    avg_score = c.fetchone()[0] or 0
                    
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{app_count}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Applications</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{avg_score:.1f}%</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Avg Match Score</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # View applications button
                if st.button("View All Applications", key=f"view_apps_{job[0]}"):
                    st.session_state.view_job_applications = job[0]
                    st.rerun()

def applications_view():
    st.markdown("## Applications")
    
    # Get jobs posted by this employer
    import sqlite3
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, title FROM jobs WHERE posted_by=?", (st.session_state.user,))
    employer_jobs = c.fetchall()
    
    if not employer_jobs:
        st.info("You haven't posted any jobs yet. Go to 'Post Job' to create your first listing.")
    else:
        # Job selection filter
        job_filter = st.selectbox(
            "Filter by job", 
            ["All Jobs"] + [f"{job[0]} - {job[1]}" for job in employer_jobs]
        )
        
        # Status filter
        status_filter = st.selectbox(
            "Filter by status",
            ["All Statuses", "Pending", "Interview", "Accepted", "Rejected"]
        )
        
        # Get applications based on filters
        if job_filter == "All Jobs":
            if status_filter == "All Statuses":
                c.execute("""
                    SELECT a.id, a.username, j.title, j.id, a.extracted_skills, a.extracted_exp, a.match_score, 
                           a.match_feedback, a.application_date, a.status
                    FROM applications a
                    JOIN jobs j ON a.job_id = j.id
                    WHERE j.posted_by = ?
                    ORDER BY a.match_score DESC
                """, (st.session_state.user,))
            else:
                c.execute("""
                    SELECT a.id, a.username, j.title, j.id, a.extracted_skills, a.extracted_exp, a.match_score, 
                           a.match_feedback, a.application_date, a.status
                    FROM applications a
                    JOIN jobs j ON a.job_id = j.id
                    WHERE j.posted_by = ? AND a.status = ?
                    ORDER BY a.match_score DESC
                """, (st.session_state.user, status_filter))
        else:
            job_id = int(job_filter.split(" - ")[0])
            if status_filter == "All Statuses":
                c.execute("""
                    SELECT a.id, a.username, j.title, j.id, a.extracted_skills, a.extracted_exp, a.match_score, 
                           a.match_feedback, a.application_date, a.status
                    FROM applications a
                    JOIN jobs j ON a.job_id = j.id
                    WHERE j.posted_by = ? AND a.job_id = ?
                    ORDER BY a.match_score DESC
                """, (st.session_state.user, job_id))
            else:
                c.execute("""
                    SELECT a.id, a.username, j.title, j.id, a.extracted_skills, a.extracted_exp, a.match_score, 
                           a.match_feedback, a.application_date, a.status
                    FROM applications a
                    JOIN jobs j ON a.job_id = j.id
                    WHERE j.posted_by = ? AND a.job_id = ? AND a.status = ?
                    ORDER BY a.match_score DESC
                """, (st.session_state.user, job_id, status_filter))
        
        applications = c.fetchall()
        
        if not applications:
            st.info("No applications found for the selected filters.")
        else:
            st.write(f"Found {len(applications)} application(s)")
            
            # Display applications
            for app in applications:
                with st.expander(f"📄 {app[1]} - {app[2]} - Match: {app[6]:.1f}%"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Application details
                        st.markdown(f"**Current Status:** {display_application_status(app[9])}", unsafe_allow_html=True)
                        st.markdown(f"**Application Date:** {app[8].split()[0] if app[8] else 'N/A'}")
                        
                        st.markdown("**Candidate Skills:**")
                        st.write(app[4])
                        
                        st.markdown("**Experience Summary:**")
                        st.write(app[5])
                    
                    with col2:
                        # Match analysis and actions
                        st.markdown("**Match Analysis:**")
                        
                        # Create a color based on the match score
                        if app[6] >= 80:
                            score_color = "green"
                            recommendation = "Strong match"
                        elif app[6] >= 60:
                            score_color = "orange"
                            recommendation = "Potential match"
                        else:
                            score_color = "red"
                            recommendation = "Low match"
                        
                        st.markdown(f'<p style="font-size:1.2rem; font-weight:bold; color:{score_color};">Match Score: {app[6]:.1f}% ({recommendation})</p>', unsafe_allow_html=True)
                        st.write(app[7])
                        
                        # Update status
                        new_status = st.selectbox(
                            "Update Application Status",
                            ["Pending", "Interview", "Accepted", "Rejected"],
                            index=["Pending", "Interview", "Accepted", "Rejected"].index(app[9]),
                            key=f"status_{app[0]}"
                        )
                        
                        if new_status != app[9]:
                            if st.button("Update Status", key=f"update_{app[0]}"):
                                update_job_status(app[0], new_status)
                                st.success(f"Status updated to: {new_status}")
                                time.sleep(1)
                                st.rerun()

def bulk_analysis_view():
    st.markdown("## Bulk Resume Analysis")
    
    # Get jobs posted by this employer
    import sqlite3
    conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, title FROM jobs WHERE posted_by=?", (st.session_state.user,))
    employer_jobs = c.fetchall()
    
    if not employer_jobs:
        st.info("You haven't posted any jobs yet. Go to 'Post Job' to create your first listing.")
    else:
        # Job selection
        job_selection = st.selectbox(
            "Select job to match resumes against", 
            [f"{job[0]} - {job[1]}" for job in employer_jobs]
        )
        job_id = int(job_selection.split(" - ")[0])
        
        # Get job requirements for context
        job = get_job_by_id(job_id)
        
        if job:
            with st.expander("View Job Requirements"):
                st.write(job[4])
        
        # File upload for multiple resumes
        st.markdown("### Upload Resumes")
        st.markdown('<div class="help-text">Upload multiple resume text files (.txt) for batch analysis. Our AI will analyze each resume and match it against the selected job requirements.</div>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader("Upload resumes", type=["txt"], accept_multiple_files=True)
        
        if uploaded_files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {len(uploaded_files)} files uploaded")
            with col2:
                analyze_button = st.button("Analyze Resumes", type="primary")
            
            if analyze_button:
                with st.spinner("Analyzing resumes... This may take a moment"):
                    # Process the batch of resumes
                    results = process_bulk_resumes(uploaded_files, job_id, job[2], job[4])
                    
                    if "error" in results:
                        st.error(results["error"])
                    else:
                        # Store results in session state for persistence
                        st.session_state.bulk_results = results
                
                # Show results if available
                if hasattr(st.session_state, 'bulk_results'):
                    # Convert to DataFrame for easier display
                    df = pd.DataFrame(st.session_state.bulk_results)
                    
                    # Create a visualization of the scores
                    st.markdown("### Match Score Overview")
                    
                    # Create a bar chart of scores
                    chart_data = pd.DataFrame({
                        'Resume': df['filename'],
                        'Match Score': df['match_score']
                    }).sort_values(by='Match Score', ascending=False)
                    
                    chart = alt.Chart(chart_data).mark_bar().encode(
                        x=alt.X('Match Score:Q', title='Match Score (%)'),
                        y=alt.Y('Resume:N', sort='-x', title='Resume'),
                        color=alt.Color('Match Score:Q', scale=alt.Scale(
                            domain=[0, 50, 100],
                            range=['#F44336', '#FF9800', '#4CAF50']
                        )),
                        tooltip=['Resume', 'Match Score']
                    ).properties(
                        width=600,
                        height=min(30 * len(df), 500)
                    )
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Display summary table
                    st.markdown("### Resume Ranking")
                    summary_df = df[["filename", "match_score"]].sort_values(by="match_score", ascending=False)
                    summary_df = summary_df.rename(columns={"filename": "Resume", "match_score": "Match Score"})
                    summary_df["Match Score"] = summary_df["Match Score"].apply(lambda x: f"{x:.1f}%")
                    st.table(summary_df)
                    
                    # Show full details in expandable sections
                    st.markdown("### Detailed Analysis")
                    for i, row in df.iterrows():
                        with st.expander(f"📄 {row['filename']} - Match Score: {row['match_score']:.1f}%"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### Skills")
                                st.write(row["skills"])
                                
                                st.markdown("#### Experience")
                                st.write(row["experience"])
                            
                            with col2:
                                st.markdown("#### Match Analysis")
                                st.write(row["match_feedback"])
                            
                            # Option to save this candidate to applications
                            if st.button(f"Save to Applications", key=f"save_{i}"):
                                try:
                                    # Extract resume text if available
                                    if "resume_text" in row:
                                        resume_text = row["resume_text"]
                                    else:
                                        # Get the resume content from the uploaded file
                                        resume_file = [f for f in uploaded_files if f.name == row['filename']][0]
                                        resume_text = resume_file.getvalue().decode("utf-8")
                                    
                                    # Generate a username from filename
                                    username = row['filename'].replace(".txt", "").replace("_", " ")
                                    
                                    # Save to applications with a temporary username based on the filename
                                    from database import apply_to_job
                                    apply_to_job(
                                        username=username,
                                        job_id=job_id,
                                        resume=resume_text,
                                        skills=row["skills"],
                                        experience=row["experience"],
                                        match_score=row["match_score"],
                                        match_feedback=row["match_feedback"]
                                    )
                                    st.success(f"✅ Added {username} to applications!")
                                except Exception as e:
                                    st.error(f"Error saving application: {str(e)}")