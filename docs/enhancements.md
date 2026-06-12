# Enhancements

The hackathon MVP covers the core loop well. Here's where it could go next.

## Quick wins

- **Batch compression** — let users paste multiple texts and compress them all at once
- **Export history** — download past runs as a CSV straight from the History tab
- **Named presets** — save favourite token budget + model combinations and reuse them
- **`.env` support** — load config from a `.env` file instead of setting env vars manually

## Worth building next

- **Iterative compression** — if the quality score drops below a threshold, automatically retry with a slightly relaxed budget
- **Custom focus instructions** — let the user say "keep all numbers" or "preserve action items only" before compressing
- **Chunked compression** — handle inputs that exceed the model's context window by splitting, compressing each chunk, then merging
- **REST API** — a simple `/compress` endpoint via Flask so other tools can call TinyPress programmatically

## Longer term

- **VS Code extension** — compress selected text without leaving the editor
- **CLI tool** — `tinypress compress --budget 500 input.txt` for terminal users
- **Hosted version** — a SaaS wrapper with usage tracking and team history
- **Domain-specific fine-tuning** — train a compressor specialised for legal, medical, or code content


🏠 [README.md](../README.md)
