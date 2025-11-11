# src/summarize.py
from transformers import pipeline
from src.config import SUM_MODEL

# Streamlit cache if available; fallback to plain function
try:
    import streamlit as st
    cache_resource = st.cache_resource
except Exception:
    def cache_resource(func):  # no-op fallback
        return func

@cache_resource
def get_summarizer():
    # Cloud usually runs CPU
    return pipeline("summarization", model=SUM_MODEL, device=-1)

def summarize_text(text: str, max_tokens=220, min_tokens=60) -> str:
    if not text:
        return ""
    summarizer = get_summarizer()
    max_len = 1024
    text = text[: max_len*2]
    out = summarizer(
        text, max_length=max_tokens, min_length=min_tokens,
        do_sample=False, truncation=True
    )[0]["summary_text"]
    return out.strip()

def summarize_article(title: str, text: str) -> str:
    lead = f"Title: {title}\n\n"
    return lead + summarize_text(text)
