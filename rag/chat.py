import requests
import os
from rag.retriever import get_relevant_docs
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROK_API_KEY")  # name can stay as-is

def ask_groq(context, question):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {
                "role": "system",
                "content": "Answer ONLY using the given context."
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{question}
"""
            }
        ],
        "temperature": 0.2
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    q = input("Ask a question: ")
    docs = get_relevant_docs(q, k=2)
    context = "\n".join(docs)

    print("\n=== Retrieved ===")
    print(context)

    print("\n=== Answer ===")
    print(ask_groq(context, q))