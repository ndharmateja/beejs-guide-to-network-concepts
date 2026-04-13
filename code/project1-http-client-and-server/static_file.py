import os

from constants import ENCODING, ContentType
from errors import MimeTypeNotSupportedException


class StaticFile:
    EXTENSION_TO_MIME_TYPE = {
        ".txt": ContentType.TEXT_PLAIN,
        ".html": ContentType.TEXT_HTML,
        ".ico": ContentType.ICO,
        ".jpg": ContentType.JPEG,
        ".jpeg": ContentType.JPEG,
        ".pdf": ContentType.PDF,
    }

    def __init__(self, file_path):
        self.base_dir = "static"

        if file_path == "/":
            self.__content_bytes = self.generate_files_listing()
            self.__content_type = ContentType.TEXT_HTML
            return

        # Get the filename
        file_name = os.path.split(file_path)[-1]
        file_extension = os.path.splitext(file_name)[-1]

        # If no extension, then we assume it is html
        if not file_extension:
            file_extension = ".html"
            file_name += file_extension

        # If the file extension is not supported, throw error
        if file_extension not in StaticFile.EXTENSION_TO_MIME_TYPE:
            raise MimeTypeNotSupportedException(
                f"Unsupported file extension: {file_extension}"
            )

        # Open the file and read the contents
        with open(os.path.join(self.base_dir, file_name), "rb") as f:
            self.__content_bytes = f.read()
            self.__content_type = self.EXTENSION_TO_MIME_TYPE[file_extension]

    def generate_files_listing(self):
        entries = os.listdir(self.base_dir)

        # Start building the HTML
        html = f"<html><head><title>Index</title></head><body>"
        html += f"<h1>Index of /</h1><ul>"

        # If entry is "cat.jpg", the link should be "/cat.jpg"
        for entry in entries:
            html += f'<li><a href="/{entry}">{entry}</a></li>'

        html += "</ul></body></html>"
        return html.encode(ENCODING)

    @property
    def content_bytes(self):
        return self.__content_bytes

    @property
    def content_type(self):
        return self.__content_type
