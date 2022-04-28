import os
import io
import requests
from dotenv import load_dotenv
from flask import request, jsonify, Response, send_file
from pymongo import MongoClient
from werkzeug.utils import secure_filename

from api import api, helpers, classifier, s3_ops

ROOT_DIR = os.path.realpath("..")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

conn_str = "mongodb://" + os.getenv('INIT_USERNAME') + ":" + os.getenv('INIT_PWD') + "@mongodb:27017/" + \
           os.getenv('INITDB')
client = MongoClient(conn_str)
collection = client.image_data.predictions


@api.route("/alive", methods=["GET"])
def alive():
    """Liveliness Endpoint. Can be used as a probe."""
    return jsonify({"message": "I'm alive", "status": 200})


@api.route("/image/<image_id>/preview", methods=["GET"])
def image_get(image_id):
    """
    Takes the image from the folder 'test_images' and returns it.

    Parameters
    ----------
    image_id

    Returns image file
    -------

    """
    filename = secure_filename(image_id)
    s3_path = 'http://localhost:9000/' + os.getenv("IMAGES_BUCKET") + '/' + filename
    image_url = requests.get(s3_path, stream=True)
    file_like_object = io.BytesIO()
    file_like_object.write(image_url.content)
    file_like_object.seek(0)

    return send_file(file_like_object, mimetype='image/jpeg')


# Takes the image details from mongodb.
@api.route("/image/<image_id>", methods=["GET"])
def get_image_data(image_id: str):
    filename = 'http://localhost:9000/' + os.getenv("IMAGES_BUCKET") + '/' + image_id

    try:
        data = collection.find_one({"uri": filename}, {"_id": 0})
        if data is None:
            return jsonify({"message": "image not found", "status": "404"}), 404
        return jsonify(data)
    except Exception as e:
        print("An exception occurred ::", e)
        return jsonify({"Error": e.__str__()})


# Take the details from all the images in mongodb.
@api.route("/images", methods=["GET"])
def images():
    search = request.args.get("search")

    offset = int(request.args.get("offset", 0))

    size = int(request.args.get("size", 10))

    if size < 0:
        return jsonify({"message": "Bad request", "status": "400"}), 400
    query = {}
    if search is not None:
        query = {"labels.label": {"$regex": search}}

    try:
        cursor = collection.find(query, {"_id": 0}).skip(offset).limit(size)
        list_cur = list(cursor)
        if not list_cur:
            return jsonify({"message": "No image found", "status": "404"}), 404
        return jsonify(list_cur)
    except Exception as e:
        print("An exception occurred ::", e)
        return jsonify({"Error": e.__str__()})


@api.route("/image", methods=["POST"])
def image_post():
    # do all the validations in payload (validate every parameter)
    """This endpoint receives a form parameter called image with the image file to be classified,
    and saves the image uri to mongo.
    """
    if "image" not in request.files:
        return (
            jsonify(
                {"message": "missing 'image' post form parameter", "status": "400"}
            ),
            400,
        )
    img = request.files['image']
    image = img.stream.read()

    if img.filename == "":
        return (
            jsonify({"message": "image filename can not be empty", "status": "400"}),
            400,
        )
    if img and helpers.allowed_file(img.filename):
        # --- Controller start
        # prepare the image and save it in the upload folder
        filename = secure_filename(img.filename)
        content_type = img.content_type
        upload_image = s3_ops.upload_file_to_s3(image, filename, content_type)
        # TODO save image reference to database

        get_image = s3_ops.image_from_s3(filename)

        # get_image.save(im_path)
        res = classifier.image_classifier(get_image)

        # Something wrong in for loop for labels.
        # TODO save classification result to database
        # uri = "/image/" + filename
        uri = upload_image
        # labels = res
        labels = {'id': res[0][0], 'label': res[0][1], 'percentage': res[0][2]}
        # for item in res[0]:
        #     case = {'id': item[0], 'label': item[1], 'percentage': item[2]}
        #     labels.append(case)

        obj = {"uri": uri, "labels": labels}

        try:
            collection.insert_one(obj)
            return jsonify({"message": "success", "status": "200"}), 200
        except Exception as e:
            print("An exception occurred ::", e)
            return jsonify({"Error": e.__str__()})

        # ----- Controller end
    else:
        return (
            jsonify(
                {
                    "message": "not allowed image type, allowed types are: 'png', 'jpg', 'jpeg', 'gif' ",
                    "status": "400",
                }
            ),
            400,
        )


if __name__ == "main":
    api.run()
