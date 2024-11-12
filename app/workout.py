# workout.py
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import streamlit as st
from utils import validate_image
from typing import Optional

class WorkoutImageAnalyzer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None

    @st.cache_resource
    def load_model(_self):
        """Load BLIP model with caching."""
        if _self.processor is None or _self.model is None:
            try:
                _self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                _self.model = BlipForConditionalGeneration.from_pretrained(
                    "Salesforce/blip-image-captioning-base",
                    torch_dtype=torch.float16
                ).to(_self.device)
            except Exception as e:
                st.error(f"Error loading model: {str(e)}")
                return None, None
        return _self.processor, _self.model

    @st.cache_data
    def predict_image(self, img) -> Optional[str]:
        """Analyze workout equipment image."""
        processor, model = self.load_model()
        if processor is None or model is None:
            return None

        try:
            if not validate_image(img):
                raise ValueError("Invalid image file")

            raw_image = Image.open(img).convert('RGB')
            
            # First pass with context
            inputs = processor(raw_image, "a photography of", return_tensors="pt").to(self.device, torch.float16)
            out = model.generate(**inputs)
            
            # Second pass without context for validation
            inputs = processor(raw_image, return_tensors="pt").to(self.device, torch.float16)
            out = model.generate(**inputs)
            
            return processor.decode(out[0], skip_special_tokens=True)
            
        except Exception as e:
            st.error(f"Error analyzing image: {str(e)}")
            return None