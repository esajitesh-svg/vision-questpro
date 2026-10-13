"""Small cloud-hosted image understanding through Transformers and SmolVLM."""
from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
import time
from PIL import Image, ImageOps, UnidentifiedImageError

MODEL_ID = "HuggingFaceTB/SmolVLM-256M-Instruct"
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MODES: dict[str, str] = {
    "scene": "Describe the visible scene in 2–4 concise sentences. Mention only clearly visible objects, actions, and setting.",
    "objects": "List clearly visible objects and say where each appears in the frame (left, center, right, foreground, or background). Do not invent unseen objects.",
    "read_text": "Transcribe only text that is visibly readable in the image. Preserve wording. Mark uncertain text as [unclear]. Do not invent missing words.",
    "accessibility": "Give a calm spoken-style description in no more than 35 words. Prioritize important visible details. Do not infer identity or personal circumstances.",
    "visual_question": "Answer the user's question using only evidence from the image. If it cannot be determined, say so clearly.",
}
MODE_LABELS = {"scene": "Scene overview", "objects": "Find and locate objects", "read_text": "Read visible text", "accessibility": "Short spoken description", "visual_question": "Ask a question about the image"}

@dataclass(frozen=True)
class VisionResult:
    text: str
    model: str
    elapsed_seconds: float
    original_size: tuple[int, int]
    processed_size: tuple[int, int]


def prepare_image(image_bytes: bytes, max_side: int = 512) -> tuple[Image.Image, tuple[int, int]]:
    if not image_bytes:
        raise ValueError("Choose an image first.")
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("Image is larger than 8 MB. Resize it or choose another image.")
    try:
        image = Image.open(BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image).convert("RGB")
        original_size = image.size
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        return image, original_size
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("This file is not a valid supported image. Try a JPG or PNG image.") from exc


def build_prompt(mode: str, focus: str = "") -> str:
    task = MODES.get(mode, MODES["scene"])
    prompt = (
        "You are VisionQuest, a cautious visual assistant. Report only what the image supports. "
        "Do not identify a person, infer a relationship, diagnose a health condition, or guess emotions or personal history. "
        "If unsure, say what is uncertain. Do not greet the user or give generic advice.\n\nTask: " + task
    )
    if focus.strip():
        prompt += "\n\nUser question/focus: " + focus.strip()[:300]
    prompt += "\n\nKeep the answer concise and directly about this image."
    return prompt


def model_status() -> tuple[bool, str]:
    return True, "Cloud model loads on first analysis; no local Ollama installation required."


def _load_model():
    import torch
    from transformers import AutoModelForVision2Seq, AutoProcessor
    torch.set_num_threads(min(2, os_cpu_count()))
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForVision2Seq.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        attn_implementation="eager",
    )
    model.eval()
    return processor, model


def os_cpu_count() -> int:
    import os
    return os.cpu_count() or 1


def analyze_image(image_bytes: bytes, mode: str = "scene", focus: str = "", max_side: int = 512) -> VisionResult:
    from functools import lru_cache
    import torch
    image, original_size = prepare_image(image_bytes, max_side=max_side)
    # Streamlit runtime offers per-process caching; this fallback keeps module standalone-testable.
    try:
        import streamlit as st
        processor, model = _cached_model()
    except ImportError:
        processor, model = _load_model()
    chat = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": build_prompt(mode, focus)}]}]
    prompt = processor.apply_chat_template(chat, add_generation_prompt=True)
    inputs = processor(text=prompt, images=[image], return_tensors="pt")
    started = time.perf_counter()
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=96, do_sample=False, num_beams=1)
    new_tokens = generated_ids[:, inputs["input_ids"].shape[1]:]
    answer = processor.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
    elapsed = round(time.perf_counter() - started, 2)
    if not answer:
        raise RuntimeError("The vision model returned an empty answer. Try another image or retry once.")
    if len(answer) > 6000:
        answer = answer[:6000].rsplit(" ", 1)[0] + "…"
    return VisionResult(answer, MODEL_ID, elapsed, original_size, image.size)


def _cached_model():
    import streamlit as st
    # Define the cached loader at module scope so Streamlit can reuse one model
    # instance across reruns instead of loading a fresh model each time.
    global _MODEL_CACHE_LOADER
    try:
        loader = _MODEL_CACHE_LOADER
    except NameError:
        @st.cache_resource(show_spinner=False)
        def load_once():
            return _load_model()
        _MODEL_CACHE_LOADER = load_once
        loader = _MODEL_CACHE_LOADER
    return loader()
