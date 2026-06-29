# utils/certificate_generator.py - Cloudinary version
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import os
from django.conf import settings
from datetime import datetime
from cloudinary.uploader import upload
import io
from reportlab.lib.utils import ImageReader
import tempfile

def generate_certificate(user, event):
    """Generate certificate and upload to Cloudinary"""
    
    # ===== HATUA 1: Unda PDF kwenye memory (si filesystem) =====
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Title
    c.setFont("Helvetica-Bold", 28)
    c.setFillColorRGB(0.8, 0.2, 0.2)
    c.drawCentredString(width/2, height - 80, "CERTIFICATE OF PARTICIPATION")
    
    # Subtitle
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 130, "This certificate is proudly presented to")
    
    # User name
    c.setFont("Helvetica-Bold", 32)
    c.setFillColorRGB(0.2, 0.3, 0.5)
    full_name = f"{user.first_name} {user.last_name}".upper()
    if full_name.strip() == "":
        full_name = user.username.upper()
    c.drawCentredString(width/2, height - 190, full_name)
    
    # Achievement text
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 240, "for participating in")
    
    # Event name
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.2, 0.4, 0.6)
    event_title = event.title[:50]
    c.drawCentredString(width/2, height - 290, event_title)
    
    # Event date
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawCentredString(width/2, height - 330, f"Held on {event.event_date.strftime('%B %d, %Y')}")
    c.drawCentredString(width/2, height - 350, f"Location: {event.location}")
    
    # Issue date
    today = datetime.now().strftime("%B %d, %Y")
    c.drawCentredString(width/2, height - 390, f"Issued on: {today}")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, height - 430, "HOCET Young Charity Generation (HEYCG)")
    
    c.save()
    
    # ===== HATUA 2: Upload PDF to Cloudinary =====
    buffer.seek(0)  # Rudi mwanzo wa buffer
    
    try:
        # Upload to Cloudinary
        result = upload(
            buffer,  # Sio file path, ni buffer!
            folder="certificates",
            public_id=f"certificate_{user.id}_{event.id}",
            resource_type="raw",  # Kwa PDF na files zisizo picha
            format="pdf"
        )
        
        # ===== HATUA 3: Return URL ya Cloudinary =====
        cloudinary_url = result['secure_url']
        print(f"✅ Certificate uploaded: {cloudinary_url}")
        return cloudinary_url
        
    except Exception as e:
        print(f"❌ Error uploading certificate: {e}")
        return None


# ===== ALTERNATIVE - Ikiwa unataka kuweka certificate kwenye model =====
def generate_and_save_certificate(user, event, certificate_model):
    """
    Generate certificate, upload to Cloudinary, and save to model
    """
    cloudinary_url = generate_certificate(user, event)
    
    if cloudinary_url:
        # Hifadhi URL kwenye model
        certificate = certificate_model.objects.create(
            user=user,
            event=event,
            certificate_url=cloudinary_url,  # Weka URL kama string
            generated_at=datetime.now()
        )
        return certificate
    return None