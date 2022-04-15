import json
import numpy as np
import requests
from flask import jsonify
from keras.applications import inception_v3
from keras.preprocessing import image


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