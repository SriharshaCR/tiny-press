import os

# Model settings
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
EMBEDDER_MODEL = os.getenv("EMBEDDER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Curated <32B open-weight causal LMs for local inference (shown in the UI dropdown).
AVAILABLE_MODELS = [
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "microsoft/Phi-3.5-mini-instruct",
    "meta-llama/Llama-3.2-1B-Instruct",
]

# Curated sentence-transformer embedding models for quality scoring.
AVAILABLE_EMBEDDER_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "BAAI/bge-small-en-v1.5",
    "BAAI/bge-base-en-v1.5",
    "mixedbread-ai/mxbai-embed-large-v1",
    "Alibaba-NLP/gte-Qwen2-1.5B-instruct",
]

EMBEDDER_INFO = {
    "sentence-transformers/all-MiniLM-L6-v2": (
        "⚡ **Fast · 22M params · Default**  \n"
        "Great baseline. Scores are reliable for typical compression ratios. "
        "Runs comfortably on CPU — minimal overhead."
    ),
    "sentence-transformers/all-mpnet-base-v2": (
        "⚖️ **Balanced · 110M params**  \n"
        "Noticeably sharper quality scores than MiniLM, especially on longer texts. "
        "Small speed trade-off; fine on CPU."
    ),
    "BAAI/bge-small-en-v1.5": (
        "⚡ **Fast · 33M params**  \n"
        "Strong quality-to-size ratio — often matches MiniLM on accuracy while being "
        "slightly more sensitive to meaning shifts. Good CPU option."
    ),
    "BAAI/bge-base-en-v1.5": (
        "⚖️ **Balanced · 109M params**  \n"
        "Consistently strong on semantic similarity benchmarks. "
        "Scores will be more discriminating — small differences in compression quality show up more clearly."
    ),
    "mixedbread-ai/mxbai-embed-large-v1": (
        "🏆 **High quality · 335M params**  \n"
        "Top-tier similarity scores. Quality readings will be the most accurate here, "
        "but slower to load and run. GPU recommended."
    ),
    "Alibaba-NLP/gte-Qwen2-1.5B-instruct": (
        "🔬 **Best quality · 1.5B params**  \n"
        "Strongest semantic understanding in this list. Scores will reflect subtle meaning loss "
        "that smaller models miss. Requires significant RAM/VRAM — GPU strongly recommended."
    ),
}

# Compression settings
DEFAULT_TARGET_TOKENS = 500
MAX_NEW_TOKENS = 1024

# Gradio
APP_TITLE = "TinyPress"
SERVER_PORT = int(os.getenv("PORT", 7860))
