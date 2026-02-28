import qrcode
import jwt
import os
from datetime import datetime, timezone

SECRET_KEY = os.getenv("SECRET_KEY", "sherlock_secret_key_123")

def generate_signed_qr(item_id: str, verification_id: str, output_dir: str):
    """
    Generates a QR code with a signed JWT payload.
    Payload: { "status": "VERIFIED", "itemId": "...", "verificationId": "...", "timestamp": "..." }
    """
    payload = {
        "status": "VERIFIED",
        "itemId": str(item_id),
        "verificationId": str(verification_id),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Sign the token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    filename = f"qr_{verification_id}.png"
    file_path = os.path.join(output_dir, filename)
    img.save(file_path)
    
    return filename, file_path
