from api import api
import json
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import requests
import numpy as np
from keras.applications import inception_v3
from keras.preprocessing import image
from pymongo import MongoClient
from dotenv import load_dotenv

ROOT_DIR = os.path.realpath("..")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# TODO move these to config
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_FOLDER = "test_images/"

conn_str = "mongodb://"+os.getenv('INIT_USERNAME')+":"+os.getenv('INIT_PWD')+"@mongodb:27017/"+os.getenv('INITDB')
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
    im_path = os.path.join(UPLOAD_FOLDER, filename)
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
    if img and allowed_file(img.filename):

        # --- Controller start
        # prepare the image and save it in the upload folder
        filename = secure_filename(img.filename)

        im_path = os.path.join(UPLOAD_FOLDER, filename)

        # TODO save image reference to database
        img.save(im_path)

        res = image_classifier(im_path)

        # Something wrong in foor loop for labels.
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


def allowed_file(filename: str) -> bool:
    """Returns true if file name contains allowed extension and false otherwise
    Parameters
    ----------
    filename : str
       the filename along with the extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "main":
    api.run()


def image_classifier(image_path: str):
    # TODO make this a "something" service to interact with classifications
    """Receives an image path and calls the tensorflow-serving endpoint that serves the classification model.
     Parameters
        ----------
        image_path : str
           the full image path where the wanted image can be found."""
    # Preprocessing our input image
    img = image.img_to_array(image.load_img(image_path, target_size=(224, 224))) / 255.

    # this line is added because of a bug in tf_serving(1.10.0-dev)
    img = img.astype('float16')

    # prepare the tensorflow-serving payload
    payload = {
        "instances": [{'input_image': img.tolist()}]
    }

    # Make the POST request
    r = requests.post('http://tensorflow-serving:8501/v1/models/inceptionv3:predict', json=payload)

    # propagate error from tf serving api
    if r.status_code > 200:
        return jsonify({"message": json.loads(r.text), "status": r.status_code})

    # Decoding results from TensorFlow Serving server
    pred = json.loads(r.content.decode('utf-8'))

    # Returning JSON response.
    return inception_v3.decode_predictions(np.array(pred['predictions']))[0]
