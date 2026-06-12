import gradio as gr
import pandas as pd
from db.store import get_runs, delete_run, get_run
from core.diff import render_diff_html

_DEFAULT_COLS = ["id", "timestamp", "model", "compression_ratio", "quality_score", "feedback"]
_ALL_COLS = [
    "id", "timestamp", "model", "tokenizer",
    "input_tokens", "output_tokens", "target_tokens",
    "compression_ratio", "quality_score", "duration_ms",
    "feedback", "feedback_comment",
]


def load_history(selected_cols=None):
    cols = selected_cols if selected_cols else _DEFAULT_COLS
    runs = get_runs(limit=100)
    if not runs:
        return pd.DataFrame(columns=cols), "", "", ""
    df = pd.DataFrame(runs)
    existing = [c for c in cols if c in df.columns]
    df = df[existing]
    avg_quality = f"{df['quality_score'].mean():.4f}" if "quality_score" in df.columns else "—"
    avg_ratio = f"{df['compression_ratio'].mean():.4f}" if "compression_ratio" in df.columns else "—"
    return df, avg_quality, avg_ratio, ""


def on_row_select(evt: gr.SelectData, df: pd.DataFrame):
    if df is None or df.empty:
        return None, "", "No rows available."
    row_idx = evt.index[0]
    run_id = int(df.iloc[row_idx]["id"])
    record = get_run(run_id)
    if not record:
        return None, "", f"Row {run_id} not found in database."
    diff_html = render_diff_html(record)
    return run_id, diff_html, f"Row {run_id} selected — click Delete to remove."


def delete_selected(run_id, selected_cols):
    if run_id is None:
        df, avg_q, avg_r, _ = load_history(selected_cols)
        return df, avg_q, avg_r, None, "", "No row selected."
    delete_run(run_id)
    df, avg_q, avg_r, _ = load_history(selected_cols)
    return df, avg_q, avg_r, None, "", f"Row {run_id} deleted."


def build_history_tab() -> gr.Tab:
    with gr.Tab("History") as tab:
        gr.Markdown("## Compression Run History")
        gr.HTML(
            '<div style="background:#fef9c3;border:1px solid #f59e0b;color:#92400e;'
            'padding:8px 14px;border-radius:6px;font-size:0.875rem;margin-bottom:4px">'
            '⚠️ <strong>Session only</strong> — history lives in memory and will be lost '
            'when this session ends. There is no persistent storage.'
            '</div>'
        )

        with gr.Row():
            refresh_btn = gr.Button("Refresh", variant="secondary")
            delete_btn  = gr.Button("Delete Selected Row", variant="stop")

        with gr.Accordion("Column visibility", open=False):
            col_picker = gr.CheckboxGroup(
                choices=_ALL_COLS,
                value=_DEFAULT_COLS,
                label=None,
            )

        with gr.Row():
            avg_quality = gr.Textbox(label="Avg Quality Score",     interactive=False)
            avg_ratio   = gr.Textbox(label="Avg Compression Ratio", interactive=False)

        history_table = gr.DataFrame(
            label="Past Runs — click a row to see its diff",
            interactive=False,
        )
        delete_status = gr.Textbox(
            label="Status", value="Click a row to select it.", interactive=False
        )

        gr.Markdown("### Side-by-side Diff")
        diff_panel  = gr.HTML(value="")
        selected_id = gr.State(value=None)

        _outputs = [history_table, avg_quality, avg_ratio, diff_panel]

        refresh_btn.click(fn=load_history, inputs=[col_picker], outputs=_outputs)
        tab.select(fn=load_history, inputs=[col_picker], outputs=_outputs)
        col_picker.change(fn=load_history, inputs=[col_picker], outputs=_outputs)
        history_table.select(
            fn=on_row_select,
            inputs=[history_table],
            outputs=[selected_id, diff_panel, delete_status],
        )
        delete_btn.click(
            fn=delete_selected,
            inputs=[selected_id, col_picker],
            outputs=[history_table, avg_quality, avg_ratio, selected_id, diff_panel, delete_status],
        )

    return tab
