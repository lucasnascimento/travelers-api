import os
import urllib.parse

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
        # Check if the directory exists, if not, create it
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_obj.save(path)
        return path

    # Define the file name to be stored in the
    download_file_name = file_name.split('__')[-1]
    safe_file_name = urllib.parse.quote(download_file_name)
    content_disposition = f'attachment; filename="{safe_file_name}"'

    path = f"{UPLOAD_FOLDER}/{file_name}"
    s3_client.upload_fileobj(
        file_obj,
        UPLOAD_BUCKET,
        path,
        ExtraArgs={
            'ContentDisposition': content_disposition
        }
    )

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
