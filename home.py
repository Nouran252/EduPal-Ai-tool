import streamlit as st
import pdfplumber

# Page settings
st.set_page_config(page_title="EduPal", page_icon="📚", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .title { text-align: center; color: #2c3e50; }
    .subtitle { text-align: center; color: #7f8c8d; font-size: 18px; }

    .stButton>button {
        min-width: 150px;
        padding: 12px 20px;
        font-size: 16px;
        border-radius: 12px;
        background-color: #4a90e2;
        color: white;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)



def extract_pdf_text(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text.strip()
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {str(e)}")
        return ""

def main():
    # Title & description
    st.markdown("<h1 class='title'>📚 EduPal</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your AI-powered study companion</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Upload file
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    # Action buttons
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Extract the text from the PDF
        text = extract_pdf_text(uploaded_file)
        
        if text:
            # Store data in session state for other pages to access
            st.session_state.uploaded_text = text
            st.session_state.uploaded_filename = uploaded_file.name
            
            st.info(f"📄 Text extracted successfully! ({len(text.split())} words)")
            st.markdown("### What would you like to do?")
            
            # Create 3 equally spaced columns for horizontal buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📝 Summarize"):
                   st.switch_page("pages/summarizer_interface.py")
            
            with col2:
                if st.button("❓ Q&A Chat"):
                    st.info("Q&A Chat interface will be here...")
            
            with col3:
                if st.button("🧠 Quiz"):
                    # Navigate to quiz page
                    st.switch_page("pages/quiz_interface.py")
        else:
            st.error("❌ Could not extract text from the PDF. Please try a different file.")
    else:
        st.warning("📂 Please upload a PDF to continue.")

if __name__ == "__main__":
    main()