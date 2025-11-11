# src/summarize.py
import os, re
from src.config import SUM_MODEL, DISABLE_SUMMARIZER

if not DISABLE_SUMMARIZER:
    try:
        from transformers import pipeline
        import streamlit as st
        @st.cache_resource
        def get_summarizer():
            return pipeline("summarization", model=SUM_MODEL, device=-1)
    except Exception:
        # If transformers fails, fallback to simple mode
        os.environ["DISABLE_SUMMARIZER"] = "1"
        DISABLE_SUMMARIZER = True

def _simple_summary(text: str, limit_chars=600):
    # Extractive fallback: first ~4 sentences / limit chars
    sents = re.split(r'(?<=[.!?])\s+', (text or "").strip())
    return (" ".join(sents[:4])[:limit_chars]).strip()

def summarize_text(text: str, max_tokens=220, min_tokens=60) -> str:
    if not text: return ""
    if DISABLE_SUMMARIZER:
        return _simple_summary(text)
    summarizer = get_summarizer()
    text = text[:2048]
    return summarizer(text, max_length=max_tokens, min_length=min_tokens,
                      do_sample=False, truncation=True)[0]["summary_text"].strip()

def summarize_article(title: str, text: str) -> str:
    lead = f"Title: {title}\n\n"
    return lead + summarize_text(text)
