# imghdr.py shim for Python 3.13+
import mimetypes


def what(file, h=None):
    """
    Replacement for the removed imghdr.what().
    Uses mimetypes to guess image type.
    """
    mime, _ = mimetypes.guess_type(file)
    if mime and mime.startswith("image/"):
        return mime.split("/")[-1]
    return None
