import streamlit as st
import threading
from summary import summarize_text, create_txt_file, create_pdf_file, text_to_speech, get_summary_stats

# Configure the page
st.set_page_config(page_title="Summary - EduPal", page_icon="📄", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { 
        background-color: #f8f9fa; 
        padding: 2rem;
    }
    .title { 
        text-align: center; 
        color: #2c3e50; 
        margin-bottom: 1rem;
    }
    .subtitle { 
        text-align: center; 
        color: #7f8c8d; 
        font-size: 18px; 
        margin-bottom: 2rem;
    }
    .summary-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-left: 4px solid #4a90e2;
    }
    .stButton>button {
        min-width: 150px;
        padding: 12px 20px;
        font-size: 16px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin: 5px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("<h1 class='title'>📄 Lecture Summary</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>AI-generated summary of your PDF lecture</p>", unsafe_allow_html=True)
    
    # Check if we have text from the uploaded file
    if 'uploaded_text' not in st.session_state:
        st.error("❌ No text found! Please go back to the home page and upload a PDF first.")
        if st.button("🏠 Go to Home"):
            st.switch_page("home.py")
        return
    
    # Get the uploaded text and filename
    text = st.session_state.uploaded_text
    filename = st.session_state.get('uploaded_filename', 'document.pdf')
    
    st.success(f"📄 Processing summary for: {filename}")
    
    # Generate or get cached summary
    if 'summary_text' not in st.session_state:
        with st.spinner("🤖 Generating summary with AI..."):
            try:
                summary = summarize_text(text)
                st.session_state.summary_text = summary
            except Exception as e:
                st.error(f"❌ Failed to generate summary: {str(e)}")
                return
    
    summary_text = st.session_state.summary_text
    
    # Display the summary
    st.markdown("### 📋 Summary")
    with st.container():
        st.markdown(f"""
        <div class="summary-container">
        {summary_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("### 🎯 Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Save as TXT
        try:
            txt_data = create_txt_file(summary_text)
            st.download_button(
                label="💾 Save as TXT",
                data=txt_data,
                file_name=f"{filename.replace('.pdf', '')}_summary.txt",
                mime="text/plain",
                key="download_txt"
            )
        except Exception as e:
            st.error(f"❌ Error creating TXT: {str(e)}")
    
    with col2:
        # Save as PDF
        try:
            pdf_data = create_pdf_file(summary_text)
            st.download_button(
                label="📄 Save as PDF",
                data=pdf_data,
                file_name=f"{filename.replace('.pdf', '')}_summary.pdf",
                mime="application/pdf",
                key="download_pdf"
            )
        except Exception as e:
            st.error(f"❌ Error creating PDF: {str(e)}")
    
    with col3:
        # Listen to Summary
        if st.button("🔊 Listen to Summary"):
            with st.spinner("🎧 Converting to speech..."):
                def speak_summary():
                    try:
                        text_to_speech(summary_text)
                        st.success("✅ Finished reading summary!")
                    except Exception as e:
                        st.error(f"❌ Could not convert to speech: {str(e)}")
                
                # Start speaking in a separate thread
                speech_thread = threading.Thread(target=speak_summary)
                speech_thread.daemon = True
                speech_thread.start()
                st.info("🎙️ Starting to read summary... (This may take a moment to start)")
    
    with col4:
        # Go to Home
        if st.button("🏠 Go to Home"):
            # Clear the summary from session state if user wants to start over
            if 'summary_text' in st.session_state:
                del st.session_state.summary_text
            st.switch_page("home.py")
    
    # Additional information
    st.markdown("---")
    st.markdown("### 📊 Summary Statistics")
    
    try:
        stats = get_summary_stats(summary_text, text)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📝 Summary Words", stats['summary_words'])
        
        with col2:
            st.metric("📉 Compression", f"{stats['compression_ratio']}%")
        
        with col3:
            st.metric("⏱️ Reading Time", f"{stats['reading_time']} min")
            
    except Exception as e:
        st.error(f"❌ Error calculating statistics: {str(e)}")

if __name__ == "__main__":
    main()