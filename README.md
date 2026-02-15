# Smart Invoice & Quotation Generator (MVP)

## Folder Structure

```text
RECONNECT/
├── backend/
│   ├── main.py
│   ├── pdf_generator.py
│   ├── requirements.txt
│   └── schemas.py
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
└── README.md
```

## Backend FastAPI Code

`backend/main.py` exposes:
- `GET /` for the frontend
- `POST /calculate` for subtotal/GST/total preview
- `POST /generate-invoice` for downloadable PDF generation

## Frontend Code

`frontend/index.html`, `frontend/styles.css`, and `frontend/app.js` provide:
- Mobile responsive invoice form
- Auto-generated invoice number
- Editable current date
- Real-time/explicit totals calculation
- Download PDF action
- Optional WhatsApp share action

## PDF Generation Code

`backend/pdf_generator.py` uses ReportLab to generate a GST-ready invoice PDF with:
- Business header
- Customer and invoice metadata
- Item row with GST rate
- Subtotal + CGST/SGST + total summary
- Signature placeholder

## Installation Instructions

```bash
cd /workspace/RECONNECT
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Run Instructions

```bash
cd /workspace/RECONNECT/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open:
- http://127.0.0.1:8000

## How to Deploy Locally

### Option 1: Direct Uvicorn

```bash
cd /workspace/RECONNECT/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 2: Systemd service (Linux)

Create `/etc/systemd/system/smart-invoice.service`:

```ini
[Unit]
Description=Smart Invoice FastAPI Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/workspace/RECONNECT/backend
Environment="PATH=/workspace/RECONNECT/.venv/bin"
ExecStart=/workspace/RECONNECT/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable smart-invoice
sudo systemctl start smart-invoice
sudo systemctl status smart-invoice
```

## Suggestions for Later Scaling

1. Add SQLite invoice history table with search by customer/date/invoice number.
2. Add multi-item invoice rows and discount/transport fields.
3. Add quotation mode output with invoice/quotation toggle.
4. Add configurable tax type support (IGST for inter-state billing).
5. Add secure file storage (S3/GCS) and shareable short links.
6. Add print-optimized HTML invoice view.
7. Add language localization (English + Hindi + regional languages).
8. Add deployment stack (Nginx reverse proxy + Gunicorn/Uvicorn workers).
