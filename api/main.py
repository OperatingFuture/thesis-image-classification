import os

from dotenv import load_dotenv
from flask import request, jsonify, send_file
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from api import api, config, helpers, classifier
from api.s3_ops import upload_file

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
    im_path = os.path.join(config.UPLOAD_FOLDER, filename)
    return send_file(im_path, mimetype="image/jpeg")


# Takes the image details from mongodb.
@api.route("/image/<image_id>", methods=["GET"])
def get_image_data(image_id: str):
    filename = "/image/" + image_id

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
    img = request.files["image"]
    if img.filename == "":
        return (
            jsonify({"message": "image filename can not be empty", "status": "400"}),
            400,
        )
    if img and helpers.allowed_file(img.filename):

        # --- Controller start
        # prepare the image and save it in the upload folder
        filename = secure_filename(img.filename)

        im_path = os.path.join(config.UPLOAD_FOLDER, filename)

        # TODO save image reference to database
        img.save(im_path)
        yolo = upload_file(img, img.filename)
        res = classifier.image_classifier(im_path)

        # Something wrong in for loop for labels.
        # TODO save classification result to database
        uri = "/image/" + filename
        labels = []
        for o in res:
            case = {'id': o[0], 'label': o[1], 'percentage': o[2]}
            labels.append(case)

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
