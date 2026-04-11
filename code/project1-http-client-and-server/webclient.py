import socket
import sys

CRLF = "\r\n"
ENCODING = "iso-8859-1"
DEFAULT_BUFFER_SIZE = 4096
DEFAULT_PORT = 80


def parse_url_and_port():
    if len(sys.argv) == 1:
        print(f"Error: Missing arguments.")
        print(f"  Usage  : python {sys.argv[0]} <url> [port]")
        print(f"  Example: python {sys.argv[0]} example.com 80")
        sys.exit(1)

    url = sys.argv[1]
    try:
        port = int(sys.argv[2]) if len(sys.argv) == 3 else DEFAULT_PORT
    except ValueError:
        print("Error: port must be a valid integer.")
        sys.exit(1)

    return url, port


def create_http_get_request(url):
    s = f"GET / HTTP/1.1{CRLF}"
    s += f"Host: {url}{CRLF}"
    s += f"Connection: close{CRLF}"
    s += CRLF

    return s.encode(ENCODING)


def receive_all_data(s: socket.socket):
    total_bytes = b""
    while True:
        bytes = s.recv(DEFAULT_BUFFER_SIZE)
        if not len(bytes):
            break
        total_bytes += bytes

    return total_bytes.decode(ENCODING)


def main():
    # 0. Parse the url and port from the command line args
    url, port = parse_url_and_port()

    # 1. Create a socket and set timeout
    s = socket.socket()
    s.settimeout(10.0)

    try:
        # 2. Get the IP using DNS (optional in python as the connect()
        # method takes care of it) and connect to the IP + port
        s.connect((url, port))

        # 3. Create and send the HTTP request
        # GET / HTTP/1.1
        # Host: <url>
        # Connection: close
        # <blank line>
        request_bytes = create_http_get_request(url)
        s.sendall(request_bytes)

        # 4. Receive all the data
        data = receive_all_data(s)
        print(data)

    # Handle error scenarios
    except socket.gaierror:
        print(f"Error: Couldn't resolve '{url}'. Check spelling and internet.")
    except ConnectionRefusedError:
        print(f"Error: Connection refused on port {port}.")
    except socket.timeout:
        print(f"Error: Connection timed out.")
    except Exception as e:
        print("Unexpected error: {e}.")

    # Cleanup resources
    finally:
        # 5. Close the socket
        s.close()
        print("\nClient socket closed")


if __name__ == "__main__":
    main()
