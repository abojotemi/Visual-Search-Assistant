# main.py
import streamlit as st
from time import sleep
import base64
from gtts import gTTS
import plotly.express as px
from datetime import datetime
import pandas as pd
from llm import render_llm, summarize_message
from pydantic import BaseModel, Field, ValidationError
import pycountry
import io
import re

class Info(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    age: int = Field(gt=10)
    sex: str = Field(min_length=3)
    weight: float = Field(ge=30)
    height: float = Field(ge=120)
    goals: str = Field(min_length=5)
    country: str = Field(min_length=3)
    

def clean_markdown(text):
    """Remove common Markdown symbols using regular expressions"""
    # Remove headings (e.g., # Heading)
    text = re.sub(r'#', '', text)
    # Remove emphasis (e.g., **bold** or *italic*)
    text = re.sub(r'\*{1,2}', '', text)
    # Remove underscores (e.g., _italic_)
    text = re.sub(r'_', '', text)
    # Remove links (e.g., [text](url))
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def text_to_speech(text):
    """Convert text to speech and return the audio player HTML"""
    # Create gTTS object
    tts = gTTS(text=clean_markdown(text), lang='en')
    
    # Create a BytesIO object and write the audio to it
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    
    # Rewind the BytesIO object to the beginning
    audio_fp.seek(0)
    
    # Encode the audio content to base64
    audio_str = base64.b64encode(audio_fp.read()).decode()
    
    # Generate HTML audio player
    audio_html = f'''
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{audio_str}" type="audio/mp3">
        </audio>
    '''
    
    return audio_html


def create_workout_card(exercise, sets, reps, rest):
    """Create a visually appealing workout card"""
    card_html = f'''
    <div style="
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1)
    ">
        <h3 style="color: #0066cc; margin: 0 0 10px 0">{exercise}</h3>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px">
            <span style="background: #0066cc; color: white; padding: 5px 10px; border-radius: 5px">
                Sets: {sets}
            </span>
            <span style="background: #0066cc; color: white; padding: 5px 10px; border-radius: 5px">
                Reps: {reps}
            </span>
            <span style="background: #0066cc; color: white; padding: 5px 10px; border-radius: 5px">
                Rest: {rest}s
            </span>
        </div>
    </div>
    '''
    return card_html

def main():
    st.set_page_config(page_title="Fit AI", page_icon="💪", layout="wide")
    
    # Add custom CSS for better styling
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #0066cc;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for tracking progress
    if 'progress_data' not in st.session_state:
        st.session_state.progress_data = []
    
    st.title("🏋️‍♂️ Fit AI - Your Personal Fitness Coach")
    
    tabs = st.tabs(["Profile", "Workout", "Progress", "Analytics"])
    
    with tabs[0]:
        st.header("Your Profile")
        name = st.text_input("Enter your name")
        col1, col2 = st.columns(2)
        age = col1.number_input("Enter your age", min_value=10)
        sex = col2.radio("Select your sex", ["Male", "Female", "Other"])
        weight = col1.number_input("Enter your weight (in kilograms)", min_value=30.0)
        height = col2.number_input("Enter your height (in centimeters)", min_value=120.0)
        countries = [country.name for country in pycountry.countries]
        country = col1.selectbox("Pick your country", countries, 234)
        goals = st.text_area("What are your fitness goals?")
        
        if st.button("Generate Personalized Plan"):
            try:
                with st.spinner("Creating your personalized fitness journey..."):
                    info = Info(name=name, age=age, sex=sex, weight=weight, 
                              height=height, goals=goals, country=country)
                    msg = render_llm(info)
                    
                    # Convert the workout plan to speech
                    st.markdown("### 🎧 Listen to Your Plan")
                    st.markdown(text_to_speech(summarzier(msg.content)), unsafe_allow_html=True)
                    
                    # Display the plan
                    st.markdown("### 📋 Your Plan")
                    st.markdown(msg.content)
                    
            except ValidationError as e:
                st.error(f"Error: {str(e)}")
    
    with tabs[1]:
        st.header("Today's Workout")
        
        # Sample workout data - you can replace this with the LLM generated workout
        workout_data = [
            {"exercise": "Push-ups", "sets": 3, "reps": 12, "rest": 30},
            {"exercise": "Squats", "sets": 4, "reps": 15, "rest": 60},
            {"exercise": "Plank", "sets": 3, "reps": 1, "rest": 15}
        ]
        
        # Create interactive workout cards
        for exercise in workout_data:
            st.markdown(
                create_workout_card(
                    exercise["exercise"],
                    exercise["sets"],
                    exercise["reps"],
                    exercise["rest"]
                ),
                unsafe_allow_html=True
            )
            
            if st.button(f"Start {exercise['exercise']}"):
                # Create audio instructions
                instructions = f"Let's do {exercise['reps']} {exercise['exercise']} for {exercise['sets']} sets. Rest for {exercise['rest']} seconds between sets."
                st.markdown(text_to_speech(instructions), unsafe_allow_html=True)
                
                # Add a countdown timer
                with st.empty():
                    for remaining in range(exercise["rest"], 0, -1):
                        st.write(f"⏱️ Rest for: {remaining} seconds")
                        sleep(1)
                    st.success("Time to start the next set! 💪")
    
    with tabs[2]:
        st.header("Track Your Progress")
        
        # Progress logging
        col1, col2, col3 = st.columns(3)
        new_weight = col1.number_input("Today's Weight (kg)", min_value=30.0, key="weight_input")
        mood = col2.select_slider("Energy Level", options=["Low", "Medium", "High"])
        workout_intensity = col3.select_slider("Workout Intensity", options=["Light", "Moderate", "Intense"])
        
        if st.button("Log Progress"):
            st.session_state.progress_data.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "weight": new_weight,
                "mood": mood,
                "intensity": workout_intensity
            })
            st.success("Progress logged successfully! 🎯")
            
            # Play success sound
            success_audio = """
            <audio autoplay>
                <source src="data:audio/wav;base64,//uQxAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAADAAAGhgBVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVWqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqr///////////////////////////////////////////8AAAA8TEFNRTMuOTlyAc0AAAAAAAAAABSAJAOkQgAAgAAABobXZzfGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//sQxAADwAABpAAAACAAADSAAAAETEFNRTMuOTkuNVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVU=" type="audio/wav">
            </audio>
            """
            st.markdown(success_audio, unsafe_allow_html=True)
    
    with tabs[3]:
        st.header("Analytics Dashboard")
        
        if st.session_state.progress_data:
            # Convert progress data to DataFrame
            df = pd.DataFrame(st.session_state.progress_data)
            
            # Create weight trend chart
            fig_weight = px.line(df, x="date", y="weight", 
                               title="Weight Progress Over Time",
                               labels={"weight": "Weight (kg)", "date": "Date"})
            st.plotly_chart(fig_weight)
            
            # Create mood and intensity distribution
            col1, col2 = st.columns(2)
            
            with col1:
                fig_mood = px.pie(df, names="mood", title="Energy Level Distribution")
                st.plotly_chart(fig_mood)
            
            with col2:
                fig_intensity = px.pie(df, names="intensity", 
                                     title="Workout Intensity Distribution")
                st.plotly_chart(fig_intensity)
            
            # Download progress report
            if st.button("Download Progress Report"):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="fitness_progress.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
