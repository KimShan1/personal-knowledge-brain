import os
from openai import OpenAI

# ---- OpenAI API key ----

# Read your API key from the environment variable OPENAI_API_KEY.
# You already added this to your ~/.zshrc and verified it with `echo $OPENAI_API_KEY`.
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. "
        "Make sure it is defined in your environment (e.g. in ~/.zshrc)."
    )

# Create a single OpenAI client for the whole backend to use.
client = OpenAI(api_key=api_key)


# ---- Vector store ID ----

# Read the vector store ID from OPENAI_VECTOR_STORE_ID.
# You created the vector store in the OpenAI UI and added its ID to ~/.zshrc.
VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")
if not VECTOR_STORE_ID:
    raise RuntimeError(
        "OPENAI_VECTOR_STORE_ID is not set. "
        "Create a vector store in the OpenAI dashboard and set its ID in ~/.zshrc."
    )

