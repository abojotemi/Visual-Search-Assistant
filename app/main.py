import streamlit as st
import os
from image_analyzer import ImageAnalyzer
from speech_generator import SpeechGenerator
from utils import save_uploaded_file, validate_image, cleanup_old_files
import glob

def main():
    st.set_page_config(
        page_title="Enhanced Visual Search Assistant",
        page_icon="🔍",
        layout="wide"
    )
    
    # Initialize components
    image_analyzer = ImageAnalyzer()
    speech_generator = SpeechGenerator()
    
    # App header
    st.title("🔍 Enhanced Visual Search Assistant")
    st.write("Upload images and I'll describe what I see in multiple languages!")
    
    # Sidebar settings
    st.sidebar.title("Settings")
    
    # Language selection
    languages = {
        'English': 'en', 'Spanish': 'es', 'French': 'fr', 
        'German': 'de', 'Italian': 'it', 'Japanese': 'ja',
        'Korean': 'ko', 'Chinese': 'zh-CN', 'Russian': 'ru'
    }
    target_lang = st.sidebar.selectbox(
        "Select Output Language",
        options=list(languages.keys())
    )

    # Screen reader mode
    screen_reader_mode = st.sidebar.checkbox("Screen Reader Mode")
    
    # Batch processing mode
    batch_mode = st.sidebar.checkbox("Batch Processing Mode")
    
    if batch_mode:
        uploaded_files = st.file_uploader(
            "Choose multiple images...", 
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            # Display uploaded images in a grid
            cols = st.columns(3)
            for idx, uploaded_file in enumerate(uploaded_files):
                if validate_image(uploaded_file):
                    cols[idx % 3].image(uploaded_file, caption=f"Image {idx+1}")
                    
            if st.button("Analyze All Images"):
                with st.spinner("Processing images..."):
                    # Clean up old files
                    cleanup_old_files()
                    
                    # Process each image
                    for idx, uploaded_file in enumerate(uploaded_files):
                        if validate_image(uploaded_file):
                            image_path = save_uploaded_file(uploaded_file)
                            
                            if image_path:
                                # Analyze image
                                result = image_analyzer.analyze_image(
                                    image_path, 
                                    target_lang=languages[target_lang]
                                )
                                
                                # Display results
                                st.write(f"### Image {idx+1} Analysis:")
                                st.write(result['description'])
                                
                                # Display detected objects
                                if 'objects' in result:
                                    st.write("#### Detected Objects:")
                                    for obj, details in result['objects'].items():
                                        st.write(f"- {obj}: {details['count']} instances ({details['confidence']}% confidence)")
                                
                                # Generate speech
                                audio_path = speech_generator.generate_speech(
                                    result['description'],
                                    lang=languages[target_lang],
                                    
                                )
                                
                                # Display audio player
                                if not audio_path.startswith("Error"):
                                    st.write("#### Audio Description:")
                                    st.audio(audio_path)
                                    
                                    # Screen reader support
                                    if screen_reader_mode:
                                        st.markdown(f"""
                                            <div class="sr-only" role="alert" aria-live="polite">
                                                {result['description']}
                                            </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.error("Error generating audio description")
                                    
    else:
        # Single image mode
        uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            if validate_image(uploaded_file):
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
                
                if st.button("Analyze Image"):
                    with st.spinner("Processing image..."):
                        # Clean up old files
                        cleanup_old_files()
                        
                        # Save and process image
                        image_path = save_uploaded_file(uploaded_file)
                        
                        if image_path:
                            # Analyze image
                            result = image_analyzer.analyze_image(
                                image_path, 
                                target_lang=languages[target_lang]
                            )
                            
                            # Display results
                            st.write("### Description:")
                            print(result)
                            st.write(result['description'])
                            
                            # Display detected objects
                            if 'objects' in result:
                                st.write("### Detected Objects:")
                                for obj, details in result['objects'].items():
                                    st.write(f"- {obj}: {details['count']} instances ({details['confidence']}% confidence)")
                            
                            # Generate speech
                            audio_path = speech_generator.generate_speech(
                                result['description'],
                                lang=languages[target_lang],
                                
                            )
                            
                            # Display audio player
                            if not audio_path.startswith("Error"):
                                st.write("### Audio Description:")
                                st.audio(audio_path)
                                
                                # Screen reader support
                                if screen_reader_mode:
                                    st.markdown(f"""
                                        <div class="sr-only" role="alert" aria-live="polite">
                                            {result['description']}
                                        </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.error("Error generating audio description")
                        else:
                            st.error("Error saving uploaded file")
            else:
                st.error("Please upload a valid image file!")

if __name__ == "__main__":
    main()