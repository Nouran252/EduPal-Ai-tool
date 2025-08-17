import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import pyttsx3
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import re

# Direct configuration
genai.configure(api_key="AIzaSyB0fLJ8Kg8z-x26w3X5kktITUa_NyQeEZM")

# Read PDF
def read_pdf(file_path):
    """Extract text from PDF file"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Summary function
def summarize_text(text):
    """Generate summary using Gemini API"""
    prompt = f"""
    You are a helpful assistant that summarizes text in clean, organized **Markdown** format.
    
    Summarize the lecture content with:
    - A main title
    - Subheadings for each topic
    - Bullet points for key details
    - Blank lines between sections
    Keep it concise but clear.
    
    {text}
    """
    try:
        # Pass API key directly
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

# File handling functions
def create_txt_file(summary_text):
    """Create TXT file content from summary"""
    # Remove markdown formatting for plain text
    plain_text = summary_text.replace("**", "").replace("##", "").replace("#", "")
    return plain_text.encode('utf-8')

def create_pdf_file(summary_text):
    """Create PDF file content from summary"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Clean the text for PDF (remove markdown)
        clean_text = summary_text.replace("**", "").replace("##", "").replace("#", "")
        
        # Split text into lines and add to PDF
        lines = clean_text.split('\n')
        for line in lines:
            if line.strip():  # Skip empty lines
                # Handle long lines by wrapping them
                if len(line) > 80:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 80:
                            current_line += word + " "
                        else:
                            pdf.cell(0, 10, txt=current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                            current_line = word + " "
                    if current_line:
                        pdf.cell(0, 10, txt=current_line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                else:
                    pdf.cell(0, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
            else:
                pdf.ln(5)  # Add space for empty lines
        
        return bytes(pdf.output(dest="S"))
    except Exception as e:
        raise Exception(f"Error creating PDF: {str(e)}")

def text_to_speech(text, filename="speech_output.wav"):
    """Convert text to speech using pyttsx3"""
    try:
        # Initialize the TTS engine
        engine = pyttsx3.init()
        
        voices=engine.getProperty('voices')

        # Set properties
        engine.setProperty('voice',voices[0].id)
        engine.setProperty('rate', 150)    # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Clean text for speech (remove markdown)
        clean_text = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)
        
        # Speak the text
        engine.say(clean_text)
        engine.save_to_file(clean_text, filename)
        engine.runAndWait()
        print(f"Audio saved as '{filename}'")
        return filename
    except Exception as e:
        raise Exception(f"Error with text-to-speech: {str(e)}")

# Utility functions
def get_summary_stats(summary_text, original_text):
    """Calculate summary statistics"""
    summary_words = len(summary_text.split())
    original_words = len(original_text.split())
    
    compression_ratio = round((1 - summary_words/original_words) * 100, 1) if original_words > 0 else 0
    reading_time = max(1, round(summary_words / 200))  # Average reading speed: 200 words/minute
    
    return {
        'summary_words': summary_words,
        'original_words': original_words,
        'compression_ratio': compression_ratio,
        'reading_time': reading_time
    }