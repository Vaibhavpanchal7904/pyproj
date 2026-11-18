# DocuSense — Smart Document Analyzer

A beginner-friendly Python web mini project. Upload a PDF or TXT file to extract text, inspect document statistics, explore common keywords, search/highlight phrases, and export reports.

## Features

- PDF and TXT upload
- Text extraction from selectable-text PDFs
- Word, character, sentence, paragraph, and estimated reading-time statistics
- Top-10 keyword frequency chart
- Search and highlight phrase occurrences
- TXT report and keyword CSV downloads
- SQLite analysis history

## Requirements

- Python 3.10 or newer
- Internet connection for the first-time package installation

## Run on Windows (PowerShell)

1. Extract the ZIP file.
2. Open PowerShell in the `docusense` folder.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

4. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run:

   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   streamlit run app.py
   ```

7. Streamlit will open the app in your browser, usually at `http://localhost:8501`.

## Project structure

```text
docusense/
├── app.py
├── analyzer.py
├── database.py
├── requirements.txt
└── README.md
```

The `docusense.db` SQLite database is created automatically the first time the app runs.

## Notes and limitations

- Scanned/image-only PDFs require OCR; OCR is intentionally not included in this beginner version.
- Reading time is estimated at 200 words per minute.
- Keyword analysis uses a small built-in stop-word list and word frequency; it does not generate an AI summary.
- Keep confidential documents off public/shared deployments.
