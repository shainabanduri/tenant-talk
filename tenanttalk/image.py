import boto3
import os

session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


class image():
    def UploadImage(name, image):
        filename = name + '_picture.jpg'
        imagedata = image
        s3 = boto3.resource('s3')
        try:
            object = s3.Object('bucket sauce', filename)
            object.put(ACL='public-read', Body=imagedata, Key=filename)
            return True
        except Exception as e:
            return e
