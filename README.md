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

## Project Flow

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

## Application Behavior

### 1. Document Upload

The user uploads PDF, DOCX, or TXT files from the sidebar. These files become the knowledge base for the chatbot. The backend extracts text from each file and prepares it for semantic search.

### 2. Text Processing

The extracted document text is cleaned by removing unnecessary short lines, headings, extra spaces, and repeated line breaks. The cleaned content is then divided into smaller overlapping chunks so that the chatbot can retrieve accurate context for each question.

### 3. Vector Embedding and Storage

Each text chunk is converted into a numerical embedding using the `sentence-transformers/all-mpnet-base-v2` model. These embeddings are stored in a FAISS vector index, which helps the application quickly find the most relevant document sections for a user query.

### 4. User Question

When the user asks a question, the question is also converted into an embedding. FAISS compares the question embedding with the stored document embeddings and retrieves the most similar chunks.

### 5. Answer Generation

The retrieved chunks are passed as context to the Hugging Face Llama model. The prompt instructs the model to answer only from the uploaded documents. This helps reduce unrelated or unsupported answers.

### 6. Source Display

The frontend displays the generated answer along with the source file names used to answer the question. This makes the response easier to verify.

## Response Handling

The chatbot handles different query situations:

- Greeting messages such as `hi`, `hello`, and `hey` receive a friendly response.
- If documents are uploaded, greetings confirm that the knowledge base is ready.
- If no documents are uploaded, the chatbot asks the user to upload documents first.
- If the question is related to the uploaded documents, the chatbot gives a document-based answer.
- If the question is not related to the uploaded documents, the chatbot replies that the question is not related to the uploaded content.
- If the answer is not present in the retrieved context, the chatbot says that the information is not available in the provided documents.

## Upload Limits

The backend includes upload limits to keep document processing fast and controlled:

- Maximum number of files per upload: `5`
- Maximum file size: `5 MB` per file
- Supported file types: `.pdf`, `.docx`, `.txt`

If the user uploads more than 5 files, uploads a file larger than 5 MB, or uploads a file that cannot be processed, the application returns an error message instead of indexing the file.

## Demo Screenshots

Add your project screenshots to a folder named `screenshots/` and update the image paths below.

### Home Page

Shows the initial chat interface before uploading documents.

```md
![Home Page](screenshots/home-page.png)
```

### Greeting Response

Shows how the chatbot responds to greetings like `hi`.

```md
![Greeting Response](screenshots/greeting-response.png)
```

### Relevant Document Answer

Shows the chatbot answering a question using information from uploaded documents.

```md
![Relevant Answer](screenshots/relevant-answer.png)
```

### Information Not Present

Shows the chatbot response when the requested information is not available in the uploaded documents.

```md
![Information Not Present](screenshots/info-not-present.png)
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

No license has been added to this repository yet.
