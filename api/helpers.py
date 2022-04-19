import io

from api import config


def allowed_file(filename: str) -> bool:
    """Returns true if file name contains allowed extension and false otherwise
    Parameters
    ----------
    filename : str
       the filename along with the extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS

#
# def image_in_memory(img):
#     buffer = io.BytesIO()
#     img.save(buffer)
#     buffer.seek(0)
#     return buffer
