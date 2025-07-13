"""
Связка:
  1. Whisper‑small (русский ASR)          – faster‑whisper
  2. CTranslate2 RU→EN                    – int8
  3. Florence‑2‑base (8‑bit)              – grounding / OD

Все модели лежат в каталоге ../models и загружаются локально
"""

from pathlib import Path
from typing import List, Tuple
from PIL import Image
import torch
from transformers import (
    AutoProcessor,
    AutoModelForCausalLM,
    AutoTokenizer,
)
from faster_whisper import WhisperModel
from ctranslate2 import Translator
from .utils import draw_boxes

# ──────────────────────────────────────────────────────────────────────────
# Общие переменные

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float32

# ──────────────────────────────────────────────────────────────────────────
# Florence‑2

FLORENCE_ID = str(MODELS_DIR / "florence-2-base-int8")  # локальный путь
fl_processor = AutoProcessor.from_pretrained(FLORENCE_ID, trust_remote_code=True)
fl_model = AutoModelForCausalLM.from_pretrained(
    FLORENCE_ID,
    torch_dtype=DTYPE,
    trust_remote_code=True,
    device_map={"": DEVICE},
    #load_in_8bit=True,
)

def detect(image: Image.Image, phrase: str, mode: str = "grounding"):
    """
    Возвращает список bbox [(x1,y1,x2,y2)…].
    mode = "grounding" / "od"
    """
    prompt = "<CAPTION_TO_PHRASE_GROUNDING>" + phrase if mode == "grounding" else "<OD>"
    inputs = fl_processor(text=prompt, images=image, return_tensors="pt")
    for k in inputs:
        if hasattr(inputs[k], "to"):
            inputs[k] = inputs[k].to(DEVICE)
    ids = fl_model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=512,
        num_beams=1,
    )
    text_out = fl_processor.batch_decode(ids, skip_special_tokens=False)[0]
    parsed = fl_processor.post_process_generation(
        text_out,
        task="<CAPTION_TO_PHRASE_GROUNDING>" if mode == "grounding" else "<OD>",
        image_size=image.size,
    )
    if mode == "grounding":
        return parsed["<CAPTION_TO_PHRASE_GROUNDING>"]["bboxes"]
    bbs = parsed["<OD>"]["bboxes"]
    labels = parsed["<OD>"]["labels"]
    return [bb for bb, lbl in zip(bbs, labels) if lbl.lower() == "cat"]

# ──────────────────────────────────────────────────────────────────────────
# ASR

ASR_DIR = str(MODELS_DIR / "whisper-small")
asr_model = WhisperModel(
    ASR_DIR,
    device=DEVICE,
    compute_type="float16" if DEVICE == "cuda" else "int8",
    cpu_threads=4,
)

def transcribe_ru(wav_path: Path) -> str:
    segments, _ = asr_model.transcribe(
        str(wav_path),
        language="ru",
        beam_size=5,
        vad_filter=True,
    )
    return " ".join(s.text.strip() for s in segments)

# ──────────────────────────────────────────────────────────────────────────
# MT Ru→En

MT_DIR = str(MODELS_DIR / "ru-en-int8")
mt_translator = Translator(
    MT_DIR,
    device=DEVICE,
    compute_type="float16" if DEVICE == "cuda" else "int8"
)
mt_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ru-en")

def ru2en(text: str) -> str:
    ids = mt_tokenizer.encode(text, add_special_tokens=True)
    toks = mt_tokenizer.convert_ids_to_tokens(ids)
    out = mt_translator.translate_batch([toks], beam_size=1, return_scores=False)[0]
    hyp = out.hypotheses[0]
    return mt_tokenizer.convert_tokens_to_string(hyp).strip()

# ──────────────────────────────────────────────────────────────────────────
# Public pipeline

def run_pipeline(audio_path: Path, image_path: Path, mode="grounding"):
    ru_text = transcribe_ru(audio_path)
    phrase = ru2en(ru_text)
    img = Image.open(image_path).convert("RGB")
    matches = detect(img, phrase, mode)
    boxed = draw_boxes(img, matches, label=ru_text)
    return boxed, matches
