import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import ingest
from . import rag

# --------- Rate limiting guardrails ---------

# Time window in seconds
RATE_LIMIT_WINDOW = 60

# Max number of calls per IP per window
RATE_LIMIT_MAX_CALLS = 5

# In-memory store of IP -> list of timestamps
client_usage = {}


def rate_limit(request: Request):
    """
    Simple per-IP rate limit:
    - At most RATE_LIMIT_MAX_CALLS calls
    - Within the last RATE_LIMIT_WINDOW seconds
    """
    ip = request.client.host
    now = time.time()

    # Initializing list for this IP if needed
    if ip not in client_usage:
        client_usage[ip] = []

    # Keeping only timestamps within the window
    recent_calls = [t for t in client_usage[ip] if now - t < RATE_LIMIT_WINDOW]
    client_usage[ip] = recent_calls

    # If too many calls in this window, blocking
    if len(recent_calls) >= RATE_LIMIT_MAX_CALLS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait a bit before trying again."
        )

    # Recording this call
    client_usage[ip].append(now)


# --------- FastAPI app setup ---------

app = FastAPI()

# Allowing my React frontend (different port) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # OK for local dev; ideally would need to be tighten later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}


@app.post("/upload-paper")
async def upload_paper(request: Request, file: UploadFile = File(...)):
    """
    1) Apply rate limit for this IP
    2) Validate that the uploaded file is a PDF
    3) Save it locally
    4) Index it into your OpenAI vector store
    """
    # Guardrail: basic rate limiting
    rate_limit(request)

    # Validating MIME type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Saving PDF locally (app/uploads/...)
    saved_path = await ingest.save_uploaded_pdf(file)

    # Uploading + attach to OpenAI vector storee
    try:
        indexing_info = ingest.index_pdf_in_openai(
            saved_path,
            replace_existing=True,  # <- clearing old files first
        )
    except Exception as e:
        # TEMPORARY: surfacing full error for debugging
        print("Error while indexing PDF in OpenAI:", repr(e))
        raise HTTPException(status_code=500, detail=f"Indexing error: {repr(e)}")


    return {
        "filename": file.filename,
        "stored_path": str(saved_path),
        "openai_file_id": indexing_info["file_id"],
        "vector_store_id": indexing_info["vector_store_id"],
        "message": "PDF uploaded and indexed successfully.",
    }


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask_question(request: Request, payload: Question):
    """
    Takes a natural language question and answers it using
    the PDFs in our OpenAI vector store (RAG).
    """
    # Guardrail: basic rate limiting
    rate_limit(request)

    answer = rag.answer_question(payload.question)
    return {"answer": answer}

@app.post("/summarize-paper")
def summarize_paper_endpoint(request: Request):
    """
    Returns a structured summary of the paper(s) in the vector store.

    This uses the RAG pipeline with a fixed 'summarize' prompt so that
    the frontend can call it without the user typing a question.
    """

    rate_limit(request)

    summary = rag.summarize_paper()
    return {"summary": summary}


