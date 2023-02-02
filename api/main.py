import base64
import io
import json
import os
import requests
from flask import request, jsonify, Response, send_file, render_template
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from api import api, helpers, s3_ops

conn_str = "mongodb://root_user:root_pwd@mongodb:27017/?authMechanism=DEFAULT"
client = MongoClient(conn_str)
collection = client.image_data.predictions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def predict(img, model):
    result = model.predict(img)
    classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    dict_result = {}
    for i in range(10):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i] * 100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result



@api.route("/alive", methods=["GET"])
def alive():
    """Liveliness Endpoint. Can be used as a probe."""
    return jsonify({"message": "I'm alive", "status": 200})


@api.route("/", methods=["GET"])
def home():
    """Homepage"""
    return render_template("index.html")


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
    s3_path = 'http://minio:9000/' + 'saved-images/' + filename
    image_url = requests.get(s3_path, stream=True)
    file_like_object = io.BytesIO()
    file_like_object.write(image_url.content)
    file_like_object.seek(0)

    return send_file(file_like_object, mimetype='image/jpeg')


# Takes the image details from mongodb.
@api.route("/image/<image_id>", methods=["GET"])
def get_image_data(image_id: str):
    filename = 'http://minio:9000/' + 'saved-images/' + image_id

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
    image_file = request.files['image']
    image_filename = secure_filename(image_file.filename)

    if image_filename == "":
        return (
            jsonify({"message": "image filename can not be empty", "status": "400"}),
            400,
        )

    if image_file and helpers.allowed_file(image_filename):
        # --- Controller start
        # prepare the image and save it in s3 bucket
        content_type = image_file.content_type
        upload_image_url = s3_ops.upload_img_to_s3(image_file, image_filename, content_type)
        get_image = s3_ops.image_from_s3(image_filename)

        model = s3_ops.load_model_from_s3("model_final")
        class_result, prob_result = predict(get_image, model)

        # predictions = {
        #     "class1": 'yolo',
        #     "class2": 'yolo',
        #     "class3": 'yolo',
        #     "prob1": 40,
        #     "prob2": 50,
        #     "prob3": 10,
        # }

        predictions = {
            "class1": class_result[0],
            "class2": class_result[1],
            "class3": class_result[2],
            "prob1": prob_result[0],
            "prob2": prob_result[1],
            "prob3": prob_result[2],
        }

        obj = {"uri": upload_image_url, "labels": "predictions"}

        try:
            collection.insert_one(obj)
            return render_template('success.html', url=upload_image_url, predictions=predictions)
        except Exception as e:
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
