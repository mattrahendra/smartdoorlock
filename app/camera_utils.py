import cv2
import urllib.request
import numpy as np
from django.http import StreamingHttpResponse
from datetime import datetime, timedelta
from .firebase_utils import upload_to_firebase

# URL kamera IP
url = 'http://192.168.1.10/640x480.jpg'

# Initialize Haar Cascade classifiers
f_cas = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml')

# Initialize last capture time
last_capture_time = datetime.now() - timedelta(seconds=1)


def capture_and_process():
    global last_capture_time
    try:
        img_resp = urllib.request.urlopen(url, timeout=5)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgnp, -1)
        img = cv2.flip(img, 0)

        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = f_cas.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for x, y, w, h in faces:
                # Gambarkan kotak di sekitar wajah yang terdeteksi
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = img[y:y + h, x:x + w]

                # Deteksi mata di dalam wajah
                eyes = eye_cascade.detectMultiScale(roi_gray)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey),
                                (ex + ew, ey + eh), (0, 255, 0), 2)

            # Debugging: Pastikan wajah terdeteksi dengan benar
            print(f"Faces detected: {len(faces)}")

            current_time = datetime.now()
            if (current_time - last_capture_time).total_seconds() >= 30:
                last_capture_time = current_time
                timestamp = current_time.strftime('%Y%m%d_%H%M%S')
                filename = f'{timestamp}_face.jpg'
                upload_to_firebase(img, filename)

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# def video_stream():
#     """
#     Fungsi untuk stream video
#     """
#     global last_capture_time

#     while True:
#         try:
#             # Ambil gambar dari stream URL
#             img_resp = urllib.request.urlopen(url, timeout=5)
#             imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
#             img = cv2.imdecode(imgnp, -1)

#             # Memutar gambar menjadi upside down
#             img = cv2.flip(img, 0)  # 0 berarti flip secara vertikal

#             # Mengubah gambar menjadi JPEG
#             _, jpeg = cv2.imencode('.jpg', img)
#             frame = jpeg.tobytes()

#             # Menghasilkan frame untuk streaming
#             yield (b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#         except Exception as e:
#             print(f"Error: {e}")
#             break

def video_stream():
    """Streaming video dari kamera IP."""
    global last_capture_time

    while True:
        try:
            # Ambil frame dari kamera IP
            img_resp = urllib.request.urlopen(url, timeout=5)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgnp, -1)

            # Membalik gambar vertikal
            img = cv2.flip(img, 0)

            # Proses deteksi wajah
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = f_cas.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5)

            for x, y, w, h in faces:
                # Gambar kotak di wajah
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = img[y:y + h, x:x + w]

                # Deteksi mata
                eyes = eye_cascade.detectMultiScale(roi_gray)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey),
                                (ex + ew, ey + eh), (0, 255, 0), 2)

                # Ambil foto setiap 30 detik
                current_time = datetime.now()
                if (current_time - last_capture_time).total_seconds() >= 30:
                    last_capture_time = current_time
                    timestamp = current_time.strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_face.jpg"
                    upload_to_firebase(img, filename)

            # Encode frame ke format JPEG untuk streaming
            _, jpeg = cv2.imencode('.jpg', img)
            frame = jpeg.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        except Exception as e:
            print(f"Error in video stream: {e}")
            break
