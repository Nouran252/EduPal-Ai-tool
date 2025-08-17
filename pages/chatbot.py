import PyPDF2
from PyPDF2 import PdfReader
import google.generativeai as genai
from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
import streamlit as st

st.title("Edupal")
st.header("Ask any question and our Edupal chatbot will help")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is None:
    st.info("Please upload a PDF file to continue")
    st.stop()


if 'pdf_processed' not in st.session_state:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    extracted_text = ""

    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=200,
        chunk_overlap=0,
        length_function=len,
    )
    chunks = text_splitter.split_text(extracted_text)
    full_text = "\n\n".join(chunks)
    # embeddings = HuggingFaceEmbeddings(
    #     model_name="sentence-transformers/all-MiniLM-L6-v2"
    # )
    # vector_store = FAISS.from_texts(chunks, embeddings)

    # Cache the results
    st.session_state.chunks = chunks
    st.session_state.full_text = full_text
    # st.session_state.embeddings = embeddings
    # st.session_state.vector_store = vector_store
    st.session_state.pdf_processed = True
else:
    # Use cached results
    chunks = st.session_state.chunks
    full_text = st.session_state.full_text
    # embeddings = st.session_state.embeddings
    # vector_store = st.session_state.vector_store

genai.configure(api_key="AIzaSyA76C3lU1hNsbdlN9xgFikgcxnJAqH4wOQ")
model = genai.GenerativeModel("gemini-2.0-flash-lite")

user_question = st.text_area("Ask here: ", key="user_input")

# --- FIX: keep chat history in session ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Send"):
    st.write("You: " + user_question)

    user_input = user_question
    st.session_state.chat_history.append(f"User: {user_input}")

    conversation_history = "\n".join(st.session_state.chat_history[-10:])

    response = model.generate_content(
        f"""You are Edupal, a helpful assistant.

Conversation so far:
{conversation_history}

The user has uploaded this text:
{full_text[:2000]}  

Now answer the latest question clearly and concisely.

User: {user_input}
Edupal:
        """,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 500
        }
    )

    st.session_state.chat_history.append(f"Edupal: {response.text}")

    print(conversation_history)
    st.write("Edupal:", response.text)
