# Visual Search Assistant 🔍 🖼️

A multimodal AI application that combines image analysis with speech synthesis to provide audio descriptions of uploaded images. Perfect for accessibility and learning applications!

## Features

- 📷 Upload images in common formats (PNG, JPG, JPEG)
- 🤖 AI-powered image analysis using state-of-the-art computer vision
- 🗣️ Text-to-speech conversion for audio descriptions
- 🌐 User-friendly web interface built with Streamlit
- ♿ Accessibility-focused design

## Demo Video

[Add your demo video link here]

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd visual-search-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app/main.py
```

2. Open your web browser and go to `http://localhost:8501`

3. Upload an image using the file uploader

4. Click "Analyze Image" to process the image and generate audio description

## Technical Details

### Architecture

The application consists of three main components:

1. **Image Analyzer**: Uses the BLIP model from Salesforce for image captioning
2. **Speech Generator**: Utilizes gTTS (Google Text-to-Speech) for audio generation
3. **Web Interface**: Built with Streamlit for easy interaction

### Workflow

1. User uploads an image through the Streamlit interface
2. Image is validated and temporarily stored
3. Image Analyzer processes the image and generates a detailed description
4. Speech Generator converts the description to audio
5. Results are displayed with both text and audio options

## Performance Optimizations

- Efficient file handling with automatic cleanup of temporary files
- Optimized image processing pipeline
- Streamlined audio generation process
- Minimal memory footprint with temporary file management

## Future Improvements

- Support for multiple languages
- Batch processing capabilities
- More detailed image analysis with object detection
- Custom voice options for speech synthesis
- Integration with screen readers

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your chosen license here]

## Acknowledgments

- Salesforce for the BLIP image captioning model
- Google Text-to-Speech for audio synthesis
- Streamlit for the wonderful web framework