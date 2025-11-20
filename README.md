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
            │    - Upload PDF             │
            │    - Ask questions          │
            │    - View structured summary│
            │    - MathJax for LaTeX      │
            └──────────────┬──────────────┘
                           │ REST (CORS)
                           ▼
            ┌──────────────────────────────┐
            │            Backend            │
            │         FastAPI Server        │
            │                                │
            │ Endpoints:                     │
            │  - /upload-paper               │
            │  - /summarize-paper            │
            │  - /ask                        │
            │                                │
            │ Guardrails:                    │
            │  - per-IP rate limiting        │
            │  - PDF validation              │
            └──────────────┬────────────────┘
                           │ OpenAI SDK
                           ▼
            ┌──────────────────────────────┐
            │      OpenAI Vector Store     │
            │   - Embedding + chunking     │
            │   - ANN search (cosine/IP)   │
            │   - file_search tool         │
            └──────────────────────────────┘
