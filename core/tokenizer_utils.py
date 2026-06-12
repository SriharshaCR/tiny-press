from models.model_loader import get_llm


def count_tokens(text: str) -> int:
    _, tokenizer = get_llm()
    return len(tokenizer.encode(text, add_special_tokens=False))


def get_token_strings(text: str) -> list[str]:
    """Return the decoded surface string for every token in text."""
    _, tokenizer = get_llm()
    ids = tokenizer.encode(text, add_special_tokens=False)
    return [tokenizer.decode([i]) for i in ids]
