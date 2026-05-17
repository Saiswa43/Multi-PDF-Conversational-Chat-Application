import os
import re
import numpy as np
import faiss
import fitz
import tempfile
import toml
from docx import Document
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

# ---------------- CONFIG ----------------
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
INITIAL_TOP_K = 5
FINAL_TOP_K = 3
MAX_FILES = 5
MAX_FILE_SIZE_MB = 5

# ---------------- INITIALIZE ----------------
app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOAD API KEY ----------------
try:
    secrets = toml.load(".streamlit/secrets.toml")
    HF_API_KEY = secrets.get("HF_API_KEY")
except Exception:
    HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_API_KEY
)

# ---------------- EMBEDDING MODEL ----------------
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---------------- STATE ----------------
all_chunks = []
index = None

# ---------------- HELPERS ----------------
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line_strip = line.strip()
        if len(line_strip) < 5 or line_strip.isupper() or "UNIT" in line_strip:
            continue
        cleaned_lines.append(line_strip)

    text = " ".join(cleaned_lines)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_text(file_content, filename):
    if filename.endswith(".pdf"):
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            return "".join([page.get_text() for page in doc])

    elif filename.endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        doc = Document(tmp_path)
        os.remove(tmp_path)

        return "\n".join([para.text for para in doc.paragraphs])

    elif filename.endswith(".txt"):
        return file_content.decode("utf-8")

    return ""


def create_chunks(text, filename):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= CHUNK_SIZE:
            current_chunk += " " + sentence
        else:
            chunks.append({
                "text": current_chunk.strip(),
                "source": filename
            })
            overlap_text = current_chunk[-CHUNK_OVERLAP:]
            current_chunk = overlap_text + " " + sentence

    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "source": filename
        })

    return chunks


# ---------------- GREETING ----------------
def is_greeting(text):
    if not text:
        return False
    greetings = ["hi", "hello", "hey", "hii", "good morning", "good evening"]
    return text.lower().strip() in greetings


def greeting_response(has_docs):
    if has_docs:
        return "Hello! Your documents are ready. What would you like to know?"
    else:
        return "Hello! Please upload documents first."


# ---------------- CLEAN OUTPUT ----------------
def clean_output(text):
    if not isinstance(text, str):
        return text

    text = text.replace("• ", "\n• ")
    text = re.sub(r'(?<!\n)\n•', '\n\n•', text)

    lines = text.split("\n")
    cleaned = []
    seen_source = False

    for line in lines:
        if "Source:" in line:
            if not seen_source:
                cleaned.append("\n" + line.strip())
                seen_source = True
        else:
            cleaned.append(line.strip())

    text = "\n\n".join(cleaned)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# ---------------- UPLOAD ----------------
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    global all_chunks, index

    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FILES} files allowed.")

    new_chunks = []

    for file in files:
        content = await file.read()

        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} exceeds {MAX_FILE_SIZE_MB} MB limit."
            )

        raw_text = extract_text(content, file.filename)
        cleaned_text = clean_text(raw_text)
        chunks = create_chunks(cleaned_text, file.filename)
        new_chunks.extend(chunks)

    if not new_chunks:
        raise HTTPException(status_code=400, detail="No text extracted from files.")

    all_chunks.extend(new_chunks)

    texts = [c["text"] for c in all_chunks]
    embeddings = embedding_model.encode(texts)
    embeddings = np.array(embeddings).astype("float32")

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return {
        "status": "success",
        "total_chunks": len(all_chunks),
        "added_chunks": len(new_chunks)
    }


# ---------------- CLEAR ----------------
@app.post("/clear")
async def clear_knowledge_base():
    global all_chunks, index
    all_chunks = []
    index = None
    return {"status": "success"}


# ---------------- QUERY ----------------
@app.post("/query")
async def query_llm(user_query: Dict[str, str]):
    global all_chunks, index

    query = user_query.get("query")

    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if is_greeting(query):
        return {
            "answer": greeting_response(len(all_chunks) > 0),
            "sources": []
        }

    if not all_chunks or index is None:
        raise HTTPException(status_code=400, detail="Upload documents first.")

    # Embedding
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)

    distances, indices = index.search(query_embedding, INITIAL_TOP_K)

    results = []
    for i, idx in enumerate(indices[0]):
        results.append({
            "score": float(distances[0][i]),
            "text": all_chunks[idx]["text"],
            "source": all_chunks[idx]["source"]
        })

    # Filtering
    SIMILARITY_THRESHOLD = 0.3
    filtered_results = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]

    if not filtered_results:
        return {
            "answer": "Sorry, this question is not related to the uploaded documents.",
            "sources": []
        }

    results = sorted(filtered_results, key=lambda x: x["score"], reverse=True)[:FINAL_TOP_K]

    context = "\n\n".join([
        f"Document: {r['source']}\nContent: {r['text']}"
        for r in results
    ])

    prompt = f"""
You are a professional AI assistant.

Answer ONLY using the context below.
If answer not found, say:
"This information is not available in the provided documents."

Context:
{context}

Question:
{query}

Answer:
"""

    try:
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )

        raw_answer = response.choices[0].message.content
        answer = clean_output(raw_answer)

        return {
            "answer": answer,
            "sources": list(set([r["source"] for r in results]))
        }

    except Exception as e:
        return {"error": str(e)}


# ---------------- HEALTH ----------------
@app.get("/health")
async def health():
    return {"status": "ok"}
