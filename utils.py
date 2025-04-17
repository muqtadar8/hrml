import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import base64
from io import StringIO

def display_match_score(score):
    """Display match score with appropriate styling"""
    if score >= 80:
        return f'<span class="match-high">{score:.1f}%</span>'
    elif score >= 60:
        return f'<span class="match-medium">{score:.1f}%</span>'
    else:
        return f'<span class="match-low">{score:.1f}%</span>'

def display_application_status(status):
    """Display application status with color coding"""
    if status == "Accepted":
        return f'<span style="color:#4CAF50; font-weight:bold;">●</span> {status}'
    elif status == "Rejected":
        return f'<span style="color:#F44336; font-weight:bold;">●</span> {status}'
    elif status == "Interview":
        return f'<span style="color:#2196F3; font-weight:bold;">●</span> {status}'
    else:  # Pending
        return f'<span style="color:#FF9800; font-weight:bold;">●</span> {status}'

def generate_match_gauge(score):
    """Generate a gauge chart for match score visualization"""
    # Define the chart data
    source = pd.DataFrame({
        'category': ['Match Score'],
        'value': [score]
    })

    # Create a gauge chart using Altair
    gauge = alt.Chart(source).mark_arc(
        innerRadius=50,
        outerRadius=80,
        startAngle=-np.pi/2,
        endAngle=np.pi/2
    ).encode(
        theta=alt.Theta(
            'value:Q',
            scale=alt.Scale(domain=[0, 100], range=[-np.pi/2, np.pi/2])
        ),
        color=alt.Color(
            'value:Q',
            scale=alt.Scale(
                domain=[0, 50, 100],
                range=['#F44336', '#FF9800', '#4CAF50']
            ),
            legend=None
        )
    ).properties(
        width=200,
        height=120
    )
    
    # Add a text mark for the value
    text = alt.Chart(source).mark_text(
        align='center',
        baseline='middle',
        fontSize=20,
        fontWeight='bold'
    ).encode(
        text=alt.Text('value:Q', format='.1f'),
        color=alt.value('#212121')
    ).properties(
        width=200,
        height=120
    )
    
    return gauge + text

def generate_skills_match_chart(required_skills, candidate_skills):
    """Generate a chart showing skill matches between job requirements and candidate"""
    # This is a placeholder implementation - in a real app, you'd parse skills more thoroughly
    
    # For demonstration, create some sample data
    required = [s.strip() for s in required_skills.lower().split(',')]
    candidate = [s.strip() for s in candidate_skills.lower().split(',')]
    
    # Find matches and missing skills
    matches = [skill for skill in required if any(s in skill for s in candidate)]
    missing = [skill for skill in required if skill not in matches]
    
    # Create a dataframe for visualization
    data = pd.DataFrame({
        'Skill': matches + missing,
        'Status': ['Match']*len(matches) + ['Missing']*len(missing)
    })
    
    # Create chart
    if not data.empty:
        chart = alt.Chart(data).mark_bar().encode(
            y=alt.Y('Skill:N', sort='-x'),
            x=alt.X('count():Q', title=''),
            color=alt.Color('Status:N', scale=alt.Scale(
                domain=['Match', 'Missing'],
                range=['#4CAF50', '#F44336']
            )),
            tooltip=['Skill', 'Status']
        ).properties(
            width=300,
            height=min(30 * len(data), 300)
        )
        return chart
    else:
        return None