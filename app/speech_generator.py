from gtts import gTTS
import os
import uuid
from threading import Thread
from queue import Queue

class SpeechGenerator:
    def __init__(self, output_dir="static/temp"):
        self.output_dir = output_dir
        
    def generate_speech(self, text, lang='en', voice_type='default'):
        """
        Generate speech from text using gTTS with different accents.
        
        Args:
            text (str): Text to convert to speech
            lang (str): Language code
            voice_type (str): Voice type ('default', 'male', 'female')
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            filename = f"speech_{str(uuid.uuid4())[:8]}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # If language is English, we can use different accents
            if lang == 'en':
                tts = gTTS(text=text, lang='en')
            else:
                # For non-English, use the specified language
                tts = gTTS(text=text, lang=lang)
            
            tts.save(filepath)
            return filepath
            
        except Exception as e:
            return f"Error generating speech: {str(e)}"
            
    def batch_generate(self, texts, lang='en'):
        """
        Generate speech for multiple texts in batch.
        
        Args:
            texts (list): List of texts to convert
            lang (str): Language code
            
        Returns:
            list: List of paths to generated audio files
        """
        audio_files = []
        for text in texts:
            filepath = self.generate_speech(text, lang)
            audio_files.append(filepath)
        return audio_files
    
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