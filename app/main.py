import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import pycountry
import base64
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from dataclasses import dataclass
import logging
import json
from workout import predict_image
from llm import LLMHandler
from gtts import gTTS
import re
import io


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
@dataclass
class AppConfig:
    VALID_IMAGE_TYPES: tuple = ("png", "jpg", "jpeg", "gif")
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    DEFAULT_WEIGHT: float = 30.0
    DEFAULT_HEIGHT: float = 120.0
    DEFAULT_AGE: int = 10

class UserInfo(BaseModel):
    """User profile data model with validation"""
    name: str = Field(min_length=3, max_length=30)
    age: int = Field(gt=10)
    sex: str = Field(min_length=3)
    weight: float = Field(ge=30)
    height: float = Field(ge=120)
    goals: str = Field(min_length=5)
    country: str = Field(min_length=3)

class SessionState:
    """Manage Streamlit session state"""
    @staticmethod
    def init_session_state():
        """Initialize session state variables if they don't exist"""
        if 'profile_completed' not in st.session_state:
            st.session_state.profile_completed = False
        if 'user_info' not in st.session_state:
            st.session_state.user_info = None
        if 'progress_data' not in st.session_state:
            st.session_state.progress_data = []
        if 'workout_history' not in st.session_state:
            st.session_state.workout_history = []

    @staticmethod
    def save_progress_data():
        """Save progress data to local storage"""
        try:
            with open('progress_data.json', 'w') as f:
                json.dump(st.session_state.progress_data, f)
        except Exception as e:
            logger.error(f"Error saving progress data: {e}")

    @staticmethod
    def load_progress_data():
        """Load progress data from local storage"""
        try:
            with open('progress_data.json', 'r') as f:
                st.session_state.progress_data = json.load(f)
        except FileNotFoundError:
            st.session_state.progress_data = []
        except Exception as e:
            logger.error(f"Error loading progress data: {e}")
            st.session_state.progress_data = []

class UIComponents:
    """UI Component handlers"""
    @staticmethod
    def setup_page():
        """Configure page settings and styling"""
        st.set_page_config(
            page_title="Fit AI",
            page_icon="💪",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.markdown("""
            <style>
            .stButton>button {
                background-color: #0066cc;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #0052a3;
                transform: translateY(-2px);
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .graph-container {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_metric_card(title: str, value: Any, unit: str = ""):
        """Render a metric card with consistent styling"""
        st.markdown(f"""
            <div class="metric-card">
                <h3>{title}</h3>
                <h2>{value} {unit}</h2>
            </div>
        """, unsafe_allow_html=True)

class FitAI:
    """Main application class"""
    def __init__(self):
        self.config = AppConfig()
        SessionState.init_session_state()
        SessionState.load_progress_data()
        self.ui = UIComponents()
        
    def clean_markdown(self, text):
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

    def text_to_speech(self,text):
        """Convert text to speech and return the audio player HTML"""
        # Create gTTS object
        tts = gTTS(text=self.clean_markdown(text), lang='en')
        
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
        
    def run(self):
        """Main application entry point"""
        self.ui.setup_page()
        st.title("🏋️‍♂️ Fit AI - Your Personal Fitness Coach")
        
        # Create tabs
        tabs = st.tabs(["Profile", "Generate Workout routine", "Equipment Based Workout", "Progress", "Analytics"])
        
        # Render appropriate tab content
        with tabs[0]:
            self.render_profile_tab()
            
        if st.session_state.profile_completed:
            with tabs[1]:
                self.render_workout_tab()
            with tabs[2]:
                self.render_equipment_tab()
            with tabs[3]:
                self.render_progress_tab()
            with tabs[4]:
                self.render_analytics_tab()
        else:
            for tab in tabs[1:]:
                with tab:
                    st.info("Please complete your profile first.")

    def render_profile_tab(self):
        """Render profile tab content"""
        st.header("Your Profile")
        
        try:
            with st.form("profile_form"):
                name = st.text_input(
                    "Name",
                    value=st.session_state.user_info.name if st.session_state.user_info else "",
                    help="Enter your full name (3-30 characters)"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input(
                        "Age",
                        min_value=self.config.DEFAULT_AGE,
                        value=st.session_state.user_info.age if st.session_state.user_info else self.config.DEFAULT_AGE
                    )
                    weight = st.number_input(
                        "Weight (kg)",
                        min_value=self.config.DEFAULT_WEIGHT,
                        value=st.session_state.user_info.weight if st.session_state.user_info else self.config.DEFAULT_WEIGHT
                    )
                
                with col2:
                    sex = st.selectbox(
                        "Sex",
                        options=["Male", "Female", "Other"],
                        index=["Male", "Female", "Other"].index(st.session_state.user_info.sex) if st.session_state.user_info else 0
                    )
                    height = st.number_input(
                        "Height (cm)",
                        min_value=self.config.DEFAULT_HEIGHT,
                        value=st.session_state.user_info.height if st.session_state.user_info else self.config.DEFAULT_HEIGHT
                    )
                
                countries = [country.name for country in pycountry.countries]
                country = st.selectbox(
                    "Country",
                    options=countries,
                    index=countries.index(st.session_state.user_info.country) if st.session_state.user_info else 234
                )
                
                goals = st.text_area(
                    "Fitness Goals",
                    value=st.session_state.user_info.goals if st.session_state.user_info else "",
                    help="Describe your fitness goals (minimum 5 characters)"
                )
                
                submit = st.form_submit_button("Save Profile")
                
                if submit:
                    try:
                        info = UserInfo(
                            name=name,
                            age=age,
                            sex=sex,
                            weight=weight,
                            height=height,
                            goals=goals,
                            country=country
                        )
                        st.session_state.user_info = info
                        st.session_state.profile_completed = True
                        st.success("Profile saved successfully! 🎉")
                        st.balloons()
                    except ValidationError as e:
                        st.error(f"Please check your inputs: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error saving profile: {e}")
                        st.error("An unexpected error occurred. Please try again.")
        
        except Exception as e:
            logger.error(f"Error rendering profile tab: {e}")
            st.error("An error occurred while loading the profile form. Please refresh the page.")


    def render_workout_tab(self):
        """Render workout tab content"""
        st.header("Generate Your Workout Routine")
        if st.button("Generate Workout Routine"):
            llm = LLMHandler()
            with st.spinner("Creating your personalized fitness journey..."):
                msg = llm.render_llm(st.session_state.user_info)
                
                # Convert the workout plan to speech
                st.markdown("### 🎧 Listen to Your Plan")
                st.markdown(self.text_to_speech(llm.summarizer(msg)), unsafe_allow_html=True)
                
                # Display the plan
                st.markdown("### 📋 Your Plan")
                st.markdown(msg.content)
        
        # Generate workout routine
    def render_equipment_tab(self):
        """Render workout tab content"""
        st.header("Today's Workout")
        
        # Equipment Image Analysis
        img = st.file_uploader(
            "Upload your workout equipment photo",
            type=list(self.config.VALID_IMAGE_TYPES),
            help="Upload a clear photo of your workout equipment"
        )
        
        if img:
            try:
                st.image(img, caption="Your equipment", use_container_width=True)
                
                if st.button("Analyze Equipment"):
                    
                    with st.spinner("Analyzing your equipment..."):
                        equipment = predict_image(img)  
                        if equipment:
                            st.success("Equipment analyzed successfully!")
                            st.write("Detected equipment:", equipment)
                            
                            with st.spinner("Generating your personalized workout plan..."):
                                llm_handler = LLMHandler()
                                workout_plan = llm_handler.workout_planner(  # Assuming this function is imported
                                    equipment,
                                    st.session_state.user_info.dict()
                                )
                                
                                if workout_plan:
                                    st.markdown("### 📋 Your Personalized Workout Plan")
                                    st.markdown(workout_plan)
                                    
                                    # Save workout to history
                                    st.session_state.workout_history.append({
                                        "date": datetime.now().strftime("%Y-%m-%d"),
                                        "equipment": equipment,
                                        "plan": workout_plan
                                    })
                                else:
                                    st.error("Unable to generate workout plan. Please try again.")
                        else:
                            st.error("Unable to analyze equipment. Please try a different image.")
                            
            except Exception as e:
                logger.error(f"Error in workout tab: {e}")
                st.error("An error occurred while processing your workout. Please try again.")

    def render_progress_tab(self):
        """Render progress tracking tab content"""
        st.header("Track Your Progress")
        
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_weight = st.number_input(
                    "Today's Weight (kg)",
                    min_value=30.0,
                    value=st.session_state.user_info.weight,
                    help="Enter your current weight"
                )
                
            with col2:
                mood = st.select_slider(
                    "Energy Level",
                    options=["Low", "Medium", "High"],
                    value="Medium"
                )
                
            with col3:
                workout_intensity = st.select_slider(
                    "Workout Intensity",
                    options=["Light", "Moderate", "Intense"],
                    value="Moderate"
                )
            
            notes = st.text_area("Additional Notes", help="Any comments about today's progress?")
            
            if st.button("Log Progress"):
                progress_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "weight": new_weight,
                    "mood": mood,
                    "intensity": workout_intensity,
                    "notes": notes
                }
                
                st.session_state.progress_data.append(progress_entry)
                SessionState.save_progress_data()
                st.success("Progress logged successfully! 🎯")
                st.balloons()
        
        except Exception as e:
            logger.error(f"Error in progress tab: {e}")
            st.error("An error occurred while logging progress. Please try again.")

    def render_analytics_tab(self):
        """Render analytics dashboard tab content"""
        st.header("Analytics Dashboard")
        
        try:
            if st.session_state.progress_data:
                df = pd.DataFrame(st.session_state.progress_data)
                
                # Weight Progress Chart
                st.subheader("Weight Progress")
                fig_weight = px.line(
                    df,
                    x="date",
                    y="weight",
                    title="Weight Tracking",
                    labels={"weight": "Weight (kg)", "date": "Date"}
                )
                st.plotly_chart(fig_weight, use_container_width=True)
                
                # Mood and Intensity Distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Energy Level Distribution")
                    fig_mood = px.pie(
                        df,
                        names="mood",
                        title="Energy Levels"
                    )
                    st.plotly_chart(fig_mood, use_container_width=True)
                
                with col2:
                    st.subheader("Workout Intensity Distribution")
                    fig_intensity = px.pie(
                        df,
                        names="intensity",
                        title="Workout Intensities"
                    )
                    st.plotly_chart(fig_intensity, use_container_width=True)
                
                # Export Data Option
                if st.button("Download Progress Report"):
                    try:
                        csv = df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="fitness_progress.csv">Download CSV File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        logger.error(f"Error exporting data: {e}")
                        st.error("Unable to generate report. Please try again.")
                
            else:
                st.info("No progress data available yet. Start tracking your progress to see analytics!")
        
        except Exception as e:
            logger.error(f"Error in analytics tab: {e}")
            st.error("An error occurred while loading analytics. Please try again.")

if __name__ == "__main__":
    try:
        app = FitAI()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please refresh the page.")