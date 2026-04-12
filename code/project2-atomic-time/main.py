import socket
import time

# There is a rate limit on the NIST server. Only one request per 4s.
# So to account for this on multiple runs, we can run the program
# using "sleep 4 && python main.py"


def system_seconds_since_1900():
    # Number of seconds between 1900-01-01 and 1970-01-01
    seconds_delta = 2208988800
    seconds_since_unix_epoch = int(time.time())
    seconds_since_1900_epoch = seconds_since_unix_epoch + seconds_delta

    # Return the total time in seconds from the 1900 epoch
    return seconds_since_1900_epoch


def main():
    # Create & connect the socket to "time.nist.gov:37"
    s = socket.socket()
    s.connect(("time.nist.gov", 37))

    # Receive all the data until we get 4 bytes and close the socket
    bytes = b""
    while len(bytes) < 4:
        bytes += s.recv(4)
    s.close()

    # Since the bytes will be in big endian order
    nist_time = int.from_bytes(bytes, "big")
    print(f"NIST time  : {nist_time}")

    # Print the system time
    print(f"System time: {system_seconds_since_1900()}")


if __name__ == "__main__":
    main()
