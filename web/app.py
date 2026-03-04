from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from rag.retriever import get_relevant_docs
from rag.chat import ask_groq
from werkzeug.utils import secure_filename
import fitz 

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    filename = secure_filename(file.filename)

    text = ""

    if filename.endswith(".txt"):
        text = file.read().decode("utf-8", errors="ignore")

    elif filename.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()

    else:
        return jsonify({"error": "Only TXT or PDF supported"}), 400

    if len(text.strip()) == 0:
        return jsonify({"error": "No readable text found"}), 400

    emb = model.encode(text).tolist()

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")  # reset graph
        session.run(
            "CREATE (:Doc {text:$text, embedding:$emb})",
            text=text,
            emb=emb
        )

    return jsonify({"status": "Document uploaded and indexed successfully"})

@app.route("/chat", methods=["POST"])
def chat():
    question = request.json["question"]
    docs = get_relevant_docs(question, k=2)
    context = "\n".join(docs)
    answer = ask_groq(context, question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)