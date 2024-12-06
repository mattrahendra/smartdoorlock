from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from .models import Image
from django.shortcuts import render
from .camera_utils import capture_and_process, video_stream
from .firebase_utils import initialize_firebase

#initialize firebase
initialize_firebase()

# Create your views here.
def home(request):
    images = Image.objects.all().order_by('-timestamp')
    return render(request, 'home.html', {'images': images})

#template integration tests
# def display_camera_feed(request):
#     if request.method == "GET":
#         capture_and_process()
#         return render(request, 'home.html', {'status': 'Processing...'})


def display_camera_feed(request):
    """
    Menangani proses capture dan menampilkan hasilnya
    """
    try:
        # Panggil capture_and_process dengan request
        response = capture_and_process(request)

        # Dapatkan images terbaru untuk ditampilkan
        images = Image.objects.all().order_by('-timestamp')

        # Render template dengan response dan images
        return render(request, 'home.html', {
            'status': 'Processing...',
            'images': images,
            'captured_image': response
        })

    except Exception as e:
        return render(request, 'home.html', {
            'error': f'Error processing image: {str(e)}'
        })

# def video_stream_view(request):
#     """
#     Menyediakan stream video ke halaman web menggunakan MJPEG
#     """
#     return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')


def video_stream_view(request):
    """
    Menyediakan stream video ke halaman web menggunakan MJPEG
    """
    try:
        return StreamingHttpResponse(
            video_stream(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return HttpResponse(f'Streaming error: {str(e)}', status=500)
