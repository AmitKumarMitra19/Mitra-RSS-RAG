from src.config import SUM_MODEL
import os

USE_FALLBACK = os.getenv("DISABLE_SUMMARIZER", "0").lower() in ("1","true","yes")

if not USE_FALLBACK:
    from transformers import pipeline
    try:
        import streamlit as st
        cache_resource = st.cache_resource
    except Exception:
        def cache_resource(f): return f

    @cache_resource
    def get_summarizer():
        return pipeline("summarization", model=SUM_MODEL, device=-1)

def summarize_text(text: str, max_tokens=220, min_tokens=60) -> str:
    if not text:
        return ""
    if USE_FALLBACK:
        # simple extractive fallback: first ~4 sentences or ~700 chars
        import re
        sents = re.split(r'(?<=[.!?])\s+', text.strip())
        out = " ".join(sents[:4])[:700]
        return out
    summarizer = get_summarizer()
    text = text[:2048]
    out = summarizer(text, max_length=max_tokens, min_length=min_tokens, do_sample=False, truncation=True)[0]["summary_text"]
    return out.strip()

def summarize_article(title: str, text: str) -> str:
    lead = f"Title: {title}\n\n"
    return lead + summarize_text(text)
