import streamlit as st
import json
import time
from quiz_gen import quiz_gen  # Import your quiz generation function

# Page settings
st.set_page_config(page_title="EduPal - Quiz", page_icon="🧠", layout="centered")

# Custom CSS for quiz interface
st.markdown("""
    <style>
    .main { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .quiz-container {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .quiz-title { 
        text-align: center; 
        color: #2c3e50; 
        font-size: 2.5rem;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    .quiz-subtitle { 
        text-align: center; 
        color: #7f8c8d; 
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    .question-card {
        background: #f8f9fa;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #4a90e2;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .question-number {
        color: #4a90e2;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    
    .question-text {
        color: #2c3e50;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 15px;
        line-height: 1.5;
    }
    
    /* Fixed radio button styling */
    .stRadio > div {
        background: white;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    
    .stRadio > div > label {
        display: flex !important;
        align-items: center !important;
        background: #ffffff !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        margin: 6px 0 !important;
        border: 2px solid #e1e8ed !important;
        cursor: pointer !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stRadio > div > label:hover {
        background: #f8f9fa !important;
        border-color: #4a90e2 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.1) !important;
    }
    
    .stRadio > div > label > div {
        color: #2c3e50 !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
        margin-left: 10px !important;
    }
    
    /* Selected radio button */
    .stRadio > div > label[data-checked="true"] {
        background: #e3f2fd !important;
        border-color: #4a90e2 !important;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2) !important;
    }
    
    .stRadio > div > label[data-checked="true"] > div {
        color: #1976d2 !important;
        font-weight: 600 !important;
    }
    
    .stButton>button {
        width: 100%;
        padding: 15px 30px;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 50px;
        background: linear-gradient(45deg, #4a90e2, #357ABD);
        color: white;
        border: none;
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.3);
        transition: all 0.3s ease;
        margin-top: 30px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(74, 144, 226, 0.4);
    }
    
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .score-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .score-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .correct-answer {
        background: #d4edda;
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .wrong-answer {
        background: #f8d7da;
        border: 2px solid #dc3545;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .answer-explanation {
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .progress-bar {
        background: #e9ecef;
        border-radius: 50px;
        height: 10px;
        margin: 20px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #28a745, #20c997);
        border-radius: 50px;
        transition: width 0.5s ease;
    }
    
    .back-button {
        background: linear-gradient(45deg, #6c757d, #495057) !important;
        margin-bottom: 20px !important;
        width: auto !important;
        padding: 10px 20px !important;
        font-size: 1rem !important;
    }
    
    .back-button:hover {
        background: linear-gradient(45deg, #495057, #343a40) !important;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_quiz_state():
    """Initialize quiz-specific session state variables"""
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = []
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False

def check_required_data():
    """Check if required data from home page exists"""
    if 'uploaded_text' not in st.session_state or 'uploaded_filename' not in st.session_state:
        st.error("❌ No document data found. Please go back to home page and upload a PDF first.")
        if st.button("🏠 Go to Home Page"):
            st.switch_page("home.py")
        st.stop()

def generate_quiz_loading():
    """Display loading screen while generating quiz"""
    st.markdown("""
        <div class="quiz-container">
            <h1 class="quiz-title">🧠 Generating Your Quiz</h1>
            <p class="quiz-subtitle">AI is analyzing your document and creating personalized questions...</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar animation
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate progress while generating quiz
    for i in range(1, 101):
        progress_bar.progress(i)
        if i < 30:
            status_text.text("📖 Analyzing document content...")
        elif i < 60:
            status_text.text("🤖 AI is creating questions...")
        elif i < 90:
            status_text.text("🔍 Reviewing question quality...")
        else:
            status_text.text("✅ Almost ready!")
        time.sleep(0.02)  # Small delay for visual effect
    
    # Generate quiz
    try:
        with st.spinner("Finalizing your quiz..."):
            quiz_data = quiz_gen(st.session_state.uploaded_text)
        
        if quiz_data and len(quiz_data) > 0:
            st.session_state.quiz_data = quiz_data
            st.session_state.quiz_generated = True
            st.success(f"✅ Quiz generated successfully with {len(quiz_data)} questions!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Failed to generate quiz. Please try again.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again"):
                    st.rerun()
            with col2:
                if st.button("🏠 Back to Home"):
                    st.switch_page("home.py")
            
    except Exception as e:
        st.error(f"❌ Error generating quiz: {str(e)}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Try Again"):
                st.rerun()
        with col2:
            if st.button("🏠 Back to Home"):
                st.switch_page("home.py")

def display_quiz_questions():
    """Display quiz questions and handle user input"""
    quiz_data = st.session_state.quiz_data
    
    # Back button
    if st.button("🔙 Back to Home", key="back_btn", help="Return to home page"):
        st.switch_page("home.py")
    
    # Quiz header
    st.markdown(f"""
        <div class="quiz-container">
            <h1 class="quiz-title">🧠 Knowledge Quiz</h1>
            <p class="quiz-subtitle">Test your understanding of: {st.session_state.uploaded_filename}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display all questions
    st.markdown("### 📝 Answer all questions below:")
    
    for i, question in enumerate(quiz_data):
        with st.container():
            st.markdown(f"""
                <div class="question-card">
                    <div class="question-number">Question {i+1} of {len(quiz_data)}</div>
                    <div class="question-text">{question['question']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Radio button for options with improved visibility
            answer = st.radio(
                f"**Select your answer for Question {i+1}:**",
                options=question['options'],
                key=f"question_{i}",
                index=None,  # No default selection
                help=f"Choose the best answer for question {i+1}"
            )
            
            # Store user answer
            if answer:
                # Extract just the letter (A, B, C, D) from the selected option
                selected_letter = answer[0]  # Gets 'A', 'B', 'C', or 'D'
                st.session_state.user_answers[i] = selected_letter
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Submit Quiz"):
            if len(st.session_state.user_answers) == len(quiz_data):
                st.session_state.quiz_submitted = True
                st.rerun()
            else:
                st.error("⚠️ Please answer all questions before submitting!")
                st.info(f"Answered: {len(st.session_state.user_answers)}/{len(quiz_data)} questions")

def display_quiz_results():
    """Display quiz results with score and corrections"""
    quiz_data = st.session_state.quiz_data
    
    # Back button
    if st.button("🔙 Back to Home", key="back_btn_results", help="Return to home page"):
        # Reset quiz state
        st.session_state.quiz_submitted = False
        st.session_state.user_answers = {}
        st.session_state.quiz_generated = False
        st.session_state.quiz_data = []
        st.switch_page("home.py")
    
    # Calculate score
    correct_count = 0
    total_questions = len(quiz_data)
    
    for i, question in enumerate(quiz_data):
        user_answer = st.session_state.user_answers.get(i, '')
        correct_answer = question['correct']
        if user_answer == correct_answer:
            correct_count += 1
    
    # Score percentage
    score_percentage = (correct_count / total_questions) * 100
    
    # Display score card
    st.markdown(f"""
        <div class="score-card">
            <div class="score-title">🎉 Quiz Complete!</div>
            <div class="score-subtitle">Your Score: {correct_count}/{total_questions} ({score_percentage:.1f}%)</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {score_percentage}%"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Performance message
    if score_percentage >= 80:
        st.success("🌟 Excellent work! You have a strong understanding of the material!")
    elif score_percentage >= 60:
        st.info("👍 Good job! Review the incorrect answers to improve your understanding.")
    else:
        st.warning("📚 Keep studying! Review the material and try again.")
    
    # Show detailed results
    st.markdown("### 📊 Detailed Results:")
    
    for i, question in enumerate(quiz_data):
        user_answer = st.session_state.user_answers.get(i, '')
        correct_answer = question['correct']
        is_correct = user_answer == correct_answer
        
        # Find the correct option text
        correct_option_text = ""
        user_option_text = ""
        for option in question['options']:
            if option.startswith(correct_answer + ")"):
                correct_option_text = option
            if option.startswith(user_answer + ")"):
                user_option_text = option
        
        if is_correct:
            st.markdown(f"""
                <div class="correct-answer">
                    <div class="answer-explanation">✅ Question {i+1}: Correct!</div>
                    <strong>Q:</strong> {question['question']}<br>
                    <strong>Your Answer:</strong> {user_option_text}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="wrong-answer">
                    <div class="answer-explanation">❌ Question {i+1}: Incorrect</div>
                    <strong>Q:</strong> {question['question']}<br>
                    <strong>Your Answer:</strong> {user_option_text}<br>
                    <strong>Correct Answer:</strong> {correct_option_text}
                </div>
            """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Retake Quiz"):
            # Reset quiz answers but keep quiz data
            st.session_state.quiz_submitted = False
            st.session_state.user_answers = {}
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Home"):
            # Reset everything and go home
            st.session_state.quiz_submitted = False
            st.session_state.user_answers = {}
            st.session_state.quiz_generated = False
            st.session_state.quiz_data = []
            st.switch_page("home.py")
    
    with col3:
        if st.button("📊 New Quiz"):
            # Generate new quiz from same document
            st.session_state.quiz_submitted = False
            st.session_state.user_answers = {}
            st.session_state.quiz_generated = False
            st.session_state.quiz_data = []
            st.rerun()

def main():
    """Main quiz page function"""
    # Initialize quiz state
    initialize_quiz_state()
    
    # Check if required data exists
    check_required_data()
    
    # Route to appropriate quiz stage
    if not st.session_state.quiz_generated:
        generate_quiz_loading()
    elif not st.session_state.quiz_submitted:
        display_quiz_questions()
    else:
        display_quiz_results()

if __name__ == "__main__":
    main()