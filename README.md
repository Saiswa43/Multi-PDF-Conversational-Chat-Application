# Multi-PDF Conversational Chat Application

A full-stack Retrieval-Augmented Generation (RAG) chatbot that lets users upload documents and ask questions based on their content. The application extracts text from uploaded files, converts the text into embeddings, stores them in a FAISS vector index, retrieves the most relevant chunks for each query, and generates answers using a Hugging Face-hosted Llama model.

## Features

- Upload multiple documents as a knowledge base
- Ask questions about uploaded document content
- Supports PDF, DOCX, and TXT file extraction
- Uses semantic search with Sentence Transformers and FAISS
- Generates grounded answers with Hugging Face Inference API
- Displays source filenames for answers
- Includes a modern React chat interface
- Provides a clear knowledge-base reset option
- Handles greetings and empty knowledge-base states

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- PyMuPDF for PDF text extraction
- python-docx for DOCX text extraction
- Sentence Transformers for embeddings
- FAISS for vector similarity search
- Hugging Face Inference API for LLM responses

### Frontend

- React
- Vite
- Lucide React icons
- Framer Motion
- React Markdown
- CSS-based dark glass UI

## Project Structure

```text
assignment-main/
|-- api.py
|-- requirements.txt
|-- .gitignore
|-- README.md
`-- frontend/
    |-- index.html
    |-- package.json
    |-- package-lock.json
    |-- vite.config.js
    `-- src/
        |-- App.jsx
        |-- index.css
        `-- main.jsx
```

Generated folders such as `venv/`, `node_modules/`, `__pycache__/`, and `.streamlit/` are ignored by Git.

## How It Works

1. The user uploads one or more documents from the frontend.
2. The frontend sends the files to the FastAPI `/upload` endpoint.
3. The backend extracts text from each document.
4. Extracted text is cleaned and split into overlapping chunks.
5. Sentence Transformer embeddings are generated for all chunks.
6. The embeddings are normalized and stored in a FAISS index.
7. When the user asks a question, the backend embeds the query.
8. FAISS retrieves the most relevant chunks.
9. The retrieved chunks are sent as context to the Hugging Face LLM.
10. The model returns an answer based only on the uploaded documents.

## Backend API

### `GET /health`

Checks whether the backend is running.

Response:

```json
{
  "status": "ok"
}
```

### `POST /upload`

Uploads and indexes documents.

Limits configured in `api.py`:

- Maximum files: `5`
- Maximum file size: `5 MB` per file
- Supported extensions: `.pdf`, `.docx`, `.txt`

Response example:

```json
{
  "status": "success",
  "total_chunks": 12,
  "added_chunks": 12
}
```

### `POST /query`

Sends a user question to the chatbot.

Request body:

```json
{
  "query": "What is this document about?"
}
```

Response example:

```json
{
  "answer": "The document explains...",
  "sources": ["example.pdf"]
}
```

### `POST /clear`

Clears the current in-memory knowledge base and FAISS index.

Response:

```json
{
  "status": "success"
}
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Saiswa43/Multi-PDF-Conversational-Chat-Application.git
cd Multi-PDF-Conversational-Chat-Application
```

### 2. Create a Python Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Hugging Face API Key

Create a `.streamlit/secrets.toml` file in the project root:

```toml
HF_API_KEY = "your_huggingface_api_key_here"
```

Alternatively, set it as an environment variable:

```bash
set HF_API_KEY=your_huggingface_api_key_here
```

For PowerShell:

```powershell
$env:HF_API_KEY="your_huggingface_api_key_here"
```

Do not commit `.streamlit/secrets.toml` to GitHub.

### 5. Run the Backend

```bash
uvicorn api:app --reload
```

The backend will run at:

```text
http://localhost:8000
```

### 6. Install Frontend Dependencies

Open another terminal:

```bash
cd frontend
npm install
```

### 7. Run the Frontend

```bash
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

The Vite development server proxies `/api` requests to `http://localhost:8000`, so the backend and frontend should both be running during development.

## Usage

1. Start the backend with `uvicorn api:app --reload`.
2. Start the frontend with `npm run dev`.
3. Open `http://localhost:5173`.
4. Click `Add Sources` and upload PDF, DOCX, or TXT files.
5. Ask questions in the chat input.
6. Use `Clear Knowledge Base` to remove uploaded document context.

## Important Notes

- The FAISS index and uploaded document chunks are stored in memory only.
- Restarting the backend clears the knowledge base.
- The app currently allows CORS from all origins for development.
- The Hugging Face API key is required for answer generation.
- The first backend startup may take time because the embedding model is loaded.
- The first query may also be slower depending on model/API response time.

## Current Configuration

The main backend settings are defined in `api.py`:

```python
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
INITIAL_TOP_K = 5
FINAL_TOP_K = 3
MAX_FILES = 5
MAX_FILE_SIZE_MB = 5
```

The embedding model used is:

```text
sentence-transformers/all-mpnet-base-v2
```

The LLM configured through Hugging Face is:

```text
meta-llama/Meta-Llama-3-8B-Instruct
```

## Future Improvements

- Add persistent vector storage
- Add user authentication
- Add document deletion per file
- Add upload progress indicators
- Improve mobile responsiveness
- Add tests for backend endpoints
- Add production deployment configuration
- Restrict CORS origins for production use

## License

This project is for educational and assignment purposes.
