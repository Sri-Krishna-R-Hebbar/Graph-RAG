# GraphRAG Chat Application

A simple **GraphRAG (Graph + Retrieval Augmented Generation)** demo built using **Neo4j**, **Groq LLM**, and **Flask**.  
Users can upload a PDF or TXT document and ask questions grounded in the uploaded content.

---

## 🚀 Features
- Upload **PDF / TXT** documents
- Graph-based retrieval using **Neo4j**
- Semantic embeddings with **Sentence Transformers**
- LLM responses powered by **Groq (openai/gpt-oss-120b)**
- Clean, professional UI
- Ready for cloud deployment (Render)

---

## 🏗️ Tech Stack
- **Backend**: Python, Flask
- **Graph DB**: Neo4j Aura
- **LLM**: Groq API
- **Embeddings**: all-MiniLM-L6-v2
- **Frontend**: HTML, CSS, JS

---

## 📂 Project Structure

```
Graph-RAG/
│
├── rag/
│   ├── ingest.py
│   ├── retriever.py
│   ├── chat.py
│
├── web/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
│
├── uploads/
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_key

NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
AURA_INSTANCEID=xxxx
AURA_INSTANCENAME=Instance01
```

---

## ▶️ Run Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m web.app
```

Open: http://127.0.0.1:5000