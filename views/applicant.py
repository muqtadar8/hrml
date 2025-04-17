import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import random
from utils import display_match_score, display_application_status
from database import get_jobs, search_jobs, get_applications_by_user

def browse_jobs_view():
    st.markdown("## Available Jobs")
    
    # Search box
    search_query = st.text_input("Search jobs by title, description, or requirements", placeholder="e.g., Python Developer, Marketing, Remote")
    
    # Get jobs
    if search_query:
        jobs = search_jobs(search_query)
        if jobs:
            st.write(f"Found {len(jobs)} jobs matching '{search_query}'")
        else:
            st.info(f"No jobs found matching '{search_query}'")
    else:
        jobs = get_jobs()
    
    # Display jobs
    if not jobs:
        st.info("No jobs available at the moment. Please check back later.")
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            # Get unique locations
            conn = sqlite3.connect("hr_match_portal.db", check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT DISTINCT location FROM jobs WHERE location != ''")
            locations = [loc[0] for loc in c.fetchall()]
            location_filter = st.selectbox("Location", ["All Locations"] + locations)
        
        with col2:
            # Get unique job types
            c.execute("SELECT DISTINCT job_type FROM jobs WHERE job_type != ''")
            job_types = [jt[0] for jt in c.fetchall()]
            type_filter = st.selectbox("Job Type", ["All Types"] + job_types)
        
        with col3:
            # Sort options
            sort_option = st.selectbox("Sort By", ["Newest First", "Salary (High to Low)", "Salary (Low to High)"])
        
        # Apply filters
        filtered_jobs = []
        for job in jobs:
            include = True
            
            # Apply location filter
            if location_filter != "All Locations" and job[6] != location_filter:
                include = False
                
            # Apply job type filter
            if type_filter != "All Types" and job[7] != type_filter:
                include = False
                
            if include:
                filtered_jobs.append(job)
        
        # Apply sorting
        if sort_option == "Newest First":
            # Already sorted by created_at DESC
            pass
        elif sort_option == "Salary (High to Low)" or sort_option == "Salary (Low to High)":
            # This is a simplified implementation - in a real app, you'd parse salary ranges properly
            # Sort by the first number found in the salary range
            def extract_salary(job):
                salary = job[5] or ""
                # Extract first number found
                import re
                numbers = re.findall(r'\d+', salary)
                if numbers:
                    return int(numbers[0])
                return 0
                
            filtered_jobs.sort(key=extract_salary, reverse=(sort_option == "Salary (High to Low)"))
        
        # Display results
        if not filtered_jobs:
            st.info("No jobs match the selected filters.")
        else:
            st.write(f"Showing {len(filtered_jobs)} job(s)")
            
            # Display jobs in a grid
            col1, col2 = st.columns(2)
            
            for i, job in enumerate(filtered_jobs):
                with (col1 if i % 2 == 0 else col2):
                    with st.container():
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"### {job[1]}")
                        st.markdown(f"**Posted by:** {job[3]}")
                        
                        st.markdown(f"**Location:** {job[6] or 'Not specified'}")
                        st.markdown(f"**Type:** {job[7] or 'Not specified'}")
                        st.markdown(f"**Salary:** {job[5] or 'Not specified'}")
                        
                        # Show a preview of the description
                        st.markdown("**Description:**")
                        preview = job[2][:150] + "..." if len(job[2]) > 150 else job[2]
                        st.write(preview)
                        
                        # View full job and apply buttons
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("View Details", key=f"view_{job[0]}"):
                                st.session_state.view_job = job[0]
                                st.rerun()
                        with col_b:
                            if st.button("Quick Apply", key=f"apply_{job[0]}"):
                                st.session_state.selected_job = job[0]
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

def my_applications_view():
    st.markdown("## My Applications")
    
    applications = get_applications_by_user(st.session_state.user)
    
    if not applications:
        st.info("You haven't applied to any jobs yet. Browse available jobs to start applying.")
        return
    
    st.write(f"You have applied to {len(applications)} job(s)")
    
    # Group by status for a dashboard view
    status_counts = {}
    for app in applications:
        status = app[6]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create a horizontal bar chart for statuses
    status_data = pd.DataFrame({
        'Status': list(status_counts.keys()),
        'Count': list(status_counts.values())
    })
    if not status_data.empty:
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
    
    # Create tabs for different statuses
    status_tabs = st.tabs(["All Applications", "Pending", "Interview", "Accepted", "Rejected"])
    
    # ---- All Applications Tab ----
    with status_tabs[0]:
        display_apps = applications
        if not display_apps:
            st.info("No applications in this category.")
        else:
            for idx, app in enumerate(display_apps):
                with st.markdown(f"{app[1]} - {display_application_status(app[6])}", unsafe_allow_html=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Employer:** {app[2]}")
                        st.markdown(f"**Applied:** {app[5].split()[0] if app[5] else 'N/A'}")
                        if st.button("View Job Details", key=f"view_job_all_{app[7]}_{idx}"):
                            st.session_state.view_job = app[7]
                            st.rerun()
                    with col2:
                        st.markdown(f"**Match Score:** {display_match_score(app[3])}", unsafe_allow_html=True)
                        st.markdown("**Match Analysis:**")
                        st.write(app[4])
    
    # ---- Status-Specific Tabs ----
    for i, status in enumerate(["Pending", "Interview", "Accepted", "Rejected"]):
        with status_tabs[i + 1]:
            display_apps = [app for app in applications if app[6] == status]
            if not display_apps:
                st.info(f"No applications with status: {status}")
            else:
                for idx, app in enumerate(display_apps):
                    with st.expander(f"{app[1]} - {app[2]}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Applied:** {app[5].split()[0] if app[5] else 'N/A'}")
                            if st.button("View Job Details", key=f"view_job_status_{status}_{app[7]}_{idx}"):
                                st.session_state.view_job = app[7]
                                st.rerun()
                        with col2:
                            st.markdown(f"**Match Score:** {display_match_score(app[3])}", unsafe_allow_html=True)
                            st.markdown("**Match Analysis:**")
                            st.write(app[4])

