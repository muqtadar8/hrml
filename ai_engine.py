import streamlit as st
from teapotai import TeapotAI
import time

# Initialize TeapotAI
@st.cache_resource(show_spinner=False)
def load_teapot():
    with st.spinner("Loading AI engine..."):
        return TeapotAI()

# Load TeapotAI instance
teapot_ai = load_teapot()

def extract_resume_info(resume_text):
    """Extract structured information from a resume using TeapotAI"""
    # Process starts
    with st.spinner("Analyzing resume content..."):
        # Extract skills with detailed query
        skills_query = """
        Extract a comprehensive list of skills from this resume. 
        Include technical skills, soft skills, and domain expertise.
        Format as a comma-separated list.
        """
        skills = teapot_ai.query(query=skills_query, context=resume_text)
        
        # Extract experience summary
        experience_query = """
        Provide a concise professional summary from this resume.
        Include key information about:
        - Years of experience
        - Industries worked in
        - Major accomplishments
        - Leadership roles (if any)
        - Educational background
        Limit to 3-4 sentences.
        """
        experience = teapot_ai.query(query=experience_query, context=resume_text)
        
        # Return the structured information
        return {
            "skills": skills,
            "experience": experience
        }

def match_resume_to_job(resume_text, job_description, job_requirements):
    """Match resume against job description and requirements, with detailed analysis"""
    with st.spinner("Calculating job match score..."):
        # Combine job information
        combined_job_info = f"Job Description: {job_description}\n\nJob Requirements: {job_requirements}"
        st.write(combined_job_info)
        st.write(resume_text)
        
        # Generate a detailed match analysis
        match_query = f"""
        Analyze how well this candidate's resume matches the job requirements. 
        
        Part 1: Provide a match score from 0-100 as a single number on the first line just the number.
        
        Part 2: Provide a detailed analysis including:
        - Key matching skills and qualifications
        - Missing or mismatched requirements
        - Overall suitability assessment
        - Recommendations for the hiring manager
        
        Format your response with the score on the first line, followed by your analysis.
        
        """
        
        match_analysis = teapot_ai.query(
            query=match_query,
            context=f"Here is the Candidate's Resume:\n{resume_text}\n and Here is the \n{combined_job_info}"
        )
        st.write(match_analysis)    
        
        # Extract score from analysis (first line should be just the score)
        lines = match_analysis.strip().split('\n')
        try:
            match_score = float(lines[0].strip())
            # Cap at 100
            match_score = min(match_score, 100.0)
        except:
            # Default score if parsing fails
            match_score = 50.0
            
        # The feedback is everything after the first line
        match_feedback = '\n'.join(lines[1:]) if len(lines) > 1 else match_analysis
        
        return {
            "score": match_score,
            "feedback": match_feedback
        }

def process_bulk_resumes(resume_files, job_id, job_description, job_requirements):
    """Process multiple resume files and match against a job"""
    if not job_id:
        return {"error": "Job not found"}
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, resume_file in enumerate(resume_files):
        try:
            # Update progress
            progress = (idx) / len(resume_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {idx+1} of {len(resume_files)}: {resume_file.name}")
            
            # Read the file content
            resume_text = resume_file.getvalue().decode("utf-8")
            filename = resume_file.name
            
            # Extract info and match to job
            extracted = extract_resume_info(resume_text)
            match_result = match_resume_to_job(resume_text, job_description, job_requirements)
            
            results.append({
                "filename": filename,
                "skills": extracted["skills"],
                "experience": extracted["experience"],
                "match_score": match_result["score"],
                "match_feedback": match_result["feedback"],
                "resume_text": resume_text  # Include the full text for later use
            })
            
            # Pause to prevent overwhelming the API
            time.sleep(0.5)
            
        except Exception as e:
            results.append({
                "filename": resume_file.name,
                "error": str(e)
            })
    
    # Complete the progress bar
    progress_bar.progress(1.0)
    status_text.text("Analysis complete!")
    
    return results