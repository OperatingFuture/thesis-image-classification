conn_str = "mongodb://root_user:root_pwd@mongodb:27017/?authMechanism=DEFAULT"

classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]

def allowed_file(filename: str) -> bool:
    """Returns true if file name contains allowed extension and false otherwise
    Parameters
    ----------
    filename : str
       the filename along with the extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS