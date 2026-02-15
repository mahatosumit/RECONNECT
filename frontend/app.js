const form = document.getElementById('invoiceForm');
const statusText = document.getElementById('statusText');

const subtotalEl = document.getElementById('subtotal');
const gstAmountEl = document.getElementById('gstAmount');
const totalAmountEl = document.getElementById('totalAmount');

const invoiceDate = document.getElementById('invoiceDate');
const invoiceNumber = document.getElementById('invoiceNumber');

const quantityInput = document.getElementById('quantity');
const unitPriceInput = document.getElementById('unitPrice');
const gstRateInput = document.getElementById('gstRate');

const formatINR = (value) => `₹ ${Number(value).toFixed(2)}`;

const today = new Date();
invoiceDate.value = today.toISOString().split('T')[0];
invoiceNumber.value = `INV-${today.getFullYear()}${String(today.getMonth() + 1).padStart(2, '0')}${String(today.getDate()).padStart(2, '0')}-${Math.floor(Math.random() * 900 + 100)}`;

function buildPayload() {
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  payload.quantity = Number(payload.quantity || 0);
  payload.unit_price = Number(payload.unit_price || 0);
  payload.gst_rate = Number(payload.gst_rate || 0);
  payload.business_gst_number = payload.business_gst_number.toUpperCase();
  return payload;
}

async function calculateTotals() {
  statusText.textContent = '';
  const payload = buildPayload();

  if (!payload.quantity || !payload.unit_price) {
    statusText.textContent = 'Enter quantity and price to calculate totals.';
    return null;
  }

  const response = await fetch('/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail?.[0]?.msg || 'Unable to calculate totals.');
  }

  const totals = await response.json();
  subtotalEl.textContent = formatINR(totals.subtotal);
  gstAmountEl.textContent = formatINR(totals.gst_amount);
  totalAmountEl.textContent = formatINR(totals.total);
  return totals;
}

async function generateInvoice(event) {
  event.preventDefault();
  try {
    const totals = await calculateTotals();
    if (!totals) return;

    const response = await fetch('/generate-invoice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildPayload()),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.[0]?.msg || 'Could not generate invoice PDF.');
    }

    const blob = await response.blob();
    const contentDisposition = response.headers.get('content-disposition') || '';
    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
    const filename = filenameMatch ? filenameMatch[1] : 'invoice.pdf';

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);

    statusText.textContent = 'Invoice PDF generated successfully.';
  } catch (error) {
    statusText.textContent = error.message;
  }
}

function shareOnWhatsApp() {
  const payload = buildPayload();
  const text = `Invoice ${payload.invoice_number}%0A${payload.customer_name}%0ATotal: ${encodeURIComponent(totalAmountEl.textContent)}%0APlease attach the downloaded PDF before sending.`;
  window.open(`https://wa.me/${payload.customer_phone}?text=${text}`, '_blank');
}

form.addEventListener('submit', generateInvoice);
document.getElementById('calculateBtn').addEventListener('click', async () => {
  try {
    await calculateTotals();
  } catch (error) {
    statusText.textContent = error.message;
  }
});
document.getElementById('whatsappBtn').addEventListener('click', shareOnWhatsApp);

[quantityInput, unitPriceInput, gstRateInput].forEach((input) => {
  input.addEventListener('input', async () => {
    if (!quantityInput.value || !unitPriceInput.value) return;
    try {
      await calculateTotals();
    } catch (_) {
      // Ignore auto-calc errors while user is typing.
    }
  });
});
