from PIL import Image


def get_orientation(image_path: str) -> str:
    """
    Read the image's EXIF orientation metadata.

    Returns one of:
        0_DEG
        90_DEG
        180_DEG
        270_DEG
    """

    try:
        with Image.open(image_path) as image:
            exif = image.getexif()

            # EXIF orientation tag.
            orientation = exif.get(274)

            mapping = {
                1: "0_DEG",
                3: "180_DEG",
                6: "90_DEG",
                8: "270_DEG",
            }

            return mapping.get(orientation, "0_DEG")

    except Exception:
        return "0_DEG"