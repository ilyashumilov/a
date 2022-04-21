import requests
from django.conf import settings

from face_recognition.services.s3_service import get_photo_raw


def test_photo(photo_s3: str):
    face_url = f'http://{settings.FACE_URL}/v2/detect?age=on&gender=on'

    headers = {
        'Content-Type': 'image/jpeg',
    }

    data = get_photo_raw(photo_s3)
    response = requests.post(face_url, headers=headers, data=data)
    print(response.json())
