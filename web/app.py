from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from rag.retriever import get_relevant_docs
from rag.chat import ask_groq
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF

load_dotenv()

app = Flask(__name__)

# ------------------ Config ------------------
UPLOAD_FOLDER = "data/uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ Models & DB ------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# ------------------ Helpers ------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_bytes):
    text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

# ------------------ Routes ------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and TXT files are allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file_bytes = file.read()
    file.seek(0)
    file.save(filepath)

    # -------- Extract text --------
    try:
        if filename.lower().endswith(".txt"):
            text = file_bytes.decode("utf-8", errors="ignore")
        else:
            text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 500

    if not text.strip():
        return jsonify({"error": "No readable text found in document"}), 400

    # -------- Embed & Store --------
    embedding = model.encode(text).tolist()

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")  # reset graph
        session.run(
            """
            CREATE (:Document {
                filename: $filename,
                text: $text,
                embedding: $embedding
            })
            """,
            filename=filename,
            text=text,
            embedding=embedding
        )

    return jsonify({
        "status": "success",
        "filename": filename,
        "message": "Document uploaded and indexed successfully"
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please enter a question."})

    docs = get_relevant_docs(question, k=2)
    context = "\n".join(docs)

    answer = ask_groq(context, question)

    # Ensure clean text (no markdown **)
    answer = answer.replace("**", "")

    return jsonify({"answer": answer})

# ------------------ Local Run ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)