from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import io

# Optional: PyPDF import
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from zyntalic.translator import translate_text

app = FastAPI(title="Zyntalic API", version="0.3.0")

# Mount static directory
# We now point to the built React app in zyntalic-flow/dist
# If running fro project root:
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "zyntalic-flow", "dist")

if not os.path.exists(static_dir):
    # Fallback to old static if build fails or during dev
    print(f"WARNING: React build not found at {static_dir}. Falling back to legacy static.")
    static_dir = os.path.join(os.path.dirname(__file__), "static")

app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
# Mount the root static files (like index.html, favicon, etc) separately or handled by root route?
# Fastapi StaticFiles at root matches everything.
# Better strategy: mount assets at /assets and serve index.html at root


class TranslateRequest(BaseModel):
    text: str
    mirror_rate: float = 0.3  # Lower value = more Zyntalic vocabulary, higher = more English templates
    engine: str = "core"  # "core"|"chiasmus"|"transformer"|"test_suite"

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

def clean_pdf_text(raw_text: str) -> str:
    """Clean extracted PDF text by removing metadata, garbled characters, and extra whitespace."""
    import re
    
    # Remove common PDF metadata patterns
    metadata_patterns = [
        r'%PDF-[\d\.]+',
        r'%����',
        r'/Author\([^)]*\)',
        r'/Creator\([^)]*\)',
        r'/Producer\([^)]*\)',
        r'/Title\([^)]*\)',
        r'/Subject\([^)]*\)',
        r'/Keywords\([^)]*\)',
        r'/CreationDate\([^)]*\)',
        r'/ModDate\([^)]*\)',
        r'\d+ \d+ obj',
        r'endobj',
        r'stream\s*.*?\s*endstream',
        r'<<[^>]*>>',
        r'\[http://[^\]]*\]',
        r'xref',
        r'trailer',
        r'startxref',
        r'%%EOF',
    ]
    
    cleaned = raw_text
    for pattern in metadata_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # Replace common PDF encoding issues
    replacements = {
        '�': '',  # Remove replacement character
        '\x00': '',  # Remove null bytes
        '\ufffd': '',  # Remove Unicode replacement character
        '\r\n': '\n',  # Normalize line endings
        '\r': '\n',
    }
    
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    # Remove multiple spaces and normalize whitespace
    cleaned = re.sub(r' +', ' ', cleaned)
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    
    # Remove lines that are just numbers or single characters (often page numbers)
    lines = cleaned.split('\n')
    filtered_lines = []
    for line in lines:
        line = line.strip()
        # Keep line if it has substantial content
        if len(line) > 3 and not line.isdigit():
            filtered_lines.append(line)
    
    cleaned = '\n'.join(filtered_lines)
    
    # Final cleanup: remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and extract text from PDF or text files."""
    
    # Handle plain text files
    if file.filename.endswith(('.txt', '.md')):
        try:
            content = await file.read()
            text = content.decode('utf-8', errors='ignore')
            return {"text": text.strip()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading text file: {str(e)}")
    
    # Handle PDF files
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="File must be PDF, TXT, or MD format"
        )
    
    if not PyPDF2:
        raise HTTPException(
            status_code=501, 
            detail="PyPDF2 not installed. Run: pip install PyPDF2"
        )
        
    try:
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        
        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="PDF is encrypted. Please provide an unencrypted PDF."
            )
        
        # Extract text from all pages
        raw_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + "\n"
            except Exception as e:
                # Skip problematic pages but continue
                print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                continue
        
        # Clean the extracted text
        cleaned_text = clean_pdf_text(raw_text)
        
        if not cleaned_text or len(cleaned_text) < 10:
            raise HTTPException(
                status_code=400, 
                detail="No readable text found in PDF. The file may be scanned images or corrupted."
            )
        
        return {"text": cleaned_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/health")
def health():
    return {"ok": True}

@app.post("/translate")
def translate(req: TranslateRequest):
    rows = translate_text(req.text, mirror_rate=req.mirror_rate, engine=req.engine)
    return {"rows": rows}
