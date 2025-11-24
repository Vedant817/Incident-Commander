import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "huggingface")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")

MCP_MODE = os.getenv("MCP_MODE", "real")

VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "vector_store/faiss_index")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en")

MAX_PLAN_STEPS = int(os.getenv("MAX_PLAN_STEPS", "10"))
RISK_THRESHOLD = float(os.getenv("RISK_THRESHOLD", "0.7"))
REQUIRE_APPROVAL = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"

RUNBOOKS_PATH = os.getenv("RUNBOOKS_PATH", "runbooks/")

GRADIO_PORT = int(os.getenv("GRADIO_PORT", "7860"))
GRADIO_SHARE = os.getenv("GRADIO_SHARE", "false").lower() == "true"