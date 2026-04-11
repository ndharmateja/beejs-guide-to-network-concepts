import socket
import sys

from constants import DEFAULT_BUFFER_SIZE, DEFAULT_PORT
from request import RequestBuilder
from response import Response


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


class WebClient:
    @staticmethod
    def receive_all_data(s: socket.socket):
        total_bytes = b""
        while True:
            bytes = s.recv(DEFAULT_BUFFER_SIZE)
            if not len(bytes):
                break
            total_bytes += bytes

        return total_bytes

    def __init__(self, url, port):
        self.url = url
        self.port = port

    def run(self):
        # 1. Create a socket and set timeout
        s = socket.socket()
        s.settimeout(10.0)

        try:
            # 2. Get the IP using DNS (optional in python as the connect()
            # method takes care of it) and connect to the IP + port
            s.connect((self.url, self.port))

            # 3. Create and send the HTTP request
            # GET / HTTP/1.1
            # Host: <url>
            # Connection: close
            # <blank line>
            request = RequestBuilder().set_host(self.url).build()
            s.sendall(request.get_bytes())

            # 4. Receive all the data
            raw_response_bytes = WebClient.receive_all_data(s)
            response = Response.from_raw_data(raw_response_bytes)
            print(response)

        # Handle error scenarios
        except socket.gaierror:
            print(f"Error: Couldn't resolve '{self.url}'. Check spelling and internet.")
        except ConnectionRefusedError:
            print(f"Error: Connection refused on port {self.port}.")
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
    # Parse the url and port from the command line args
    url, port = parse_url_and_port()

    # Create and run the client
    client = WebClient(url, port)
    client.run()
