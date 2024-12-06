from datetime import datetime
import cv2
import firebase_admin
from firebase_admin import credentials, storage


def initialize_firebase():
    # Firebase setup
    cred = credentials.Certificate(
        'SDL/cred/sdl-irn-firebase-adminsdk-veab8-41164ac055.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'sdl-irn.firebasestorage.app'
    })
    print("Firebase initialized successfully.")

# Fungsi untuk mengunggah gambar ke Firebase


def upload_to_firebase(img, filename):
    """Mengunggah gambar ke Firebase Storage."""
    try:
        _, img_encoded = cv2.imencode('.jpg', img)
        img_bytes = img_encoded.tobytes()

        # Firebase bucket
        bucket = storage.bucket()
        current_date = datetime.now().strftime('%Y-%m-%d')
        full_path = f"intruder_images/{current_date}/{filename}"

        blob = bucket.blob(full_path)
        blob.upload_from_string(img_bytes, content_type='image/jpeg')
        blob.make_public()

        print(f"Gambar berhasil diunggah ke Firebase: {blob.public_url}")
        return blob.public_url
    except Exception as e:
        print(f"Error saat mengunggah ke Firebase: {e}")
        return None
