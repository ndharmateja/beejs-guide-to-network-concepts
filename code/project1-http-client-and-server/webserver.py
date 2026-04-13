import socket
import sys

from constants import DEFAULT_BUFFER_SIZE, DEFAULT_LISTENING_PORT, ENCODING, ContentType
from errors import InvalidRequestException, MimeTypeNotSupportedException
from request import Request
from response import Response, ResponseBuilder
from static_file import StaticFile


def parse_port():
    try:
        port = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_LISTENING_PORT
    except ValueError:
        print("Error: port must be a valid integer.")
        sys.exit(1)

    return port


class WebServer:
    def __init__(self, port):
        self.port = port

    # Since client is not going to (atleast in the general case) close the
    # connection, recv() is not going to return an empty string like in the case
    # of webclient.py
    # So we have to look for the CRLF * 2 in the data
    # Raises InvalidRequestException if request is not valid
    @staticmethod
    def receive_all_data(s: socket.socket):
        total_bytes = b""
        while True:
            # If client closes connection
            bytes = s.recv(DEFAULT_BUFFER_SIZE)
            if not bytes:
                break

            # Test if the last 4 bytes are CRLF * 2
            # We add to the total bytes and then decode it because there could
            # be characters that are split up between 2 recv() calls
            # In which case a UnicodeDecodeError will be raised and we can continue
            total_bytes += bytes
            try:
                if Request.is_data_receiving_done(total_bytes):
                    break
            except UnicodeDecodeError:
                continue

        return total_bytes

    def start(self):
        # 1. Create a socket for listening
        listening_socket = socket.socket()
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            # 2. Bind the socket to a port
            listening_socket.bind(("", port))

            # 3. Listen for incoming connections
            listening_socket.listen()
            print(f"Listening for connections on port: {port}")

            # 4. Accept connection (in a loop) and send and receive data
            while True:
                conn_socket, (client_ip, client_port) = listening_socket.accept()
                print(
                    f"Accepted a connection from [IP: {client_ip}, port: {client_port}]"
                )

                try:
                    # Receive the data
                    raw_request_data = WebServer.receive_all_data(conn_socket)
                    request = Request.from_raw_bytes(raw_request_data)
                    print(f"Request:\n[{request}]\n")

                    # Create the response and send it back
                    file = StaticFile(request.path)
                    response = (
                        ResponseBuilder()
                        .set_content_bytes(file.content_bytes, file.content_type)
                        .build()
                    )

                except InvalidRequestException as e:
                    print(f"Invalid request: {str(e)}")
                    response = Response.create_400_response(f"Invalid request.")
                except MimeTypeNotSupportedException as e:
                    print(f"Error handling connection: {str(e)}")
                    response = Response.create_415_response(str(e))
                except FileNotFoundError:
                    print("File not found")
                    response = Response.create_404_response()
                except Exception as e:
                    print(f"Error handling connection: {str(e)}")
                    response = Response.create_500_response(f"Unknown error.")
                finally:
                    # Send the response
                    conn_socket.sendall(response.get_bytes())

                    # Close the connection socket
                    conn_socket.close()
                    print("Closed the connection with the client")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: Shutting down the server.")
        finally:
            # Close the listening socket
            listening_socket.close()
            print("Listening socket closed.")


if __name__ == "__main__":
    # Parse args
    port = parse_port()

    # Create and run the server
    server = WebServer(port)
    server.start()
