import socket
import sys

DEFAULT_LISTENING_PORT = 28333
DEFAULT_BUFFER_SIZE = 4096
ENCODING = "iso-8859-1"
CRLF = "\r\n"


def parse_port():
    try:
        port = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_LISTENING_PORT
    except ValueError:
        print("Error: port must be a valid integer.")
        sys.exit(1)

    return port


# Since client is not going to (atleast in the general case) close the
# connection, recv() is not going to return an empty string like in the case
# of webclient.py
# So we have to look for the CRLF * 2 in the data
def receive_all_data(s: socket.socket):
    total_bytes = b""
    data = ""
    while True:
        # If client closes connection
        bytes = s.recv(DEFAULT_BUFFER_SIZE)
        if not bytes:
            break

        # Decode and append the data
        data += bytes.decode(ENCODING)
        if data.endswith(CRLF * 2):
            break

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
