import streamlit as st
import fitz
import os
from dotenv import load_dotenv
from rag.retriever import get_relevant_docs
from rag.chat import ask_groq

load_dotenv()

st.set_page_config(page_title="Chat with Document", layout="centered")

st.title("📄 Chat with your Document")

uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    text = ""

    if uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8", errors="ignore")

    elif uploaded_file.name.endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()

    if len(text.strip()) == 0:
        st.error("No readable text found.")
    else:
        with open("data/document.txt", "w", encoding="utf-8") as f:
            f.write(text)

        st.success("Document uploaded successfully!")

question = st.text_input("Ask a question")

if question:
    docs = get_relevant_docs(question, k=2)
    context = "\n".join(docs)
    answer = ask_groq(context, question)
    st.markdown("### 💡 Answer")
    st.write(answer)