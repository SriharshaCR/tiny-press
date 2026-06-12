import html as _h
import time
from datetime import datetime, timezone

import gradio as gr

import config
from core.compressor import compress
from core.scorer import semantic_score
from core.tokenizer_utils import count_tokens, get_token_strings
from db.store import save_run, update_feedback, update_feedback_comment
from models.model_loader import get_current_model_id, get_current_tokenizer_id, switch_llm, switch_embedder, get_current_embedder_id

# ── token colour palette (10 soft pastels, cycles) ───────────────────────────

_PALETTE = [
    "#fde68a",  # amber
    "#bbf7d0",  # emerald
    "#bfdbfe",  # sky-blue
    "#fecaca",  # rose
    "#e9d5ff",  # violet
    "#fed7aa",  # orange
    "#99f6e4",  # teal
    "#e0e7ff",  # indigo
    "#fce7f3",  # pink
    "#d1fae5",  # green
]

_BTN_SHOW = "🔍  Show Token Highlights"
_BTN_HIDE = "🙈  Hide Token Highlights"


# ── token visualiser ─────────────────────────────────────────────────────────

def _render_token_html(text: str) -> str:
    if not text.strip():
        return ""
    tokens = get_token_strings(text)
    if not tokens:
        return ""

    spans = []
    for i, tok in enumerate(tokens):
        color = _PALETTE[i % len(_PALETTE)]
        # Make leading whitespace visible with a mid-dot; escape everything else.
        display = _h.escape(tok).replace(
            " ", '<span style="opacity:0.35;font-size:0.7em">·</span>'
        )
        spans.append(
            f'<span title="token {i + 1} · id" '
            f'style="background:{color};border-radius:4px;padding:2px 5px;'
            f'font-family:\'Courier New\',monospace;font-size:0.8rem;'
            f'line-height:2.2;margin:2px 1px;display:inline-block;'
            f'cursor:default;border:1px solid rgba(0,0,0,0.06)">{display}</span>'
        )

    return (
        '<div style="font-family:system-ui,sans-serif;padding:10px 12px;'
        'border:1px solid #e5e7eb;border-radius:8px;background:#fafafa">'
        f'<div style="font-size:0.75rem;color:#6b7280;margin-bottom:8px;font-weight:500">'
        f'{len(tokens)} tokens — each chip = one token, hover for index</div>'
        '<div style="line-height:2.6;word-break:break-all;'
        'max-height:200px;overflow-y:auto">'
        + "".join(spans)
        + "</div></div>"
    )


# ── toggle handler ────────────────────────────────────────────────────────────

def toggle_token_panel(is_visible: bool, text: str):
    new_visible = not is_visible
    html_content = _render_token_html(text) if new_visible else ""
    btn_label = _BTN_HIDE if new_visible else _BTN_SHOW
    return new_visible, html_content, gr.update(value=btn_label)


def update_token_panel(text: str, is_visible: bool) -> str:
    """Called on every keystroke — only re-renders when the panel is open."""
    if not is_visible:
        return ""
    return _render_token_html(text)


# ── compression status banner ─────────────────────────────────────────────────

_STATUS_EMPTY = "<span></span>"
_STATUS_RED = (
    '<div style="background:#fee2e2;border:1px solid #ef4444;color:#b91c1c;'
    'padding:8px 12px;border-radius:6px;font-size:0.9rem;">'
    "🔴 <strong>Compression not needed</strong> — input ({input_tok} tokens) "
    "is already within the {budget}-token budget."
    "</div>"
)
_STATUS_GREEN = (
    '<div style="background:#dcfce7;border:1px solid #22c55e;color:#15803d;'
    'padding:8px 12px;border-radius:6px;font-size:0.9rem;">'
    "🟢 <strong>Ready to compress</strong> — {input_tok} tokens → {budget} token budget "
    "({delta} tokens to shed)."
    "</div>"
)


def compression_status(text: str, target_tokens: int) -> str:
    if not text.strip():
        return _STATUS_EMPTY
    n = count_tokens(text)
    if n <= int(target_tokens):
        return _STATUS_RED.format(input_tok=n, budget=int(target_tokens))
    return _STATUS_GREEN.format(input_tok=n, budget=int(target_tokens), delta=n - int(target_tokens))


# ── core handlers ─────────────────────────────────────────────────────────────

def run_compression(text: str, target_tokens: int):
    _hidden = gr.update(visible=False)
    if not text.strip():
        return ("", 0, 0, 0, 0.0, None,
                _hidden, _hidden, gr.update(value="", visible=False),
                gr.update(value="", visible=False), _hidden, gr.update(value="", visible=False))

    t0 = time.perf_counter()
    compressed, input_tokens, output_tokens = compress(text, int(target_tokens))
    duration_ms = round((time.perf_counter() - t0) * 1000, 1)

    ratio = round(output_tokens / input_tokens, 4) if input_tokens else 0.0
    quality = semantic_score(text, compressed)

    run_id = save_run({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": get_current_model_id() or config.LLM_MODEL,
        "tokenizer": get_current_tokenizer_id() or config.LLM_MODEL,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "target_tokens": int(target_tokens),
        "compression_ratio": ratio,
        "quality_score": quality,
        "duration_ms": duration_ms,
        "input_text": text,
        "output_text": compressed,
    })

    return (
        compressed, input_tokens, output_tokens, ratio, quality,
        run_id,
        gr.update(visible=True), gr.update(visible=True),    # thumbs buttons
        gr.update(value="", visible=True),                    # feedback_status
        gr.update(value="", visible=False),                   # comment_box reset
        gr.update(visible=False),                             # save_comment_btn reset
        gr.update(value="", visible=False),                   # comment_saved reset
    )


def load_model(model_id: str) -> str:
    if not model_id:
        return "No model selected."
    try:
        return switch_llm(model_id)
    except Exception as exc:
        return f"Error loading {model_id}: {exc}"


def load_embedder(model_id: str) -> str:
    if not model_id:
        return "No model selected."
    try:
        return switch_embedder(model_id)
    except Exception as exc:
        return f"Error loading {model_id}: {exc}"


def on_embedder_change(model_id: str) -> str:
    return config.EMBEDDER_INFO.get(model_id, "")


def submit_feedback(run_id, value: int):
    if run_id is None:
        return "Run a compression first.", gr.update(visible=False), gr.update(visible=False), gr.update(value="", visible=False)
    update_feedback(run_id, value)
    msg = "👍 Marked as helpful — thanks!" if value == 1 else "👎 Noted — thanks for the feedback!"
    return msg, gr.update(visible=True), gr.update(visible=True), gr.update(value="", visible=False)


def save_comment(run_id, comment: str):
    if run_id is None:
        return gr.update(value="Run a compression first.", visible=True)
    if not comment.strip():
        return gr.update(value="Type a note first.", visible=True)
    update_feedback_comment(run_id, comment.strip())
    return gr.update(value="✓ Note saved.", visible=True)


# ── UI ────────────────────────────────────────────────────────────────────────

def build_compress_tab() -> gr.Tab:
    with gr.Tab("Compress") as tab:
        gr.Markdown("## TinyPress — Prompt Compression Engine")
        gr.Markdown(
            "Paste any long text. Set your token budget. Get a compressed version "
            "that preserves intent — scored for quality."
        )

        with gr.Accordion("Model Settings", open=False):
            gr.Markdown("**Compression Model**")
            model_dropdown = gr.Dropdown(
                choices=config.AVAILABLE_MODELS,
                value=config.LLM_MODEL,
                label="Compression Model",
                allow_custom_value=True,
            )
            load_model_btn = gr.Button("Load Model", variant="secondary")
            model_status = gr.Textbox(
                label="Model Status",
                value=f"Active: {config.LLM_MODEL}",
                interactive=False,
            )

            gr.Divider()

            gr.Markdown("**Scoring Embedder**")
            embedder_dropdown = gr.Dropdown(
                choices=config.AVAILABLE_EMBEDDER_MODELS,
                value=config.EMBEDDER_MODEL,
                label="Embedder Model",
                allow_custom_value=True,
            )
            embedder_info_panel = gr.Markdown(
                value=config.EMBEDDER_INFO.get(config.EMBEDDER_MODEL, "")
            )
            load_embedder_btn = gr.Button("Load Embedder", variant="secondary")
            embedder_status = gr.Textbox(
                label="Embedder Status",
                value=f"Active: {config.EMBEDDER_MODEL}",
                interactive=False,
            )

        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    label="Input Text",
                    lines=12,
                    placeholder="Paste your text here...",
                )

                # ── token highlight panel ──────────────────────────────────
                token_toggle_btn = gr.Button(_BTN_SHOW, variant="secondary", size="sm")
                token_panel = gr.HTML(value="")
                tokens_visible = gr.State(value=False)
                # ──────────────────────────────────────────────────────────

                target_slider = gr.Slider(
                    minimum=100,
                    maximum=1000,
                    value=config.DEFAULT_TARGET_TOKENS,
                    step=50,
                    label="Target Token Budget",
                )
                status_banner = gr.HTML(value=_STATUS_EMPTY)
                compress_btn = gr.Button("Compress", variant="primary")

            with gr.Column():
                output_text = gr.Textbox(label="Compressed Output", lines=12)
                with gr.Row():
                    input_tok = gr.Number(label="Input Tokens", interactive=False)
                    output_tok = gr.Number(label="Output Tokens", interactive=False)
                with gr.Row():
                    ratio = gr.Number(label="Compression Ratio", interactive=False)
                    quality = gr.Number(label="Quality Score (0–1)", interactive=False)
                gr.Markdown("**Was this compression helpful?**")
                with gr.Row():
                    thumbs_up_btn   = gr.Button("👍  Helpful",      variant="secondary", visible=False, scale=1)
                    thumbs_down_btn = gr.Button("👎  Not helpful",  variant="secondary", visible=False, scale=1)
                feedback_status = gr.Markdown("", visible=False)
                comment_box = gr.Textbox(
                    label="Add a note (optional)",
                    placeholder="e.g. 'lost key dates', 'too short', 'great summary'",
                    lines=2,
                    visible=False,
                )
                save_comment_btn = gr.Button("Save note", variant="secondary", size="sm", visible=False)
                comment_saved = gr.Markdown("", visible=False)

        last_run_id = gr.State(value=None)

        # ── event wiring ──────────────────────────────────────────────────
        token_toggle_btn.click(
            fn=toggle_token_panel,
            inputs=[tokens_visible, input_text],
            outputs=[tokens_visible, token_panel, token_toggle_btn],
        )
        input_text.change(
            fn=update_token_panel,
            inputs=[input_text, tokens_visible],
            outputs=[token_panel],
        )

        _status_args = dict(inputs=[input_text, target_slider], outputs=[status_banner])
        input_text.change(fn=compression_status, **_status_args)
        target_slider.change(fn=compression_status, **_status_args)

        load_model_btn.click(fn=load_model, inputs=[model_dropdown], outputs=[model_status])
        embedder_dropdown.change(fn=on_embedder_change, inputs=[embedder_dropdown], outputs=[embedder_info_panel])
        load_embedder_btn.click(fn=load_embedder, inputs=[embedder_dropdown], outputs=[embedder_status])
        compress_btn.click(
            fn=run_compression,
            inputs=[input_text, target_slider],
            outputs=[output_text, input_tok, output_tok, ratio, quality,
                     last_run_id, thumbs_up_btn, thumbs_down_btn, feedback_status,
                     comment_box, save_comment_btn, comment_saved],
        )
        thumbs_up_btn.click(
            fn=lambda run_id: submit_feedback(run_id, 1),
            inputs=[last_run_id],
            outputs=[feedback_status, comment_box, save_comment_btn, comment_saved],
        )
        thumbs_down_btn.click(
            fn=lambda run_id: submit_feedback(run_id, -1),
            inputs=[last_run_id],
            outputs=[feedback_status, comment_box, save_comment_btn, comment_saved],
        )
        save_comment_btn.click(
            fn=save_comment,
            inputs=[last_run_id, comment_box],
            outputs=[comment_saved],
        )

    return tab
