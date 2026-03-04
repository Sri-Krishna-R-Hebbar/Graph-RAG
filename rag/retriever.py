# rag/retriever.py
import os
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # required
HF_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def get_embedding(text: str):
    """Get embedding using Hugging Face Inference API"""
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{HF_EMBEDDING_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    response = requests.post(url, headers=headers, json={"inputs": text})
    response.raise_for_status()
    return response.json()[0]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b)


def get_relevant_docs(question, k=2):
    query_emb = get_embedding(question)

    with driver.session() as session:
        records = session.run(
            "MATCH (d:Document) RETURN d.text AS text, d.embedding AS embedding"
        )

        scored = []
        for r in records:
            score = cosine_similarity(query_emb, r["embedding"])
            scored.append((score, r["text"]))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [text for _, text in scored[:k]]