from api import config


def allowed_file(filename: str) -> bool:
    """Returns true if file name contains allowed extension and false otherwise
    Parameters
    ----------
    filename : str
       the filename along with the extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS
