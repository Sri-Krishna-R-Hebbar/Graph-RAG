from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

with driver.session() as session:
    docs = session.run("MATCH (d:Doc) RETURN d.id AS id, d.text AS txt")
    for d in docs:
        emb = model.encode(d["txt"]).tolist()
        session.run("MATCH (d:Doc {id:$id}) SET d.embedding=$emb",
                    id=d["id"], emb=emb)

print("✅ Embeddings added")