import streamlit as st

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

# Title & description
st.markdown("<h1 class='title'>📚 EduPal</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your AI-powered study companion</p>", unsafe_allow_html=True)
st.markdown("---")

# Upload file
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

# Action buttons
if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    st.markdown("### What would you like to do?")

     # Create 3 equally spaced columns for horizontal buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Summarize"):
            st.info("Summarization will be here...")
    with col2:
        if st.button("❓ Q&A Chat"):
            st.info("Q&A Chat interface will be here...")
    with col3:
        if st.button("🧠 Quiz"):
            st.info("Quiz generation will be here...")
else:
    st.warning("📂 Please upload a PDF to continue.")
