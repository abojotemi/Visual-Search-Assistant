import os
from PIL import Image
import uuid

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to a temporary directory.
    
    Args:
        uploaded_file: StreamLit uploaded file object
        
    Returns:
        str: Path to the saved file
    """
    try:
        # Create temp dir if it doesn't exist
        temp_dir = "static/temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        filename = f"upload_{str(uuid.uuid4())[:8]}{file_extension}"
        filepath = os.path.join(temp_dir, filename)
        
        # Save the file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return filepath
    except Exception as e:
        return None

def validate_image(file):
    """
    Validate that the uploaded file is an image.
    
    Args:
        file: StreamLit uploaded file object
        
    Returns:
        bool: True if valid image, False otherwise
    """
    try:
        Image.open(file)
        return True
    except:
        return False

def cleanup_old_files(directory="static/temp"):
    """Clean up old files except .gitkeep"""
    try:
        for file in os.listdir(directory):
            if file != ".gitkeep":
                file_path = os.path.join(directory, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up files: {str(e)}")
