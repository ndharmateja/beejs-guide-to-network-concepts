import re
import socket
import sys

from constants import CRLF, DEFAULT_BUFFER_SIZE, DEFAULT_LISTENING_PORT, ENCODING


class InvalidRequestException(Exception):
    pass


def parse_port():
    try:
        port = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_LISTENING_PORT
    except ValueError:
        print("Error: port must be a valid integer.")
        sys.exit(1)

    return port


# Raises InvalidRequestException if specified content length is less than
# the actual length of the payload
def is_data_receiving_done(total_bytes: bytes):
    # Decode the bytes
    data = total_bytes.decode(ENCODING)

    # If the empty line has not been received yet, we can return false
    double_crlf_index = data.find(CRLF * 2)
    if double_crlf_index == -1:
        return False

    # At this point we know that atleast the empty line after the headers
    # have been received. So we can parse the content length.
    # Content-Length:  24   \r\n
    # There could be white spaces before and after the number
    # and content-length itself could be lowercase
    match = re.search(r"Content-Length:\s*(\d+)", data, re.IGNORECASE)

    # If content-length header is not there, we can return true
    # as at this point, we have the double CRLF
    if not match:
        return True

    # At this point we can extract the content length
    content_length = int(match.group(1))

    # We can now check if the number of bytes after the empty line is
    # equal to the content length
    payload_start_index = double_crlf_index + len(CRLF * 2)
    num_bytes_payload = len(data[payload_start_index:].encode(ENCODING))

    # If the number of bytes in the payload is more than what the content length
    # specifies, we throw an error
    if num_bytes_payload > content_length:
        raise InvalidRequestException(
            "Payload length more than content length specified."
        )

    return num_bytes_payload == content_length


# Since client is not going to (atleast in the general case) close the
# connection, recv() is not going to return an empty string like in the case
# of webclient.py
# So we have to look for the CRLF * 2 in the data
# Raises InvalidRequestException if request is not valid
def receive_all_data(s: socket.socket):
    total_bytes = b""
    data = ""
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
            if is_data_receiving_done(total_bytes):
                break
        except UnicodeDecodeError:
            continue

    return data


def create_http_response():
    response_body = "Hello!"
    content_length = len(response_body.encode(ENCODING))

    s = f"HTTP/1.1 200 OK{CRLF}"
    s += f"Content-Type: text/plain{CRLF}"
    s += f"Content-Length: {content_length}{CRLF}"
    s += f"Connection: close{CRLF}"
    s += CRLF
    s += response_body

    return s.encode(ENCODING)


def extract_request_method(request: str):
    space_index = request.find(" ")
    return request[:space_index]


def main():
    # 0. Parse args
    port = parse_port()

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
            print(f"Accepted a connection from [IP: {client_ip}, port: {client_port}]")

            try:
                # Receive the data
                request = receive_all_data(conn_socket)
                if request:
                    request_method = extract_request_method(request)
                    print(f"Request method: {request_method}")

                # Create the response and send it back
                response_bytes = create_http_response()
                conn_socket.sendall(response_bytes)
            except InvalidRequestException as e:
                print(f"Invalid request: {e}")
            except Exception as e:
                print(f"Error handling connection: {e}")
            finally:
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
    main()
