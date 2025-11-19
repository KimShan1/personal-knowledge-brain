import { useState } from 'react';
import { MathJax } from 'better-react-mathjax';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState("");
  const [summary, setSummary] = useState("");
  const [summarizing, setSummarizing] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [answering, setAnswering] = useState(false);

  async function handleUpload() {
  if (!selectedFile) return;

  setUploading(true);
  setUploadResult("Uploading...");

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch("http://127.0.0.1:8000/upload-paper", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Upload failed: ${res.status}`);
    }

    const data = await res.json();
    setUploadResult(JSON.stringify(data, null, 2));
  } catch (err) {
    setUploadResult("Error: " + err.message);
  }

  setUploading(false);
}

async function handleSummarize() {
  setSummarizing(true);
  setSummary("Summarizing...");

  try {
    const res = await fetch("http://127.0.0.1:8000/summarize-paper", {
      method: "POST",
    });

    if (!res.ok) {
      throw new Error(`Summarize failed: ${res.status}`);
    }

    const data = await res.json();
    // Our FastAPI returns: { "summary": "..." }
    setSummary(data.summary || "No summary returned.");
  } catch (err) {
    setSummary("Error: " + err.message);
  }

  setSummarizing(false);
}

  async function handleAsk() {
    const trimmed = question.trim();
    if (!trimmed) return;

    setAnswering(true);
    setAnswer("Thinking...");

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!res.ok) {
        throw new Error(`Ask failed: ${res.status}`);
      }

      const data = await res.json();
      // Our FastAPI /ask returns: { "answer": "..." }
      setAnswer(data.answer || "No answer returned.");
    } catch (err) {
      setAnswer("Error: " + err.message);
    }

    setAnswering(false);
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Personal Knowledge Brain</h1>
        <p>Upload a paper, summarize it, and ask questions using RAG.</p>
      </header>

      <main className="app-main">
        {/* Section 1: Upload PDF */}
<section className="card">
  <h2>1. Upload PDF</h2>
  <p>
    Choose a PDF and upload it.
  </p>

  <input
    type="file"
    accept="application/pdf"
    onChange={(e) => setSelectedFile(e.target.files[0])}
  />

  <button onClick={handleUpload} disabled={!selectedFile || uploading}>
    {uploading ? "Uploading..." : "Upload PDF"}
  </button>

  <pre className="output-box">
    {uploadResult || "No upload yet."}
  </pre>		
</section>


  {/* Section 2: Summarize Paper */}
<section className="card">
  <h2>2. Summarize Paper</h2>
  <p>
    Once a paper is uploaded, you&apos;ll be able to generate a structured summary here.
  </p>

  <button onClick={handleSummarize} disabled={summarizing}>
    {summarizing ? "Summarizing..." : "Summarize Paper"}
  </button>

  <div className="output-box">
    <MathJax dynamic>
      {summary || "No summary yet."}
    </MathJax>
  </div>
</section>



 {/* Section 3: Ask a Question */}
<section className="card">
  <h2>3. Ask a Question about the Paper</h2>
  <p>Type a question and the app will answer using the uploaded paper (via RAG).</p>

  <textarea
    rows={3}
    placeholder="Example: Explain intuitively what a loss surface is and why it matters."
    value={question}
    onChange={(e) => setQuestion(e.target.value)}
  />

  <button onClick={handleAsk} disabled={answering || !question.trim()}>
    {answering ? "Thinking..." : "Ask"}
  </button>

  <div className="output-box">
    <MathJax dynamic>
      {answer || "No answer yet."}
    </MathJax>
  </div>
</section>

      </main>
    </div>
  );
}

export default App;

