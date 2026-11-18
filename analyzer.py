import re
from collections import Counter
from io import BytesIO
import fitz  # PyMuPDF

# Small built-in English stop-word list; this is rule-based, not machine learning.
STOP_WORDS = set("""
a an the and or but if then else when at by for from in into on onto of off out over under
to up with without is am are was were be been being do does did have has had can could will
would shall should may might must this that these those it its as not no nor so than too very
i me my we our you your he she they them their what which who whom where why how all any both
each few more most other some such only own same also just about after before between during
through because while again further once here there
""".split())

def extract_text(file_bytes: bytes, filename: str) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "txt":
        # Try common encodings for text files.
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("The text file encoding could not be identified.")
    if suffix == "pdf":
        try:
            with fitz.open(stream=BytesIO(file_bytes), filetype="pdf") as doc:
                return "\n\n".join(page.get_text("text") for page in doc)
        except Exception as exc:
            raise ValueError("The PDF may be damaged or password-protected.") from exc
    raise ValueError("Unsupported file type. Upload a PDF or TXT file.")

def analyze_document(text: str) -> dict:
    words = re.findall(r"\b[\w'-]+\b", text.lower(), flags=re.UNICODE)
    meaningful = [
        word.strip("'-_")
        for word in words
        if len(word.strip("'-_")) > 1 and word.strip("'-_") not in STOP_WORDS
        and not word.strip("'-_").isdigit()
    ]
    meaningful = [word for word in meaningful if word]
    frequencies = Counter(meaningful)
    keywords = frequencies.most_common(10)

    # Approximate sentence count; avoid counting empty punctuation-only text.
    sentence_parts = re.split(r"[.!?]+(?:\s|$)", text.strip())
    sentence_count = sum(1 for part in sentence_parts if part.strip())
    paragraphs = [part for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]
    word_count = len(words)
    return {
        "word_count": word_count,
        "character_count": len(text),
        "sentence_count": sentence_count,
        "paragraph_count": len(paragraphs),
        "reading_minutes": max(1, round(word_count / 200)),
        "keywords": keywords,
    }
