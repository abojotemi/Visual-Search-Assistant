import torch
import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import streamlit as st
from utils import validate_image

@st.cache_resource
def load_blip_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base", torch_dtype=torch.float16).to(device)
    return processor, model

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def predict_image(img):
    processor, model = load_blip_model()
    try:
        
        if validate_image(img):
            raw_image = Image.open(img).convert('RGB')
        else:
            raise ValueError("Invalid image File")
        text = "a photography of"
        inputs = processor(raw_image, text, return_tensors="pt").to(device, torch.float16)

        out = model.generate(**inputs)
        print(processor.decode(out[0], skip_special_tokens=True))
        inputs = processor(raw_image, return_tensors="pt").to(device, torch.float16)

        out = model.generate(**inputs)
        return (processor.decode(out[0], skip_special_tokens=True))
    except ValueError as e:
     return (f"Error: {str(e)}")
    
