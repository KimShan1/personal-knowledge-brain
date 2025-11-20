A full-stack RAG (Retrieval-Augmented Generation) application built with FastAPI + React + OpenAI Vector Stores
This project is a complete end-to-end implementation of a Personal Research Copilot that allows you to:
  - Upload any research paper
  - Automatically index it into an OpenAI Vector Store
  - Generate a structured mathematical summary (with LaTeX → MathJax rendering)
  - Ask questions grounded in the PDF using real RAG
  - Serve the backend via FastAPI and frontend via React + Vite

It was built from scratch, including:
custom ingestion pipeline
hosted vector store setup
rate limiting guardrails
frontend UI with MathJax
OpenAI Responses API + file_search integration
full React client → FastAPI backend → OpenAI vector store round-trip
replace-mode vector store for clean uploads
GitHub-ready repository structure

This project is intentionally simple but shows all essential RAG system components. 

### Demo (Architecture Overview):



            ┌──────────────────────────────┐
            │           Frontend           │
            │      React + Vite + JS       │
            │    - Upload PDF              │
            │    - Ask questions           │
            │    - View structured summary │
            │    - MathJax for LaTeX       │
            └──────────────┬───────────────┘
                           │ REST (CORS)
                           ▼
            ┌────────────────────────────────┐
            │            Backend             │
            │         FastAPI Server         │
            │                                │
            │ Endpoints:                     │
            │  - /upload-paper               │
            │  - /summarize-paper            │
            │  - /ask                        │
            │                                │
            │ Guardrails:                    │
            │  - per-IP rate limiting        │
            │  - PDF validation              │
            └──────────────┬─────────────────┘
                           │ OpenAI SDK
                           ▼
            ┌──────────────────────────────┐
            │      OpenAI Vector Store     │
            │   - Embedding + chunking     │
            │   - ANN search (cosine/IP)   │
            │   - file_search tool         │
            └──────────────────────────────┘

### Repo Structure

personal-knowledge-brain/
│
├── backend/
│   ├── app/
│   │   ├── config.py         # OpenAI client + env vars + vector store ID
│   │   ├── ingest.py         # Save PDF + upload + index to OpenAI store
│   │   ├── rag.py            # RAG summarization + RAG QA logic
│   │   ├── main.py           # FastAPI app, endpoints, rate limiting
│   │   └── uploads/          # User PDFs (gitignored)
│   └── requirements.txt      # FastAPI + OpenAI dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # UI + upload + summary + QA
│   │   ├── main.jsx          # MathJax provider + React root
│   │   └── App.css           # polished UI styling
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── README.md                 # You are reading it 🙂

### Technologies Used
*Frontend*
- React: the JavaScript library that builds the interactive UI.
- Vite: the dev server & build tool that runs React fast and bundles the final website.
- JavaScript (ES6+): It handles button clicks, storing the PDF file in memory, calling the API, displaying the response. React is built on top of JavaScript.
- Fetch API (for calling backend routes): It sends data from the frontend → backend and retrieves results.
- Vite environment variables (import.meta.env): A secure configuration system for Vite. To avoid hardcoding the backend URL into your code.
- Render (Static Site Hosting)
- MathJax (via better-react-mathjax): A library that displays math, formulas, and equations beautifully in the browser

*Backend*
- FastAPI: A modern, high-performance web framework for Python. Frontend needs to call the backend via HTTP and FastAPI provides these routes:
| FastAPI Route           | Purpose                                          |
| ----------------------- | ------------------------------------------------ |
| `POST /upload-paper`    | Receive the PDF + index into OpenAI vector store |
| `POST /summarize-paper` | Generate structured summary                      |
| `POST /ask`             | Answer user questions using RAG                  |
| `GET /`                 | Health check                                     |

- Uvicorn: A lightning-fast web server for Python/ASGI. FastAPI does not serve itself —> Uvicorn runs it
- Pydantic: A data validation library FastAPI uses (enforces proper request formats, ensures user input is the correct type, automatically returns validation errors)
- CORS Middleware: Middleware that controls which websites can call my API. Browsers block cross-site requests by default; CORS middleware tells the browser:"Yes, it’s safe — allow our frontend to talk to the backend."
- Render Web Service Hosting: A hosting platform that runs the FastAPI app 24/7
  
*OpenAI*
- OpenAI Python SDK (2024)
- Responses API (client.responses.create)
- File Upload API
- Vector Store API: An OpenAI-managed vector database that stores embeddings of the PDF content for RAG.
- File Search tool
- gpt-4o-mini (cost-efficient model for RAG)

### Features
1. PDF Upload → Automatic Vectorization
PDFs uploaded via the React interface are saved locally, then:
- sent to OpenAI via client.files.create()
- indexed into an OpenAI vector store
- replace-mode ensures only one paper is stored at a time (clean UX)
  
2. RAG Summarization (Structured, Mathematical, Concise)
Uses OpenAI’s file_search to retrieve relevant chunks and returns:
- high-level overview
- key concepts
- bullet points
- formulas rendered in LaTeX ($$...$$) -> Math is rendered visually thanks to MathJax on the frontend
- intuitive explanations

3. RAG Question Answering
Users can ask natural language questions and receive grounded answers from the paper

4. Backend with Rate Limiting
Custom guardrail:
- 5 requests per minute per IP
- prevents abuse and accidental infinite loops





