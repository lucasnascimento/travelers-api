import os

import boto3

from config import ENVIRONMENT, UPLOAD_BUCKET, UPLOAD_FOLDER

s3_client = boto3.client("s3")


def upload_file(file_obj, file_name):
    if ENVIRONMENT == "local":
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"static/{UPLOAD_FOLDER}",
            file_name,
        )
        file_obj.save(path)
        return path

    path = f"{UPLOAD_FOLDER}/{file_name}"
    s3_client.upload_fileobj(file_obj, UPLOAD_BUCKET, path)

    return path


def get_path(region, path, expiration=300):
    if region == "local":
        return f"/static{path.split('static')[1]}"

    if region == "web":
        return path

    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": UPLOAD_BUCKET, "Key": path},
        ExpiresIn=expiration,
    )
