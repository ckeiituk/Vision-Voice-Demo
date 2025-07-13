"""
Gradio‑веб‑интерфейс.
"""

from pathlib import Path
import gradio as gr
from .pipeline import run_pipeline

def inference(audio, image):
    boxed, _ = run_pipeline(Path(audio), Path(image))
    return boxed

demo = gr.Interface(
    fn=inference,
    inputs=[
        gr.Audio(type="filepath", label="Русская голосовая команда (MP3/WAV)"),
        gr.Image(type="filepath", label="Картинка"),
    ],
    outputs=gr.Image(label="Результат detections"),
    title="Vision‑Voice Demo (CPU‑only)",
)

if __name__ == "__main__":
    demo.launch(share=True,server_name="0.0.0.0", server_port=7860)
