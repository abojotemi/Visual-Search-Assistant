from gtts import gTTS
import os
import uuid

class SpeechGenerator:
    def __init__(self, output_dir="static/temp"):
        self.output_dir = output_dir
        
    def generate_speech(self, text, lang='en'):
        """
        Generate speech from text and save it as an audio file.
        
        Args:
            text (str): Text to convert to speech
            lang (str): Language code (default: 'en')
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            # Generate unique filename
            filename = f"speech_{str(uuid.uuid4())[:8]}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate speech
            tts = gTTS(text=text, lang=lang)
            tts.save(filepath)
            
            return filepath
            
        except Exception as e:
            return f"Error generating speech: {str(e)}"
            
    def cleanup_old_files(self):
        """Clean up old audio files to prevent storage buildup"""
        try:
            for file in os.listdir(self.output_dir):
                if file.startswith("speech_") and file.endswith(".mp3"):
                    file_path = os.path.join(self.output_dir, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up files: {str(e)}")