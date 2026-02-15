from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from pdf_generator import build_invoice_pdf
from schemas import InvoiceRequest, calculate_totals

app = FastAPI(title="Smart Invoice & Quotation Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def home() -> FileResponse:
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_file)


@app.post("/calculate")
def calculate(payload: InvoiceRequest) -> JSONResponse:
    totals = calculate_totals(payload.quantity, payload.unit_price, payload.gst_rate)
    return JSONResponse(content={
        "subtotal": float(totals.subtotal),
        "gst_amount": float(totals.gst_amount),
        "total": float(totals.total),
    })


@app.post("/generate-invoice")
def generate_invoice(payload: InvoiceRequest) -> Response:
    totals = calculate_totals(payload.quantity, payload.unit_price, payload.gst_rate)
    pdf_data = build_invoice_pdf(payload, totals)

    filename = f"{payload.invoice_number.replace(' ', '_')}.pdf"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "X-Subtotal": str(totals.subtotal),
        "X-GST-Amount": str(totals.gst_amount),
        "X-Total": str(totals.total),
    }
    return Response(content=pdf_data, media_type="application/pdf", headers=headers)
