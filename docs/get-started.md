# Get Started

Once `python app.py` is running, head to `http://localhost:7860` in your browser. You'll see two tabs.

## Compress tab

This is where the action is.

1. Paste your text — could be a long prompt, meeting notes, an article, anything really
2. Use the slider to set your token budget (anywhere from 100 to 1000)
3. Hit **Compress**

As you type or adjust the slider, a status banner updates live:
- **Green** — the input is over budget, compression will run
- **Red** — the input is already within budget, nothing to do

On the right you'll see:
- The compressed version of your text
- How many tokens went in vs came out
- The compression ratio (how much it shrank)
- A quality score between 0 and 1 — closer to 1 means the meaning held up well

Once the result appears, **👍 Helpful** and **👎 Not helpful** buttons show up below the metrics. Click either one to rate the result — the feedback is saved instantly. A note field then slides in where you can optionally type what worked well or didn't (e.g. "lost key dates", "too short", "great summary") and hit **Save note**. Both the rating and the note are stored with the run and visible in the History tab.

Every run saves automatically in the background. You don't need to do anything.

### Token Highlights

Below the input box there's a **Show Token Highlights** button. Click it and each token in your input gets rendered as a colour-coded chip — useful for seeing exactly where your budget is going. The panel updates live as you type. Click again to hide it.

### Switching the compression model

Click **Model Settings** at the top of the tab to expand the accordion. Pick a model from the dropdown (or type a custom HuggingFace model ID) and hit **Load Model**. The current model is unloaded from memory first, then the new one loads — no restart needed. The status box confirms when it's ready.

Available presets: Qwen2.5-1.5B-Instruct (default), Qwen2.5-0.5B-Instruct, SmolLM2-1.7B-Instruct, Phi-3.5-mini-instruct, Llama-3.2-1B-Instruct.

### Switching the scoring embedder

Below the compression model section in the same accordion, there's a separate **Embedder Model** dropdown. The embedder is what computes the quality score — changing it affects how accurately that score reflects meaning retention.

When you select a model from the dropdown, an info panel updates immediately to explain the trade-off:
- ⚡ **Fast** models (MiniLM, bge-small) — low overhead, good baseline scores, CPU-friendly
- ⚖️ **Balanced** models (mpnet, bge-base) — more discriminating scores, small speed cost
- 🏆 **High quality** models (mxbai-large) — most accurate scores, GPU recommended
- 🔬 **Best quality** models (gte-Qwen2-1.5B) — catches subtle meaning loss, requires significant RAM/VRAM

Hit **Load Embedder** to apply the selection. The previous embedder is unloaded from memory before the new one loads.

## History tab

Click over here to see everything that's been compressed so far.

The table loads automatically when you open the tab. Hit **Refresh** to pull in the latest runs. At the top you'll find the average quality score and compression ratio across all sessions — a quick way to see how the tool is performing over time.

### Column visibility

By default the table shows: `id`, `timestamp`, `model`, `compression_ratio`, `quality_score`, `feedback`. Open the **Column visibility** accordion above the table to toggle any additional columns on or off — changes apply instantly without a refresh.

### Side-by-side diff

Click any row in the table and a word-level diff panel opens below it. Words are colour-coded:
- Red strikethrough — dropped from the original
- Amber — rewritten by the model
- Green — inserted (rare connector words)
- Plain — survived unchanged

### Deleting a run

Click a row to select it, then hit **Delete Selected Row**. The table refreshes and the aggregate stats update automatically.


🏠 [README.md](../README.md)
