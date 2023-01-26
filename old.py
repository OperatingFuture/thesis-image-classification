def image_classifier(image_path):
    # TODO make this a "something" service to interact with classifications
    """Receives an image path and calls the tensorflow-serving endpoint that serves the classification model.
     Parameters
        ----------
        image_path : str
           the full image path where the wanted image can be found."""
    # Preprocessing our input image
    # img = image.img_to_array(image.load_img(image_path, target_size=(224, 224))) / 255.
    img = image.img_to_array(image_path) / 255.

    url = 'http://tensorflow-serving:8501/v1/models/inceptionv3:predict'
    headers = {"content-type": "application/json"}
    # prepare the tensorflow-serving payload
    # payload = {
    #     "instances": [{'input_image': img.tolist()}]
    # }
    data = json.dumps({"instances": [{'input_image': img.tolist()}]})

    # Make the POST request
    response = requests.post(url, data=data, headers=headers)

    # propagate error from tf serving api
    if response.status_code > 200:
        return jsonify({"message": json.loads(response.text), "status": response.status_code})

    # Decoding results from TensorFlow Serving server
    pred = json.loads(response.content)

    # Returning JSON response.
    return inception_v3.decode_predictions(np.array(pred['predictions']))[0]