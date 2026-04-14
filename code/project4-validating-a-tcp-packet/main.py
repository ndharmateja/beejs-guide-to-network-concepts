def ip_string_to_bytes(ip: str) -> bytes:
    """Converts an input IP string like '1.2.3.4' into a
    bytes string b'\x01\x02\x03\x04'"""

    # "1.2.3.4"
    # ["1", "2", "3", "4"]
    # [1, 2, 3, 4]
    ints_list = [int(part) for part in ip.split(".")]

    # b'\x01\x02\x03\x04'
    return bytes(ints_list)


def get_byte_data(filename: str) -> bytes:
    with open(filename, "rb") as f:
        return f.read()


def get_ip_strings(ips_filename: str) -> list[str]:
    with open(ips_filename, "r") as f:
        return f.read().strip().split()


def make_pseudo_ip_header(src_ip: bytes, dest_ip: bytes, tcp_data_len: int) -> bytes:
    """Constructs the pseudo IP header with the format
    Source IP | Dest IP | Z | P | TCP Data Length"""

    # The Z (zero) byte is \x00
    # The P (protocol) byte is \x06 for TCP
    tcp_data_len_bytes = tcp_data_len.to_bytes(2, "big")
    return src_ip + dest_ip + b"\x00" + b"\x06" + tcp_data_len_bytes


def compute_cksum(data: bytes):
    total = 0
    for i in range(0, len(data), 2):
        # Get the 16-bit word's value by slicing two bytes at a time
        word: bytes = data[i : i + 2]
        value = int.from_bytes(word, "big")

        # In one's complement, we add the 17th bit to the sum
        # That is the carry around which we can get by "total >> 16"
        total += value
        total = (total & 0xFFFF) + (total >> 16)

    # Return one's complement of the total sum
    # The ~ in python for a positive number generally gives us a negative number
    # to keep it in the 16 bit range, we and it with 0xFFFF
    return (~total) & 0xFFFF


def main():
    for i in range(10):
        # Get the TCP data bytes and compute its length and checksum
        tcp_dat_filename = f"tcp_data/tcp_data_{i}.dat"
        tcp_data: bytes = get_byte_data(tcp_dat_filename)
        orig_cksum: int = int.from_bytes(tcp_data[16:18], "big")
        tcp_data_len = len(tcp_data)

        # Get the src and dest IPs as byte strings
        ips_filename = f"tcp_data/tcp_addrs_{i}.txt"
        ip_strings: list[str] = get_ip_strings(ips_filename)
        src_ip: bytes = ip_string_to_bytes(ip_strings[0])
        dest_ip: bytes = ip_string_to_bytes(ip_strings[1])

        # Construct the pseudo IP Header
        pseudo_ip_header: bytes = make_pseudo_ip_header(src_ip, dest_ip, tcp_data_len)

        # Make the bytes at offset 16 and 17 to \x00 in the TCP data which is the checksum
        # And make the length of the data even by padding it with a zero byte if necessary
        tcp_zero_cksum_data: bytes = tcp_data[:16] + b"\x00\x00" + tcp_data[18:]
        if tcp_data_len % 2 != 0:
            tcp_zero_cksum_data += b"\x00"

        # Concatenate the pseudo IP header and the TCP data (header + payload) to compute cksum
        data: bytes = pseudo_ip_header + tcp_zero_cksum_data
        computed_cksum = compute_cksum(data)

        # Check if the computed cksum matches the original cksum
        if computed_cksum == orig_cksum:
            print("PASS")
        else:
            print("FAIL")


if __name__ == "__main__":
    main()
