# Setup

## What you need

**Hardware**

| | Minimum (CPU) | Recommended (GPU) |
|---|---|---|
| RAM | 8 GB | 8 GB+ |
| VRAM | — | 4 GB (e.g. NVIDIA T4) |
| Disk | ~4 GB free | ~4 GB free |
| Inference speed | Slow (float32) | Fast (float16, auto device map) |

The default model (Qwen2.5-1.5B-Instruct) fits in 4 GB VRAM. Larger models from the dropdown (e.g. Phi-3.5-mini) need more headroom.

**Software**

- Python 3.10 or above

**Network**

- Internet required on first run only — model weights (~3.5 GB total) download from HuggingFace and are cached locally
- Fully offline after that

## Steps

**1. Navigate to the project folder**

```bash
cd app
```

**2. Create and activate the virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Optionally tweak the defaults**

You can override any of these via environment variables if needed:

| Variable | Default | What it does |
|---|---|---|
| `LLM_MODEL` | `Qwen/Qwen2.5-1.5B-Instruct` | The model used for compression |
| `EMBEDDER_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Used to score compression quality |
| `DB_PATH` | `tinypress.db` | Where the SQLite database lives |
| `PORT` | `7860` | Port the Gradio app listens on |

**5. Run it**

```bash
python app.py
```

The first time you run it, model weights will download from HuggingFace automatically. After that, everything runs from local cache.

## Managing dependencies

**Installing a new package**

```bash
pip install <package-name>
pip freeze > requirements.txt
```

**Removing a package**

```bash
pip uninstall <package-name>
pip freeze > requirements.txt
```

Always run `pip freeze > requirements.txt` after any install or uninstall — that keeps the file in sync with what's actually in your environment.

## Deactivating the virtual environment

When you're done, just run:

```bash
deactivate
```

That drops you back to your system Python. Next time, activate again with `.venv\Scripts\activate` before working on the project.


🏠 [README.md](../README.md)
