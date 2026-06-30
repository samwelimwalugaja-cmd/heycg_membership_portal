# utils/certificate_generator.py - Version ya Local Media
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import os
from django.conf import settings
from datetime import datetime

def generate_certificate(user, event):
    """Generate certificate and save to local media folder"""
    
    # Unda folder
    cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    
    # Jina la file
    filename = f"certificate_{user.id}_{event.id}.pdf"
    filepath = os.path.join(cert_dir, filename)
    
    # Unda PDF
    c = canvas.Canvas(filepath, pagesize=landscape(A4))
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
    
    # Return URL ya picha (media path)
    return f"/media/certificates/{filename}"