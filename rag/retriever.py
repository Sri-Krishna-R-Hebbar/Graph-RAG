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

def get_relevant_docs(query, k=3):
    emb = model.encode(query).tolist()
    with driver.session() as session:
        result = session.run(
            """
            CALL db.index.vector.queryNodes('docIndex', $k, $emb)
            YIELD node, score
            RETURN node.text AS text
            """,
            k=k, emb=emb
        )
        return [record["text"] for record in result]