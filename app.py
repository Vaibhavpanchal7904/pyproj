import streamlit as st
import pandas as pd
import re
from pathlib import Path
from analyzer import analyze_document, extract_text
from database import init_db, save_analysis, get_history, delete_history

st.set_page_config(page_title="DocuSense | Document Analyzer", page_icon="📄", layout="wide")
init_db()

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#102a43,#176b72); color:white; margin-bottom:1.2rem;}
.hero h1 {margin:0; color:white; font-size:2.2rem;}
.hero p {margin:.4rem 0 0; color:#e4f4f4;}
.small-muted {color: #64748b; font-size: .9rem;}
</style>
<div class="hero">
<h1>📄 DocuSense</h1>
<p>Smart Document Analyzer · Extract, explore, and understand your documents.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Analyze Document", "Analysis History", "About"])
    st.divider()
    st.caption("Files are processed by this app. Avoid uploading confidential documents to a shared deployment.")

if page == "Analyze Document":
    st.subheader("Upload a document")
    uploaded = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    if uploaded:
        max_bytes = 15 * 1024 * 1024
        if uploaded.size > max_bytes:
            st.error("File is too large. Please upload a file smaller than 15 MB.")
            st.stop()
        raw = uploaded.getvalue()
        try:
            extracted_text = extract_text(raw, uploaded.name)
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")
            st.stop()

        if not extracted_text.strip():
            st.warning("No readable text was found. If this is a scanned PDF, OCR is required; OCR is not included in this version.")
            st.stop()

        result = analyze_document(extracted_text)
        st.success(f"Successfully analyzed **{uploaded.name}**")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Words", f"{result['word_count']:,}")
        c2.metric("Characters", f"{result['character_count']:,}")
        c3.metric("Sentences", f"{result['sentence_count']:,}")
        c4.metric("Paragraphs", f"{result['paragraph_count']:,}")
        c5.metric("Reading time", f"{result['reading_minutes']} min")

        left, right = st.columns([1, 1])
        with left:
            st.subheader("Top keywords")
            if result["keywords"]:
                keyword_df = pd.DataFrame(result["keywords"], columns=["Keyword", "Frequency"])
                st.bar_chart(keyword_df.set_index("Keyword"))
                st.dataframe(keyword_df, use_container_width=True, hide_index=True)
            else:
                st.info("Not enough meaningful words to display keyword frequencies.")
        with right:
            st.subheader("Find a word or phrase")
            query = st.text_input("Search within extracted text", placeholder="e.g. Python")
            if query:
                count = len(re.findall(re.escape(query), extracted_text, flags=re.IGNORECASE))
                st.write(f"Found **{count}** occurrence(s).")
                # Escape HTML before adding safe highlighting.
                import html
                safe_text = html.escape(extracted_text)
                pattern = re.compile(re.escape(query), re.IGNORECASE)
                safe_text = pattern.sub(lambda m: f'<mark>{m.group(0)}</mark>', safe_text)
                st.markdown(
                    f'<div style="max-height:320px;overflow:auto;white-space:pre-wrap;border:1px solid #ddd;padding:12px;border-radius:8px">{safe_text}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.caption("Enter a phrase to highlight its matches in the text.")

        with st.expander("Preview extracted text"):
            st.text_area("Extracted content", extracted_text[:20000], height=260, disabled=True)
            if len(extracted_text) > 20000:
                st.caption("Preview limited to the first 20,000 characters.")

        report = [
            "DocuSense Analysis Report",
            f"Filename: {Path(uploaded.name).name}",
            f"Words: {result['word_count']}",
            f"Characters: {result['character_count']}",
            f"Sentences: {result['sentence_count']}",
            f"Paragraphs: {result['paragraph_count']}",
            f"Estimated reading time: {result['reading_minutes']} minute(s)",
            "",
            "Top keywords:",
            *[f"{word}: {count}" for word, count in result["keywords"]],
        ]
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button("⬇ Download TXT report", "\n".join(report), file_name="docusense_report.txt", mime="text/plain", use_container_width=True)
        with col_b:
            keyword_csv = pd.DataFrame(result["keywords"], columns=["Keyword", "Frequency"]).to_csv(index=False)
            st.download_button("⬇ Download keyword CSV", keyword_csv, file_name="docusense_keywords.csv", mime="text/csv", use_container_width=True)

        if st.button("Save analysis to history", type="primary"):
            save_analysis(
                filename=Path(uploaded.name).name,
                word_count=result["word_count"],
                character_count=result["character_count"],
                sentence_count=result["sentence_count"],
                paragraph_count=result["paragraph_count"],
                reading_minutes=result["reading_minutes"],
                keywords=result["keywords"],
            )
            st.success("Analysis saved to history.")
    else:
        st.info("Upload a PDF or TXT file to start.")
        st.markdown("**Included features**")
        st.write("- Document statistics and estimated reading time")
        st.write("- Top keyword frequency chart")
        st.write("- Search and highlight")
        st.write("- Downloadable TXT and CSV reports")
        st.write("- Optional analysis history saved in SQLite")

elif page == "Analysis History":
    st.subheader("Previous analyses")
    history = get_history()
    if history.empty:
        st.info("No saved analyses yet. Analyze a document and select “Save analysis to history.”")
    else:
        st.dataframe(history.drop(columns=["keywords_json"]), use_container_width=True, hide_index=True)
        with st.expander("View saved keywords"):
            for _, row in history.iterrows():
                st.markdown(f"**{row['filename']}** — {row['created_at']}")
                st.write(row["keywords_json"])
        if st.button("Clear all history", type="secondary"):
            delete_history()
            st.success("History cleared.")
            st.rerun()

else:
    st.subheader("About DocuSense")
    st.write(
        "DocuSense is a beginner-friendly Python web application that extracts text from PDF/TXT files "
        "and reports document statistics and frequent keywords. It uses rule-based text processing, "
        "not machine learning."
    )
    st.markdown("""
    **Technology stack**
    - Python — application logic
    - Streamlit — web interface
    - PyMuPDF — PDF text extraction
    - Pandas — tables and CSV export
    - Matplotlib/Streamlit charts — visualization
    - SQLite — local analysis history

    **Current limitation:** scanned PDFs that contain images rather than selectable text need OCR, which is not included.
    """)
