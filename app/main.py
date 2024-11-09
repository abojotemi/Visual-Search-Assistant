import streamlit as st
import os
from image_analyzer import ImageAnalyzer
from speech_generator import SpeechGenerator
from utils import save_uploaded_file, validate_image, cleanup_old_files

def main():
    st.set_page_config(
        page_title="Visual Search Assistant",
        page_icon="🔍",
        layout="wide"
    )
    
    # Initialize components
    image_analyzer = ImageAnalyzer()
    speech_generator = SpeechGenerator()
    
    # App header
    st.title("🔍 Visual Search Assistant")
    st.write("Upload an image and I'll describe what I see!")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # Validate image
        if not validate_image(uploaded_file):
            st.error("Please upload a valid image file!")
            return
            
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        # Process button
        if st.button("Analyze Image"):
            with st.spinner("Processing image..."):
                # Clean up old files
                cleanup_old_files()
                
                # Save uploaded file
                image_path = save_uploaded_file(uploaded_file)
                
                if image_path:
                    # Analyze image
                    description = image_analyzer.analyze_image(image_path)
                    
                    # Display description
                    st.write("### Description:")
                    st.write(description)
                    
                    # Generate speech
                    audio_path = speech_generator.generate_speech(description)
                    
                    # Display audio player
                    if not audio_path.startswith("Error"):
                        st.write("### Audio Description:")
                        st.audio(audio_path)
                    else:
                        st.error("Error generating audio description")
                else:
                    st.error("Error saving uploaded file")

if __name__ == "__main__":
    main()