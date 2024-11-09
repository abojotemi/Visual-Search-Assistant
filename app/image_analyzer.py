from transformers import pipeline
from PIL import Image
import torch
from deep_translator import GoogleTranslator


class ImageAnalyzer:
    def __init__(self):
        # Initialize the image-to-text pipeline
        self.image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")
        # Initialize object detection pipeline
        self.object_detector = pipeline("object-detection", model="facebook/detr-resnet-50")
        # Initialize translator
        
        
    def analyze_image(self, image_path, target_lang='en'):
        """
        Analyze an image and return a detailed description with object detection.
        
        Args:
            image_path (str): Path to the image file
            target_lang (str): Target language code (default: 'en')
            
        Returns:
            dict: Detailed analysis including description and detected objects
        """
        try:
            # Load and process the image
            image = Image.open(image_path)
            
            # Generate caption
            caption_result = self.image_to_text(image)
            description = caption_result[0]['generated_text']
            
            # Detect objects
            objects_result = self.object_detector(image)
            
            # Process detected objects
            detected_objects = {}
            for obj in objects_result:
                label = obj['label']
                confidence = round(obj['score'] * 100, 2)
                if label in detected_objects:
                    if confidence > detected_objects[label]['confidence']:
                        detected_objects[label] = {'count': detected_objects[label]['count'] + 1, 
                                                 'confidence': confidence}
                else:
                    detected_objects[label] = {'count': 1, 'confidence': confidence}
            
            # # Create detailed description
            # object_description = ", ".join([f"{vals['count']} {label} ({vals['confidence']}% confidence)" 
            #                              for label, vals 
            #                              in detected_objects.items()])
            
            enhanced_description = f"In this image, {description.lower()}"
            
            # Translate if needed
            if target_lang != 'en':
                
                enhanced_description = GoogleTranslator(source='auto', target=target_lang).translate(
                    enhanced_description)

            return {
                'description': enhanced_description,
                'objects': detected_objects,
                'language': target_lang
            }
            
        except Exception as e:
            return {'error': f"Error analyzing image: {str(e)}"}
            
    def batch_analyze(self, image_paths, target_lang='en'):
        """
        Analyze multiple images in batch.
        
        Args:
            image_paths (list): List of paths to image files
            target_lang (str): Target language code
            
        Returns:
            list: List of analysis results for each image
        """
        return [self.analyze_image(path, target_lang) for path in image_paths]