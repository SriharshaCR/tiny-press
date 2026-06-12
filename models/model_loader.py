from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import torch
import gc
import config

_llm = None
_tokenizer = None
_embedder = None
_current_model_id = None
_current_embedder_id = None


def get_current_model_id() -> str | None:
    return _current_model_id


def get_current_tokenizer_id() -> str | None:
    # Tokenizer is always loaded from the same HF repo as the model.
    return _current_model_id


def get_current_embedder_id() -> str | None:
    return _current_embedder_id


def get_llm():
    global _llm, _tokenizer
    if _llm is None:
        _load_llm(config.LLM_MODEL)
    return _llm, _tokenizer


def switch_llm(model_id: str) -> str:
    global _current_model_id
    if _current_model_id == model_id:
        return f"Already using {model_id}"
    _unload_llm()
    _load_llm(model_id)
    return f"Loaded: {model_id}"


def _load_llm(model_id: str):
    """Load model + its paired tokenizer. Both come from the same model_id."""
    global _llm, _tokenizer, _current_model_id
    _tokenizer = AutoTokenizer.from_pretrained(model_id)
    _llm = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        device_map="auto",
    )
    _llm.eval()
    _current_model_id = model_id


def _unload_llm():
    """Free GPU/CPU memory before loading a different model."""
    global _llm, _tokenizer, _current_model_id
    del _llm
    del _tokenizer
    _llm = None
    _tokenizer = None
    _current_model_id = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def get_embedder():
    global _embedder, _current_embedder_id
    if _embedder is None:
        _load_embedder(config.EMBEDDER_MODEL)
    return _embedder


def switch_embedder(model_id: str) -> str:
    global _current_embedder_id
    if _current_embedder_id == model_id:
        return f"Already using {model_id}"
    _unload_embedder()
    _load_embedder(model_id)
    return f"Loaded: {model_id}"


def _load_embedder(model_id: str):
    global _embedder, _current_embedder_id
    _embedder = SentenceTransformer(model_id)
    _current_embedder_id = model_id


def _unload_embedder():
    global _embedder, _current_embedder_id
    del _embedder
    _embedder = None
    _current_embedder_id = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
