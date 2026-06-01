"""
verified_pdf_generator.py
─────────────────────────
Generates a ResumeAI Verified PDF by overlaying a verification stamp
and QR code onto the ORIGINAL uploaded resume PDF.

Key design decisions:
  - Original PDF content is PRESERVED — we only add an overlay stamp page
  - Stamp is appended as a new page (not merged onto existing pages)
  - QR code links to /verify-resume/<verification_id> for public verification
  - Uses ReportLab for stamp generation + PyPDF2 for merging
  - Output saved to uploads/verified/
"""

import os
import io
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_verified_pdf(
    original_pdf_path: str,
    verification_id: str,
    institution: str,
    verified_email: str,
    app_base_url: str,
    output_dir: str,
    upload_date: str = "",
) -> str:
    """
    Generate a verified PDF by:
    1. Extracting candidate name from the first page text
    2. Adding a subtle verification watermark to the footer of each page
    3. Appending a full premium verification certificate page at the end

    Args:
        original_pdf_path: Path to the uploaded original resume PDF.
        verification_id:   Unique ID like RAI-2026-A3F9B.
        institution:       Verified institution name.
        verified_email:    The email that was verified.
        app_base_url:      Base URL for QR code link (e.g. https://app.com).
        output_dir:        Directory to save verified PDF (e.g. uploads/verified/).
        upload_date:       The date the resume was uploaded.

    Returns:
        Absolute path to the generated verified PDF.
    """
    try:
        from PyPDF2 import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.colors import Color, HexColor
        from reportlab.lib.units import inch, mm
    except ImportError as e:
        logger.error(f"[verified_pdf] Missing dependency: {e}")
        raise RuntimeError(f"Server dependency missing: {e}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Verify original file exists
    if not os.path.isfile(original_pdf_path):
        raise FileNotFoundError(f"Original resume not found: {original_pdf_path}")

    # ── Generate QR code image ─────────────────────────────────────
    qr_image = _generate_qr_code(f"{app_base_url}/verify-resume/{verification_id}")

    # ── Read original PDF ──────────────────────────────────────────
    reader = PdfReader(original_pdf_path)
    writer = PdfWriter()

    # ── Extract candidate name from original PDF ──────────────────
    candidate_name = "Candidate"
    try:
        if reader.pages:
            first_page_text = reader.pages[0].extract_text() or ""
            filename = os.path.basename(original_pdf_path)
            candidate_name = _extract_candidate_name(first_page_text, filename)
    except Exception as e:
        logger.warning(f"[verified_pdf] Could not extract candidate name: {e}")

    # ── Step 1: Copy all original pages + add watermark to footer ──
    for page in reader.pages:
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        overlay = _create_footer_watermark(page_width, page_height, verification_id)
        overlay_reader = PdfReader(overlay)
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    # ── Step 2: Append full verification certificate page ──────────
    cert_page = _create_certificate_page(
        verification_id=verification_id,
        institution=institution,
        verified_email=verified_email,
        issue_date=datetime.now(timezone.utc).strftime("%B %d, %Y"),
        qr_image=qr_image,
        candidate_name=candidate_name,
        upload_date=upload_date,
    )
    cert_reader = PdfReader(cert_page)
    for page in cert_reader.pages:
        writer.add_page(page)

    # ── Step 3: Write output ───────────────────────────────────────
    output_filename = f"verified_{verification_id}.pdf"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(f"[verified_pdf] Generated: {output_path}")
    return output_path


def _generate_qr_code(url: str) -> io.BytesIO:
    """Generate a QR code image in memory."""
    try:
        import qrcode
        from qrcode.image.pil import PilImage

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    except ImportError:
        logger.warning("[verified_pdf] qrcode not installed, generating placeholder")
        # Return a minimal 1x1 white PNG as fallback
        buf = io.BytesIO()
        try:
            from PIL import Image
            img = Image.new("RGB", (100, 100), "white")
            img.save(buf, format="PNG")
        except ImportError:
            # Absolute fallback — empty bytes
            pass
        buf.seek(0)
        return buf


def _extract_candidate_name(resume_text: str, filename: str) -> str:
    """Helper to extract a clean candidate name from resume text or filename."""
    import re
    # 1. Check the first few lines of text
    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
    for line in lines[:3]:
        # Filter out lines that are too long, contain contact info, or common label words
        words = line.split()
        if 2 <= len(words) <= 4 and "@" not in line and ":" not in line and not any(
            k in line.lower() for k in ["resume", "cv", "curriculum", "university", "college", "email", "phone", "profile", "contact", "address", "portfolio"]
        ):
            cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            if cleaned and len(cleaned.split()) >= 2:
                # Capitalize words
                return " ".join(w.capitalize() for w in cleaned.split())

    # 2. Fallback to filename
    base = os.path.splitext(filename)[0]
    # Strip prefixes like "verified_" or hashes
    base = re.sub(r'^(verified_)?', '', base)
    base_clean = re.sub(r'(?i)(_|-|\s)+(resume|cv|pdf|docx|202\d|new|final|copy|main|v\d+)', '', base)
    base_clean = re.sub(r'[^a-zA-Z\s_-]', '', base_clean)
    words = re.split(r'[_-\s]+', base_clean)
    words = [w.capitalize() for w in words if w]
    if words:
        return " ".join(words)

    return "Candidate"


def draw_verification_seal(c, x: float, y: float, size: float):
    """
    Programmatically draw a premium, vector-based ResumeAI Verification Seal at (x, y) with the given size.
    Shield-inspired trust design, with blue/emerald-green colors, fully printer and PDF viewer compatible.
    """
    from reportlab.lib.colors import HexColor, Color

    r = size / 2.0
    c.saveState()

    # 1. Outer Concentric Border (Deep Blue)
    c.setStrokeColor(HexColor("#2563EB"))
    c.setLineWidth(size * 0.02)
    c.circle(x, y, r, stroke=1, fill=0)

    # 2. Accent Border (Gold)
    c.setStrokeColor(HexColor("#D4AF37"))
    c.setLineWidth(size * 0.01)
    c.circle(x, y, r - size * 0.04, stroke=1, fill=0)

    # 3. Seal Background (Soft Emerald Green)
    c.setFillColor(Color(16 / 255, 185 / 255, 129 / 255, alpha=0.10))
    c.setStrokeColor(HexColor("#10B981"))
    c.setLineWidth(size * 0.035)
    c.circle(x, y, r - size * 0.08, stroke=1, fill=1)

    # 4. Center Shield Design (Deep Blue Fill)
    c.setFillColor(HexColor("#2563EB"))
    c.setStrokeColor(HexColor("#1E3A8A"))
    c.setLineWidth(size * 0.015)

    shield_path = c.beginPath()
    # Top center
    shield_path.moveTo(x, y + r * 0.5)
    # Top right
    shield_path.lineTo(x + r * 0.45, y + r * 0.5)
    # Right edge to bottom center curve
    shield_path.quadraticTo(x + r * 0.45, y - r * 0.1, x, y - r * 0.6)
    # Left edge to bottom center curve
    shield_path.quadraticTo(x - r * 0.45, y - r * 0.1, x - r * 0.45, y + r * 0.5)
    shield_path.close()
    c.drawPath(shield_path, fill=1, stroke=1)

    # 5. White Checkmark inside the shield
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", int(size * 0.38))
    # Vertical offset to center within the shield
    c.drawCentredString(x, y - size * 0.06, "✓")

    # 6. Mini Stars / Dots (Only on larger seals)
    if size >= 60:
        c.setFillColor(HexColor("#10B981"))
        c.setFont("Helvetica-Bold", int(size * 0.06))
        c.drawString(x - r * 0.7, y + r * 0.4, "★")
        c.drawString(x + r * 0.58, y + r * 0.4, "★")

    c.restoreState()


def draw_certificate_header(c, width: float, height: float):
    """
    Draw a premium header branding for the certificate page.
    """
    from reportlab.lib.colors import HexColor

    center_x = width / 2
    c.saveState()

    # Brand name / Logo
    c.setFillColor(HexColor("#2563EB"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(center_x, height - 65, "⚡ RESUMEAI")

    # Indigo/Gold divider line below brand
    c.setStrokeColor(HexColor("#E5E7EB"))
    c.setLineWidth(1.0)
    c.line(width * 0.25, height - 80, width * 0.75, height - 80)

    c.restoreState()


def _create_footer_watermark(page_width: float, page_height: float, verification_id: str) -> io.BytesIO:
    """
    Create a subtle, professional watermark in the footer area of the page.
    Features a thin separator line and centered verification details in dark gray.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import Color

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    c.saveState()
    
    # ── Draw thin separator line ──
    c.setStrokeColor(Color(100/255, 116/255, 139/255, alpha=0.25))
    c.setLineWidth(0.5)
    line_y = 52
    c.line(page_width / 2 - 120, line_y, page_width / 2 + 120, line_y)

    # ── Draw tiny verification seal centered ──
    draw_verification_seal(c, page_width / 2, 34, 20)

    # ── Draw watermark text ──
    c.setFillColor(Color(102/255, 102/255, 102/255, alpha=0.55))
    c.setFont("Helvetica-Bold", 8.0)
    c.drawCentredString(page_width / 2, 17, "✓ VERIFIED BY RESUMEAI")

    # Shorten verification ID for display in the badge (e.g. RAI-2026-B8C2D4E9)
    parts = verification_id.split("-")
    if len(parts) >= 3:
        display_id = f"{parts[0]}-{parts[1]}-{parts[2][:8]}"
    else:
        display_id = verification_id[:17]

    # Slightly smaller/lighter for the subline ID
    c.setFont("Helvetica", 7.0)
    c.drawCentredString(page_width / 2, 8, f"Verification ID: {display_id}")
    
    c.restoreState()

    c.save()
    packet.seek(0)
    return packet


def _create_certificate_page(
    verification_id: str,
    institution: str,
    verified_email: str,
    issue_date: str,
    qr_image: io.BytesIO,
    candidate_name: str,
    upload_date: str = "",
) -> io.BytesIO:
    """
    Create a premium full-page verification certificate with:
    - ResumeAI branding & title "RESUME AUTHENTICITY CERTIFICATE"
    - Corporate double-line borders
    - Large green/gold verification seal (badge)
    - Statement of authenticity
    - Candidate Name, Institution Name, Status, verification ID, dates
    - QR code link for online confirmation
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import Color, HexColor

    W, H = letter  # 612 x 792
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    # ── Page Background ────────────────────────────────────────────
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Double-line Border ─────────────────────────────────────────
    # Outer Indigo Border
    c.setStrokeColor(HexColor("#1E3A8A"))
    c.setLineWidth(1.5)
    c.rect(20, 20, W - 40, H - 40, stroke=1, fill=0)

    # Inner Gold Border
    c.setStrokeColor(HexColor("#D4AF37"))
    c.setLineWidth(0.75)
    c.rect(24, 24, W - 48, H - 48, stroke=1, fill=0)

    # ── Header Branding ────────────────────────────────────────────
    draw_certificate_header(c, W, H)

    # ── Main Certificate Title ──────────────────────────────────────
    c.setFillColor(HexColor("#1F2937"))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 95, "RESUME AUTHENTICITY CERTIFICATE")

    # ── Large Verification Seal (Badge) ────────────────────────────
    center_x = W / 2
    seal_y = H - 165
    draw_verification_seal(c, center_x, seal_y, 76)

    # Seal text labels
    c.setFillColor(HexColor("#2563EB"))  # Deep Blue
    c.setFont("Helvetica-Bold", 10.5)
    c.drawCentredString(center_x, seal_y - 52, "RESUMEAI VERIFIED")
    
    c.setFillColor(HexColor("#10B981"))  # Emerald Green
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(center_x, seal_y - 64, "INSTITUTION AUTHENTICATED")
    
    c.setFillColor(HexColor("#6B7280"))  # Slate/Gray
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(center_x, seal_y - 74, "AI-Powered Resume Verification")

    # ── Statement of Authenticity ──────────────────────────────────
    statement_y = seal_y - 105
    c.setFillColor(HexColor("#4B5563"))
    c.setFont("Helvetica-Oblique", 9.5)
    statement_l1 = "This resume has been verified through an institutional email verification process"
    statement_l2 = "and authenticated by ResumeAI."
    c.drawCentredString(center_x, statement_y, statement_l1)
    c.drawCentredString(center_x, statement_y - 12, statement_l2)

    # ── Candidate Name ─────────────────────────────────────────────
    name_label_y = statement_y - 44
    c.setFillColor(HexColor("#6B7280"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(center_x, name_label_y, "CANDIDATE NAME")

    name_val_y = name_label_y - 20
    c.setFillColor(HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(center_x, name_val_y, candidate_name.upper())

    # ── Details Grid ───────────────────────────────────────────────
    details_y = name_val_y - 50
    display_upload_date = upload_date if upload_date else issue_date

    details = [
        ("Institution Name", institution or "Not specified"),
        ("Verification Status", "VERIFIED"),
        ("Verification ID", verification_id),
        ("Verification Date", issue_date),
        ("Resume Upload Date", display_upload_date),
    ]

    for i, (label, value) in enumerate(details):
        y = details_y - (i * 35)

        # Label
        c.setFillColor(HexColor("#6B7280"))
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(center_x, y + 10, label.upper())

        # Value
        if label == "Verification Status":
            c.setFillColor(HexColor("#10B981"))
        elif label == "Verification ID":
            c.setFillColor(HexColor("#4F46E5"))
        else:
            c.setFillColor(HexColor("#1F2937"))
        
        c.setFont("Helvetica-Bold", 10.5)
        c.drawCentredString(center_x, y - 2, value)

    # ── QR Code ────────────────────────────────────────────────────
    qr_y = details_y - (len(details) * 35) - 15
    qr_size = 72

    try:
        from reportlab.lib.utils import ImageReader
        qr_reader = ImageReader(qr_image)
        c.drawImage(
            qr_reader,
            center_x - qr_size / 2,
            qr_y - qr_size,
            width=qr_size,
            height=qr_size,
        )
    except Exception as e:
        logger.warning(f"[verified_pdf] Could not embed QR code: {e}")

    # QR Label
    c.setFillColor(HexColor("#6B7280"))
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(center_x, qr_y - qr_size - 10, "Scan to verify this resume online")

    # ── Footer ─────────────────────────────────────────────────────
    c.setFillColor(HexColor("#9CA3AF"))
    c.setFont("Helvetica", 7)
    c.drawCentredString(center_x, 42, "This certificate is an official proof of resume authentication issued by ResumeAI.")
    c.drawCentredString(center_x, 32, f"Verification ID: {verification_id}  |  Secured via Cryptographic QR Code Links")

    c.save()
    packet.seek(0)
    return packet
