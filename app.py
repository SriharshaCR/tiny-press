import gradio as gr
import config
from models.model_loader import get_llm, get_embedder
from ui.compress_tab import build_compress_tab
from ui.history_tab import build_history_tab


def build_app() -> gr.Blocks:
    with gr.Blocks(title=config.APP_TITLE) as app:
        build_compress_tab()
        build_history_tab()
    return app


if __name__ == "__main__":
    print("Loading models (first run may download weights)...")
    get_llm()
    get_embedder()

    print("Starting TinyPress...")
    app = build_app()
    app.launch(server_port=config.SERVER_PORT)
