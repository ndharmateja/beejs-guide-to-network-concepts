import os
from pathlib import Path

from constants import BASE_STATIC_DIR, ENCODING, ContentType
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
        # Get the absolute path and handle invalid path cases
        self.server_root = os.path.abspath(BASE_STATIC_DIR)
        full_path = os.path.sep.join((self.server_root, file_path))
        full_path = os.path.abspath(full_path)

        # We have to make sure that whatever is being requested is a (nested)
        # subfolder in the base directory
        if not full_path.startswith(self.server_root):
            raise FileNotFoundError("Invalid path.")

        # If a folder is requested, show the listing
        if os.path.isdir(full_path):
            self.__content_bytes = self.generate_files_listing(full_path)
            self.__content_type = ContentType.TEXT_HTML
            return

        # If a file is requested, serve it
        # Get the filename
        file_extension = os.path.splitext(full_path)[-1]

        # If no extension, then we assume it is html
        if not file_extension:
            file_extension = ".html"
            full_path += file_extension

        # If the file extension is not supported, throw error
        if file_extension not in StaticFile.EXTENSION_TO_MIME_TYPE:
            raise MimeTypeNotSupportedException(
                f"Unsupported file extension: {file_extension}"
            )

        # Open the file and read the contents
        # Automatically throws a FileNotFoundError if the requested file
        # doesn't exist
        with open(full_path, "rb") as f:
            self.__content_bytes = f.read()
            self.__content_type = self.EXTENSION_TO_MIME_TYPE[file_extension]

    def generate_files_listing(self, full_path):
        """Assumes that full_path is a path to a folder"""

        # Get the relative path of the given folder
        dir_path = Path(full_path)
        relative_path = dir_path.relative_to(self.server_root)

        # Start building the HTML
        html = f"<html><head><title>Index</title></head><body>"
        html += f"<h1>Index of /{relative_path}</h1><ul>"

        # If entry is "cat.jpg", the link should be "/cat.jpg"
        entries = os.listdir(full_path)
        for entry in entries:
            entry_path = dir_path / entry
            relative_path = entry_path.relative_to(self.server_root)
            html += f'<li><a href="/{relative_path}">{entry}</a></li>'

        html += "</ul></body></html>"
        return html.encode(ENCODING)

    @property
    def content_bytes(self):
        return self.__content_bytes

    @property
    def content_type(self):
        return self.__content_type
