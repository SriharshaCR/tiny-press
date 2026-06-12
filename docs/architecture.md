# Architecture

TinyPress is built modular — each concern lives in its own place, nothing bleeds into something it shouldn't.

## How a compression request flows

```
User Input (Gradio UI)
        │
        ▼
  core/compressor.py       ← builds the prompt, calls the model, trims if it overshoots
        │
        ▼
  models/model_loader.py   ← Qwen2.5-1.5B-Instruct, loaded once and reused
        │
        ▼
  core/scorer.py           ← checks how much meaning survived using all-MiniLM-L6-v2
        │
        ▼
  db/store.py              ← saves the run to memory (session only)
        │
        ▼
  ui/compress_tab.py       ← shows the result and metrics back to the user
```

## What each module does

| Module | Responsibility |
|---|---|
| `app.py` | Starts everything — model load, Gradio launch |
| `config.py` | One place for all settings — model names, token limits, port |
| `ui/compress_tab.py` | The compression interface — input, slider, output, metrics |
| `ui/history_tab.py` | History view — past runs, averages, trends |
| `core/compressor.py` | Builds the compression prompt, runs generation, hard-trims if needed |
| `core/scorer.py` | Cosine similarity between original and compressed text |
| `core/tokenizer_utils.py` | Token counting and per-token string extraction using the LLM's own tokenizer |
| `core/diff.py` | Word-level SequenceMatcher diff — produces annotated HTML for the history side-by-side view |
| `models/model_loader.py` | Singleton model store — loads LLM + embedder on demand, supports hot-swapping both via `switch_llm` / `switch_embedder` |
| `db/store.py` | In-memory run store — save, fetch, update feedback, delete; data lives for the session only |
| `db/schema.sql` | The `compression_runs` table definition (reference only — not used at runtime) |

## A few decisions worth knowing

**Models load once at startup.** This matters on a laptop — you don't want to reload a 1.5B model on every request. Both the LLM and the embedder are held in memory after the first load.

**Model hot-swapping without a restart.** The Model Settings accordion in the UI lets you pick a different compression model or scoring embedder mid-session. Both `switch_llm` and `switch_embedder` in `model_loader.py` unload the current model (deletes the references, calls `gc.collect`, and flushes the CUDA cache if a GPU is present) before loading the new one — so you don't end up with two large models in memory at once.

**Hard token trim as a safety net.** If the model overshoots the target budget, the output gets trimmed at the tokenizer level. It's a fallback, not the primary path — the prompt already asks the model to stay within budget.

**Thin UI layer.** The Gradio handlers in `ui/` don't contain logic. They take inputs, call into `core/`, and return outputs. All the real work happens in `core/` and `db/`.

**In-memory run store.** Compression history is held in a Python list for the duration of the session. There is no database on disk — this keeps the app stateless and portable (HF Spaces, Colab). `feedback` is `None` by default, `1` = 👍, `-1` = 👎. `feedback_comment` holds the optional text note.


🏠 [README.md](../README.md)
