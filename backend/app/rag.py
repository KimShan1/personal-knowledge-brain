from .config import client, VECTOR_STORE_ID

# ---- Model + safety limits ----

# We'll use a small, cheap model good for RAG.
MODEL_NAME = "gpt-4.1-mini"

# Hard limit for how long answers can be.
# This controls cost per request.
MAX_TOKENS = 800


def answer_question(question: str) -> str:
    """
    Ask OpenAI to answer a question using our vector store (RAG).

    It uses the Responses API + file_search tool so OpenAI:
    - searches your vector store (where your PDFs are indexed)
    - writes an answer grounded in those documents
    """

    # This is the actual RAG call to OpenAI.
    # - model: which model to use
    # - input: the user's question
    # - tools: tell the model it can use file_search on your vector store
    # - max_output_tokens: guardrail on answer length / cost
    response = client.responses.create(
        model=MODEL_NAME,
        input=question,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID],
        }],
        max_output_tokens=MAX_TOKENS,
    )

    # The Responses API returns a structured object.
    # We now try to extract the final answer text from it.
    try:
        # Often, the last output item contains the final answer.
        last_output = response.output[-1]
        first_block = last_output.content[0]

        # Depending on SDK version, .text might be a string
        # or an object with a .value attribute.
        text = getattr(first_block, "text", None)

        if hasattr(text, "value"):
            return text.value  # case: text is an object like { value: "..." }

        if isinstance(text, str):
            return text  # case: text is already a string

    except Exception:
        # If something changes in the response structure,
        # we don't want your app to crash.
        return "Sorry, I couldn't extract the answer properly from the model output."

    # Fallback: at least return the whole response as a string (for debugging).
    return str(response)

def summarize_paper() -> str:
    """
    Generate a structured summary of the paper(s) in the vector store.

    This uses the same RAG mechanism (file_search) but with a fixed prompt
    focused on:
    - high-level overview
    - key concepts
    - main formulas/results
    - intuition
    """

    prompt = (
        "You are an AI research assistant. Using the research paper(s) stored in "
        "the vector store (via file_search), write a structured summary with the "
        "following sections:\n\n"
        "1. High-level overview (2–3 sentences).\n"
        "2. Key concepts and definitions (bullet points).\n"
        "3. Main results and important formulas (use LaTeX and wrap display equations in $$ ... $$ blocks).\n"
        "4. Intuition and implications: why these results matter for training or understanding neural networks.\n\n"
        "Keep the overall answer concise (max ~600–700 words) but mathematically informative and intuitive."
    )

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID],
        }],
        max_output_tokens=MAX_TOKENS,
    )

    # Reuse the same extraction logic as in answer_question
    try:
        last_output = response.output[-1]
        first_block = last_output.content[0]
        text = getattr(first_block, "text", None)

        if hasattr(text, "value"):
            return text.value

        if isinstance(text, str):
            return text

    except Exception:
        return "Sorry, I couldn't extract the summary properly from the model output."

    return str(response)

