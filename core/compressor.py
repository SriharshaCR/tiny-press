import torch
import config
from core.tokenizer_utils import count_tokens
from models.model_loader import get_llm


_PROMPT_TEMPLATE = """You are a lossless compression assistant. Compress the following text to at most {target} tokens.
Preserve all key facts, decisions, and intent. Do not add commentary. Output only the compressed text.

TEXT:
{text}

COMPRESSED:"""


def _generate(prompt: str) -> str:
    model, tokenizer = get_llm()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=config.MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def compress(text: str, target_tokens: int) -> tuple[str, int, int]:
    """Returns (compressed_text, input_token_count, output_token_count)."""
    input_tokens = count_tokens(text)

    # If already within budget, return as-is
    if input_tokens <= target_tokens:
        return text, input_tokens, input_tokens

    prompt = _PROMPT_TEMPLATE.format(target=target_tokens, text=text)
    compressed = _generate(prompt)

    # Trim to hard token limit if model overshoots
    _, tokenizer = get_llm()
    ids = tokenizer.encode(compressed, add_special_tokens=False)
    if len(ids) > target_tokens:
        compressed = tokenizer.decode(ids[:target_tokens], skip_special_tokens=True)

    output_tokens = count_tokens(compressed)
    return compressed, input_tokens, output_tokens
