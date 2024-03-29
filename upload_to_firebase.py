import firebase_admin
from firebase_admin import credentials, storage
from PIL import Image
import io
from datetime import datetime, timedelta
import uuid


class UploadImage:
    def __init__(self) -> None:

        cred = credentials.Certificate(
            "antique-store-36cbb-firebase-adminsdk-xq1fg-043309d265.json"
        )
        firebase_admin.initialize_app(
            cred, {"storageBucket": "antique-store-36cbb.appspot.com"}
        )

    def get_img_url(self, image):
        # Get a reference to the Firebase Storage service
        bucket = storage.bucket()

        file = Image.open(image)

        # Convert the image file to bytes
        image_bytes = io.BytesIO()
        file.save(image_bytes, format=file.format)
        image_bytes.seek(0)

        # Get the image filename
        image_name = str(uuid.uuid1())

        # Upload image to Firebase Storage
        blob = bucket.blob("images/" + image_name)
        blob.upload_from_file(image_bytes, content_type=file.format)

        # Get download URL of the uploaded image with expiration time
        download_url = blob.generate_signed_url(
            expiration=(datetime.now() + timedelta(days=100000))
        )
        return download_url
