import socket
import sys

# How many bytes is the word length?
WORD_LEN_SIZE = 2


def usage():
    print("usage: wordclient.py server port", file=sys.stderr)


packet_buffer = b""


def get_next_word_packet(s: socket.socket):
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """

    global packet_buffer

    while True:
        # Check if the buffer already has a full word packet
        # If the buffer already has a full word packet, we can extract
        # the word packet from the buffer and return it

        # We want the buffer to have atleast WORD_LEN_SIZE + 1 bytes
        # because just having WORD_LEN_SIZE bytes means that no bytes are
        # there for the word in the buffer
        if len(packet_buffer) > WORD_LEN_SIZE:
            # Parse the length of the word in the packet
            word_length = int.from_bytes(packet_buffer[:WORD_LEN_SIZE], "big")
            packet_length = WORD_LEN_SIZE + word_length

            # If the full packet is present in the buffer, we can extract
            # and exit
            if len(packet_buffer) >= packet_length:
                packet = packet_buffer[:packet_length]
                packet_buffer = packet_buffer[packet_length:]
                return packet

        # If we reach here, it means that either there weren't even
        # WORD_LEN_SIZE + 1 bytes in the buffer or the full packet isn't present
        # So we receive the next bytes of the stream and go to the next iteration
        received_bytes = s.recv(4096)

        # If connection is closed then 0 bytes are received, in which case we can
        # return None
        if not received_bytes:
            return None

        # Append the bytes received to the buffer
        packet_buffer += received_bytes


def extract_word(word_packet: bytes):
    """
    Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """

    # The first WORD_LEN_SIZE bytes store the length of the word
    # Decode the word_length number of bytes as a word (UTF-8 is default)
    word = word_packet[WORD_LEN_SIZE:].decode()
    return word


# Do not modify:


def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    s.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
