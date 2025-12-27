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

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not PyPDF2:
        raise HTTPException(status_code=501, detail="PyPDF2 not installed")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    try:
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return {"text": text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"ok": True}

@app.post("/translate")
def translate(req: TranslateRequest):
    rows = translate_text(req.text, mirror_rate=req.mirror_rate, engine=req.engine)
    return {"rows": rows}
