import streamlit as st
import time
from database import get_job_by_id, get_applications_by_job, apply_to_job
from ai_engine import extract_resume_info, match_resume_to_job
from utils import display_match_score, display_application_status, generate_match_gauge
import pandas as pd
import altair as alt

def job_detail_view():
    """Display detailed view of a specific job"""
    job = get_job_by_id(st.session_state.view_job)
    
    if job:
        st.markdown(f"## {job[1]}")
        
        # Job details
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Posted by:** {job[3]}")
            st.markdown(f"**Location:** {job[6] or 'Not specified'}")
            st.markdown(f"**Type:** {job[7] or 'Not specified'}")
            st.markdown(f"**Salary:** {job[5] or 'Not specified'}")
            
            st.markdown("### Job Description")
            st.write(job[2])
            
            st.markdown("### Requirements")
            st.write(job[4])
        
        with col2:
            # Apply button
            if st.button("Apply Now", type="primary"):
                st.session_state.selected_job = job[0]
                st.session_state.view_job = None
                st.rerun()
            
            # Back button
            if st.button("Back to Jobs"):
                st.session_state.view_job = None
                st.rerun()

def job_applications_view():
    """Display all applications for a specific job"""
    job = get_job_by_id(st.session_state.view_job_applications)
    
    if job:
        st.markdown(f"## Applications for: {job[1]}")
        
        applications = get_applications_by_job(job[0])
        
        if not applications:
            st.info("No applications for this job yet.")
        else:
            st.write(f"Total applications: {len(applications)}")
            
            # Group by status
            status_counts = {}
            for app in applications:
                status = app[8]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Create a bar chart for statuses
            if status_counts:
                status_data = pd.DataFrame({
                    'Status': list(status_counts.keys()),
                    'Count': list(status_counts.values())
                })
                
                # Display a bar chart
                status_chart = alt.Chart(status_data).mark_bar().encode(
                    x='Count:Q',
                    y=alt.Y('Status:N', sort='-x'),
                    color=alt.Color('Status:N', scale=alt.Scale(
                        domain=['Pending', 'Interview', 'Accepted', 'Rejected'],
                        range=['#FF9800', '#2196F3', '#4CAF50', '#F44336']
                    )),
                    tooltip=['Status', 'Count']
                ).properties(
                    width=300,
                    height=150
                )
                
                st.altair_chart(status_chart, use_container_width=True)
            
            # Display applications grouped by status
            status_tabs = st.tabs(["All Applications", "Pending", "Interview", "Accepted", "Rejected"])
            
            with status_tabs[0]:
                for app in applications:
                    with st.expander(f"{app[1]} - Match: {app[5]:.1f}%"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Status:** {display_application_status(app[8])}", unsafe_allow_html=True)
                            st.markdown(f"**Applied:** {app[7].split()[0] if app[7] else 'N/A'}")
                            
                            st.markdown("**Skills:**")
                            st.write(app[3])
                            
                            st.markdown("**Experience:**")
                            st.write(app[4])
                        
                        with col2:
                            st.markdown(f"**Match Score:** {display_match_score(app[5])}", unsafe_allow_html=True)
                            st.markdown("**Match Analysis:**")
                            st.write(app[6])
                            
                            # Update status
                            from database import update_job_status
                            new_status = st.selectbox(
                                "Update Application Status",
                                ["Pending", "Interview", "Accepted", "Rejected"],
                                index=["Pending", "Interview", "Accepted", "Rejected"].index(app[8]),
                                key=f"job_app_status_{app[0]}"
                            )
                            
                            if new_status != app[8]:
                                if st.button("Update Status", key=f"update_job_app_{app[0]}"):
                                    update_job_status(app[0], new_status)
                                    st.success(f"Status updated to: {new_status}")
                                    time.sleep(1)
                                    st.rerun()
            
            # Filter applications by status for the remaining tabs
            for i, status in enumerate(["Pending", "Interview", "Accepted", "Rejected"]):
                with status_tabs[i+1]:
                    display_apps = [app for app in applications if app[8] == status]
                    if not display_apps:
                        st.info(f"No applications with status: {status}")
                    else:
                        for app in display_apps:
                            with st.expander(f"{app[1]} - Match: {app[5]:.1f}%"):
                                # Similar content as above, but for filtered status
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown(f"**Applied:** {app[7].split()[0] if app[7] else 'N/A'}")
                                    
                                    st.markdown("**Skills:**")
                                    st.write(app[3])
                                    
                                    st.markdown("**Experience:**")
                                    st.write(app[4])
                                
                                with col2:
                                    st.markdown(f"**Match Score:** {display_match_score(app[5])}", unsafe_allow_html=True)
                                    st.markdown("**Match Analysis:**")
                                    st.write(app[6])
                                    
                                    # Update status
                                    from database import update_job_status
                                    new_status = st.selectbox(
                                        "Update Application Status",
                                        ["Pending", "Interview", "Accepted", "Rejected"],
                                        index=["Pending", "Interview", "Accepted", "Rejected"].index(app[8]),
                                        key=f"job_app_status_{app[0]}_{i}"
                                    )
                                    
                                    if new_status != app[8]:
                                        if st.button("Update Status", key=f"update_job_app_{app[0]}_{i}"):
                                            update_job_status(app[0], new_status)
                                            st.success(f"Status updated to: {new_status}")
                                            time.sleep(1)
                                            st.rerun()

def application_form_view():
   """Display the application form for a selected job"""
   job = get_job_by_id(st.session_state.selected_job)
   
   if job:
       st.header(f"Apply for: {job[1]}")
       
       with st.expander("View Job Details"):
           st.markdown("### Job Description")
           st.write(job[2])
           
           if job[4]:  # If requirements exist
               st.markdown("### Requirements")
               st.write(job[4])
       
       st.subheader("Paste Your Resume Below")
       resume_text = st.text_area("Resume", height=300)
       
       if st.button("Analyze Resume and Apply", type="primary"):
           if resume_text:
               with st.spinner("Analyzing your resume..."):
                   try:
                       # Generate a random match score for testing
                       import random
                       match_score = random.uniform(50.0, 95.0)
                       
                       # Extract info from resume
                       # extracted = extract_resume_info(resume_text)
                       
                       # Generate random feedback
                       feedback_options = [
                           "Your experience aligns well with the job requirements.",
                           "Consider highlighting more relevant skills for this position.",
                           "Your technical skills match what the employer is looking for.",
                           "Your resume shows strong qualifications for this role."
                       ]
                       match_feedback = random.choice(feedback_options)
                       
                       # Create a match result dictionary
                       match_result = {
                           "score": match_score,
                           "feedback": match_feedback
                       }
                       
                       # Extract skills directly from resume text as fallback
                       if not extracted["skills"] or len(extracted["skills"]) < 3:
                           # Simple extraction of potential skills based on resume sections
                           resume_parts = resume_text.lower().split('\n')
                           potential_skills = []
                           
                           # Look for skills section and extract items
                           in_skills_section = False
                           for line in resume_parts:
                               if "skills" in line.lower() or "technologies" in line.lower():
                                   in_skills_section = True
                                   continue
                               
                               if in_skills_section and line.strip():
                                   # Extract comma or bullet separated items
                                   if ',' in line:
                                       skills_items = [s.strip() for s in line.split(',')]
                                       potential_skills.extend(skills_items)
                                   elif '•' in line or '-' in line:
                                       skill = line.replace('•', '').replace('-', '').strip()
                                       potential_skills.append(skill)
                                   else:
                                       potential_skills.append(line.strip())
                               
                               # Exit skills section when we hit another heading
                               if in_skills_section and line.strip() and line.strip().endswith(':'):
                                   in_skills_section = False
                           
                           # If we found potential skills, use them
                           if potential_skills:
                               extracted["skills"] = potential_skills[:10]  # Limit to 10 skills
                       
                       # Save application
                       apply_to_job(
                           username=st.session_state.user,
                           job_id=st.session_state.selected_job,
                           resume=resume_text,
                           skills=extracted["skills"],
                           experience=extracted["experience"],
                           match_score=match_result["score"],
                           match_feedback=match_result["feedback"]
                       )
                       
                       # Display results
                       st.success("✅ Application submitted successfully!")
                       
                       col1, col2 = st.columns(2)
                       
                       with col1:
                           st.subheader("Extracted Skills")
                           st.write(extracted["skills"])
                           
                           st.subheader("Experience Summary")
                           st.write(extracted["experience"])
                       
                       with col2:
                           st.subheader("Match Analysis")
                           
                           # Create a color based on the match score
                           if match_result["score"] >= 80:
                               color = "green"
                               emoji = "🌟"
                           elif match_result["score"] >= 60:
                               color = "orange"
                               emoji = "⭐"
                           else:
                               color = "red" 
                               emoji = "⚠️"
                               
                           st.markdown(f"<h3 style='color:{color}'>{emoji} Match Score: {match_result['score']:.1f}%</h3>", unsafe_allow_html=True)
                           st.write(match_result["feedback"])
                       
                       # Option to go back to job list
                       if st.button("Back to Job Listings"):
                           st.session_state.selected_job = None
                           st.rerun()
                       
                   except Exception as e:
                       st.error(f"⚠️ Error processing resume: {str(e)}")
                       st.info("Your application was not submitted. Please try again.")
           else:
               st.error("⚠️ Please paste your resume to apply")
