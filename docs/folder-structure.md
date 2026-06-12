# Folder Structure

```
app/
├── app.py                        # Entry point
├── config.py                      # All tunable settings
├── requirements.txt               # Pinned Python dependencies
├── tinypress.db                   # SQLite DB (auto-created on first run)
│
├── ui/
│   ├── compress_tab.py            # Compression UI tab
│   └── history_tab.py             # Metrics history tab
│
├── core/
│   ├── compressor.py              # Compression pipeline logic
│   ├── scorer.py                  # Semantic similarity scoring
│   ├── tokenizer_utils.py         # Token counting helpers
│   └── diff.py                    # Word-level diff + HTML renderer for history view
│
├── models/
│   └── model_loader.py            # Lazy model + embedder loading
│
├── db/
│   ├── schema.sql                 # SQLite table definitions
│   └── store.py                   # DB read/write operations
│
├── docs/                          # Project documentation
│   ├── architecture.md
│   ├── folder-structure.md
│   ├── setup.md
│   ├── get-started.md
│   └── enhancements.md
│
├── my-notes/                      # Planning notes (not part of the app)
│   └── overall-idea.md
│
└── claude-grounding/              # Context files for Claude (not part of the app)
    ├── hackathon.md
    ├── tech-stack.md
    └── about-me.md
```


🏠 [README.md](../README.md)
