import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="EduPal", page_icon="📚", layout="centered")
confused_sign = "false";
if "uploaded_text" not in st.session_state or not st.session_state.uploaded_text:
    st.error("❌ No document data found. Please go back to home page and upload a PDF first.")
    if st.button("🏠 Go to Home Page"):
        st.switch_page("home.py")
    st.stop()  # stop execution to avoid crash

full_text = st.session_state.uploaded_text
st.subheader("Ask any question and our Edupal chatbot will help")
genai.configure(api_key="AIzaSyA76C3lU1hNsbdlN9xgFikgcxnJAqH4wOQ")
model = genai.GenerativeModel("gemini-2.0-flash-lite")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_question := st.chat_input("Ask here..."):
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.write(user_question)

        response = model.generate_content(
            f"""You are Edupal, a helpful assistant.

        Conversation so far:
        {st.session_state.messages}

        The user has uploaded this text:
        {full_text[:2000]}

        Now answer the latest question clearly and concisely.

        User: {user_question}

            if the user asked a question about the uploaded text make your response format like:
           - your response to users questions and explanations.
           - examples and more details.
           - summary to all your response main points.

       provide 3 external learning resources (articles, websites, or videos), only  if user asked for resources, 
       Format it like:
           - Suggested Resources: 
          1. short Title -short link
          2. short Title -short link
          3. short Title -short link

        Edupal:
                """,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 500
            }

        )

        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.write(response.text)