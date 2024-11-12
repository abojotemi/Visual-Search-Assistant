# main.py
import streamlit as st
from time import sleep
import base64
from gtts import gTTS
import plotly.express as px
from datetime import datetime
import pandas as pd
from llm import render_llm, summarizer, workout_planner
from pydantic import BaseModel, Field, ValidationError
import pycountry
import io
import re
from workout import predict_image

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
    # Initialize session state for profile and progress data
    if 'profile_completed' not in st.session_state:
        st.session_state.profile_completed = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'progress_data' not in st.session_state:
        st.session_state.progress_data = []

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
    
    st.title("🏋️‍♂️ Fit AI - Your Personal Fitness Coach")
    
    # Create tabs
    tabs = st.tabs(["Profile", "Workout", "Progress", "Analytics"])
    
    # Profile Tab
    with tabs[0]:
        st.header("Your Profile")
        name = st.text_input("Enter your name", value=st.session_state.user_info.name if st.session_state.user_info else "")
        col1, col2 = st.columns(2)
        age = col1.number_input("Enter your age", min_value=10, value=st.session_state.user_info.age if st.session_state.user_info else 10)
        sex = col2.radio("Select your sex", ["Male", "Female", "Other"], 
                        index=["Male", "Female", "Other"].index(st.session_state.user_info.sex) if st.session_state.user_info else 0)
        weight = col1.number_input("Enter your weight (in kilograms)", min_value=30.0,
                                 value=st.session_state.user_info.weight if st.session_state.user_info else 30.0)
        height = col2.number_input("Enter your height (in centimeters)", min_value=120.0,
                                 value=st.session_state.user_info.height if st.session_state.user_info else 120.0)
        countries = [country.name for country in pycountry.countries]
        country = col1.selectbox("Pick your country", countries, 
                               index=countries.index(st.session_state.user_info.country) if st.session_state.user_info else 234)
        goals = st.text_area("What are your fitness goals?", 
                           value=st.session_state.user_info.goals if st.session_state.user_info else "")
        
        if st.button("Save Information"):
            try:
                info = Info(name=name, age=age, sex=sex, weight=weight, 
                          height=height, goals=goals, country=country)
                st.session_state.user_info = info
                st.session_state.profile_completed = True
                # st.rerun()  # Rerun the app to update all tabs
                st.success(f"Information saved successfully. Welcome, {info.name}!")
                
            except ValidationError as e:
                st.error(f"Error: {str(e)}")

    # Only show other tabs if profile is completed
    if st.session_state.profile_completed and st.session_state.user_info is not None:
        # Workout Tab
        with tabs[0]:
            if st.button("Generate Personalized Plan"):
                    with st.spinner("Creating your personalized fitness journey..."):
                        msg = render_llm(st.session_state.user_info)
                        
                        # Convert the workout plan to speech
                        st.markdown("### 🎧 Listen to Your Plan")
                        st.markdown(text_to_speech(summarizer(msg.content)), unsafe_allow_html=True)
                        
                        # Display the plan
                        st.markdown("### 📋 Your Plan")
                        st.markdown(msg.content)
        with tabs[1]:
            st.header("Today's Workout")
            img = st.file_uploader("Drag or drop a picture of your workout tools here", type=['png', 'jpg', 'jpeg', 'gif'])
            if img is not None:
                st.image(img)
                if st.button("Analyze"):
                    with st.spinner("Analyzing Image..."):
                        text = predict_image(img)
                    st.write(text)
                    with st.spinner("Generating workout plan..."):
                        workout_plan = workout_planner(text, st.session_state.user_info.model_dump())
                    st.markdown("### 📋 Your Workout Plan")
                    st.markdown(workout_plan)

        # Progress Tab
        with tabs[2]:
            st.header("Track Your Progress")
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

        # Analytics Tab
        with tabs[3]:
            st.header("Analytics Dashboard")
            if st.session_state.progress_data:
                df = pd.DataFrame(st.session_state.progress_data)
                
                fig_weight = px.line(df, x="date", y="weight", 
                                   title="Weight Progress Over Time",
                                   labels={"weight": "Weight (kg)", "date": "Date"})
                st.plotly_chart(fig_weight)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_mood = px.pie(df, names="mood", title="Energy Level Distribution")
                    st.plotly_chart(fig_mood)
                
                with col2:
                    fig_intensity = px.pie(df, names="intensity", 
                                         title="Workout Intensity Distribution")
                    st.plotly_chart(fig_intensity)
                
                if st.button("Download Progress Report"):
                    csv = df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="fitness_progress.csv">Download CSV File</a>'
                    st.markdown(href, unsafe_allow_html=True)
    else:
        # Show message in other tabs when profile is not completed
        for tab in tabs[1:]:
            with tab:
                st.info("Please complete your profile in the Profile tab before accessing this section.")


if __name__ == "__main__":
    main()
        
