# graph/setup_db.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

with open("data/documents.txt") as f:
    lines = [l.strip() for l in f if l.strip()]

with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")  # reset
    for i, text in enumerate(lines):
        session.run(
            "CREATE (:Doc {id:$id, text:$text})",
            id=i, text=text
        )

print("✅ Documents loaded")