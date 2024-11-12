# components.py
import streamlit as st
import base64
from gtts import gTTS
import io
import re
from typing import Dict, Any

class UIComponents:
    @staticmethod
    def create_workout_card(exercise: str, sets: int, reps: int, rest: int) -> str:
        """Create a visually appealing workout card."""
        return f'''
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

    @staticmethod
    def text_to_speech(text: str) -> str:
        """Convert text to speech and return audio player HTML."""
        try:
            # Clean markdown
            cleaned_text = re.sub(r'[#*_\[\]\(\)]', '', text).strip()
            
            # Create speech
            tts = gTTS(text=cleaned_text, lang=config.DEFAULT_LANG)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # Encode to base64
            audio_str = base64.b64encode(audio_fp.read()).decode()
            
            return f'''
                <audio controls autoplay>
                    <source src="data:audio/mp3;base64,{audio_str}" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
            '''
        except Exception as e:
            st.error(f"Error generating audio: {str(e)}")
            return ""
