from transformers import pipeline
from PIL import Image
import torch

class ImageAnalyzer:
    def __init__(self):
        # Initialize the image-to-text pipeline
        self.image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")
    
    def analyze_image(self, image_path):
        """
        Analyze an image and return a detailed description.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Detailed description of the image
        """
        try:
            # Load and process the image
            image = Image.open(image_path)
            
            # Generate caption
            result = self.image_to_text(image)
            
            # Extract and enhance the description
            description = result[0]['generated_text']
            
            # Add more context and detail to the description
            enhanced_description = f"In this image, {description.lower()}"
            
            return enhanced_description
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"