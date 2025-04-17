import streamlit as st
import time
from database import register_user, login_user

def login_view():
    st.markdown("## Login")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        
        if st.button("Login", type="primary"):
            user = login_user(username, password)
            if user:
                st.session_state.user = username
                st.session_state.is_admin = bool(user[3])
                st.success(f"✅ Welcome, {username}!")
                time.sleep(1)  # Brief pause for the success message to be seen
                st.rerun()
            else:
                st.error("⚠️ Invalid username or password")
    
    with col2:
        st.markdown("""
        ### Welcome to HR Match Portal
        
        Our AI-powered platform helps:
        
        * **Employers** find the best candidates
        * **Job seekers** match with ideal positions
        * **HR professionals** streamline recruitment
        
        Get started by logging in or creating a new account.
        """)

def register_view():
    st.markdown("## Create Account")
    
    col1, col2 = st.columns(2)
    with col1:
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type='password')
    
    with col2:
        email = st.text_input("Email")
        is_admin = st.checkbox("Register as Employer")
        account_type = "Employer" if is_admin else "Job Seeker"
        st.markdown(f"*Account type: **{account_type}***")
    
    if st.button("Register", type="primary"):
        if new_user and new_pass and email:
            if "@" in email and "." in email:  # Basic email validation
                success = register_user(new_user, new_pass, email, is_admin)
                if success:
                    st.success("✅ Account created successfully! Please login.")
                else:
                    st.error("⚠️ Username already exists. Please choose another username.")
            else:
                st.error("⚠️ Please enter a valid email address.")
        else:
            st.error("⚠️ All fields are required.")