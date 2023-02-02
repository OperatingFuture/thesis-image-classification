# from keras.models import load_model

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]


def allowed_file(filename: str) -> bool:
    """Returns true if file name contains allowed extension and false otherwise
    Parameters
    ----------
    filename : str
       the filename along with the extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
