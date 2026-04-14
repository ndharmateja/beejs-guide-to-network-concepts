import json
import sys


def ipv4_to_value(ipv4_addr: str) -> int:
    """
    Convert a dots-and-numbers IP address to a single 32-bit numeric
    value of integer type. Returns an integer type.

    Example:

    ipv4_addr: "255.255.0.0"
    return:    4294901760  (Which is 0xffff0000 hex)

    ipv4_addr: "1.2.3.4"
    return:    16909060  (Which is 0x01020304 hex)
    """

    # nums = [1, 2, 3, 4]
    nums = [int(x) for x in ipv4_addr.split(".")]

    # Method 1:
    # accumulate the value using left shifts and or operations
    #        0 << 8 | 1 = 0x01
    #     0x01 << 8 | 2 = 0x0102
    #   0x0102 << 8 | 3 = 0x010203
    # 0x010203 << 8 | 4 = 0x01020304
    # This is the same as calculating ax^3 + bx^2 + cx + d
    # using Horner's method with x = 256. (((ax + b)x + c)x + d
    # Instead of multiplying by 256 each time we are left shifting by 8
    # and instead of adding, we are doing | and it is the same as after
    # shifting by 8 bits the remaining 8 bits are 0s so adding or oring with
    # an 8 bit number is the same.
    # 0x0100 + 0x02 = 0x0100 | 0x02 = 0x0102
    def method1():
        val = 0
        for num in nums:
            val = (val << 8) | num
        return val

    # Method 2:
    # Directly do the required shift in one go and accumulate
    # (1 << 24) | (2 << 16) | (3 << 8) | (4 << 0) = 0x01020304
    def method2():
        val = 0
        for i, num in enumerate(nums):
            val |= num << ((3 - i) * 8)
        return val

    # Method 3:
    # Convert it into a bytes array and then create an int out of it
    def method3():
        return int.from_bytes(bytes(nums), "big")

    # Return answer
    return method3()


def value_to_ipv4(addr: int) -> str:
    """
    Convert a single 32-bit numeric value of integer type to a
    dots-and-numbers IP address. Returns a string type.

    Example:

    There is only one input value, but it is shown here in 3 bases.

    addr:   0xffff0000 0b11111111111111110000000000000000 4294901760
    return: "255.255.0.0"

    addr:   0x01020304 0b00000001000000100000001100000100 16909060
    return: "1.2.3.4"
    """

    # Method 1:
    # Extracting one byte at a time with AND and right shifts
    def method1():
        # the tuple (24, 16, 8, 0) can also created programmatically
        # for let's say IPv6
        # shifts = range((num_bytes - 1) * 8, -1, -8)
        # For IPv4 (4 bytes): (24, 16, 8, 0)
        # For IPv6 (16 bytes): (120, 112, ..., 0)
        octets = []
        for shift in (24, 16, 8, 0):
            octets.append(str((addr >> shift) & 0xFF))

        # result at this point will be ["255", "255", "0", "0"]
        return ".".join(octets)

    # Method 2:
    # By converting the number in to a bytes string
    def method2():
        bytes_str = addr.to_bytes(4, "big")

        # bytes_str will be b"\xff\xff\x00\x00" at this point
        return ".".join(str(byte) for byte in bytes_str)

    # Return result
    return method2()


def get_subnet_mask_value(slash: str) -> int:
    """
    Given a subnet mask in slash notation, return the value of the mask
    as a single number of integer type. The input can contain an IP
    address optionally, but that part should be discarded.

    Returns an integer type.

    Example:

    There is only one return value, but it is shown here in 3 bases.

    slash:  "/16"
    return: 0xffff0000 0b11111111111111110000000000000000 4294901760

    slash:  "10.20.30.40/23"
    return: 0xfffffe00 0b11111111111111111111111000000000 4294966784
    """

    # Get the number of network bits and host bits
    # It is the int(sliced part after the / in the slash string)
    n = int(slash[slash.find("/") + 1 :])
    h = 32 - n

    # Edge cases:
    # Not necessary for python, but C and C++ have undefined behaviour
    # when ints are shifted by 32 bits
    if n == 0:
        return 0
    if n == 32:
        return 0xFFFFFFFF

    # Generate n 1s first by using (1 << n) - 1
    # which is (1 followed by n 0s) - 1
    # which is n 1s
    # and then add (32 - n) 0s at the end by left shifting
    # Gotcha: If n = 32, 1 << 32 will be undefined in C and C++
    def method1():
        return ((1 << n) - 1) << h

    # Method 2:
    def method2():
        return (0xFFFFFFFF << h) & 0xFFFFFFFF

    # Method 3:
    def method3():
        return ((0xFFFFFFFF) >> h) << h

    # Return result
    return method3()


def get_network(ip_value: int, netmask: int) -> int:
    """
    Return the network portion of an address value as integer type.

    Example:

    ip_value: 0x01020304
    netmask:  0xffffff00
    return:   0x01020300
    """

    # We just have to a bitwise AND between the IP and the subnet mask
    return ip_value & netmask


def ips_same_subnet(ip1: str, ip2: str, slash: str) -> bool:
    """
    Given two dots-and-numbers IP addresses and a subnet mask in slash
    notation, return true if the two IP addresses are on the same
    subnet.

    Returns a boolean.

    FOR FULL CREDIT: this must use your get_subnet_mask_value() and
    ipv4_to_value() functions. Don't do it with pure string
    manipulation.

    This needs to work with any subnet from /1 to /31

    Example:

    ip1:    "10.23.121.17"
    ip2:    "10.23.121.225"
    slash:  "/23"
    return: True

    ip1:    "10.23.230.22"
    ip2:    "10.24.121.225"
    slash:  "/16"
    return: False
    """

    # Get the numerical values of the IPs
    ip1_val = ipv4_to_value(ip1)
    ip2_val = ipv4_to_value(ip2)

    # Get the network values for both IPs and compare them
    def method1():
        subnet_mask = get_subnet_mask_value(slash)
        return get_network(ip1_val, subnet_mask) == get_network(ip2_val, subnet_mask)

    # Right shift by the number of host bits and the values should match
    # Number of network bits
    def method2():
        n = int(slash[slash.find("/") + 1 :])
        h = 32 - n
        return (ip1_val >> h) == (ip2_val >> h)

    # Return result
    return method2()


def find_router_for_ip(routers: dict[str, dict[str, str]], ip: str) -> str | None:
    """
    Search a dictionary of routers (keyed by router IP) to find which
    router belongs to the same subnet as the given IP.

    Return None if no routers is on the same subnet as the given IP.

    FOR FULL CREDIT: you must do this by calling your ips_same_subnet()
    function.

    Example:

    [Note there will be more data in the routers dictionary than is
    shown here--it can be ignored for this function.]

    routers: {
        "1.2.3.1": {
            "netmask": "/24"
        },
        "1.2.4.1": {
            "netmask": "/24"
        }
    }
    ip: "1.2.3.5"
    return: "1.2.3.1"


    routers: {
        "1.2.3.1": {
            "netmask": "/24"
        },
        "1.2.4.1": {
            "netmask": "/24"
        }
    }
    ip: "1.2.5.6"
    return: None
    """

    # TODO -- write me!
    pass


# Uncomment this code to have it run instead of the real main.
# Be sure to comment it back out before you submit!
def my_tests():
    print("-------------------------------------")
    print("This is the result of my custom tests")
    print("-------------------------------------")

    # Test cases
    # ipv4_to_value
    assert ipv4_to_value("0.0.0.0") == 0
    assert ipv4_to_value("255.255.255.255") == 4294967295
    assert ipv4_to_value("192.168.0.1") == 3232235521
    assert ipv4_to_value("10.0.0.1") == 167772161
    assert ipv4_to_value("1.2.3.4") == 16909060
    assert ipv4_to_value("255.255.0.0") == 4294901760
    print("All test cases for ipv4_to_value successfully passed!")

    # value_to_ipv4
    assert value_to_ipv4(0xFFFF0000) == "255.255.0.0"
    assert value_to_ipv4(0x01020304) == "1.2.3.4"
    assert value_to_ipv4(16909060) == "1.2.3.4"
    assert value_to_ipv4(167772161) == "10.0.0.1"
    assert value_to_ipv4(3232235521) == "192.168.0.1"
    assert value_to_ipv4(4294967295) == "255.255.255.255"
    print("All test cases for value_to_ipv4 successfully passed!")

    # get_subnet_mask_value
    assert get_subnet_mask_value("/16") == 0xFFFF0000
    assert get_subnet_mask_value("10.20.30.40/23") == 0xFFFFFE00
    assert get_subnet_mask_value("10.20.30.40/24") == 0xFFFFFF00
    assert get_subnet_mask_value("10.20.30.40/25") == 0xFFFFFF80
    assert get_subnet_mask_value("10.20.30.40/26") == 0xFFFFFFC0
    assert get_subnet_mask_value("10.20.30.40/27") == 0xFFFFFFE0
    assert get_subnet_mask_value("10.20.30.40/28") == 0xFFFFFFF0
    assert get_subnet_mask_value("10.20.30.40/29") == 0xFFFFFFF8
    assert get_subnet_mask_value("10.20.30.40/30") == 0xFFFFFFFC
    assert get_subnet_mask_value("10.20.30.40/31") == 0xFFFFFFFE
    assert get_subnet_mask_value("10.20.30.40/32") == 0xFFFFFFFF
    print("All test cases for get_subnet_mask_value successfully passed!")

    # ips_same_subnet
    assert ips_same_subnet("1.2.3.4", "1.2.3.5", "/24") is True
    assert ips_same_subnet("1.2.3.4", "1.2.3.5", "/31") is True
    assert ips_same_subnet("1.2.3.4", "1.2.3.5", "/32") is False
    assert ips_same_subnet("1.2.2.1", "1.2.3.1", "/23") is True
    assert ips_same_subnet("1.2.2.1", "1.2.3.1", "/24") is False
    assert ips_same_subnet("10.20.30.40", "10.20.30.40", "/32") is True
    assert ips_same_subnet("192.168.0.100", "192.168.0.100", "/0") is True
    assert ips_same_subnet("0.0.0.0", "255.255.255.255", "/0") is True
    assert ips_same_subnet("172.16.0.1", "172.31.255.254", "/12") is True
    assert ips_same_subnet("172.16.0.1", "172.32.0.1", "/12") is False
    assert ips_same_subnet("192.168.1.64", "192.168.1.127", "/26") is True
    assert ips_same_subnet("192.168.1.127", "192.168.1.128", "/26") is False
    assert ips_same_subnet("8.8.8.8", "8.8.8.9", "/31") is True
    print("All test cases for ips_same_subnet successfully passed!")

    # get_network
    # The IP: 192.168.0.65 -> 3232235585
    ip = 3232235585
    assert get_network(ip, 0x00000000) == 0
    assert get_network(ip, 0xFFFF0000) == 3232235520
    assert get_network(ip, 0xFFFFFF00) == 3232235520
    assert get_network(ip, 0xFFFFFF80) == 3232235520
    assert get_network(ip, 0xFFFFFFC0) == 3232235584
    assert get_network(ip, 0xFFFFFFFC) == 3232235584
    assert get_network(ip, 0xFFFFFFFE) == 3232235584
    assert get_network(ip, 0xFFFFFFFF) == 3232235585
    print("All test cases for get_network successfully passed!")


## -------------------------------------------
## Do not modify below this line
##
## But do read it so you know what it's doing!
## -------------------------------------------


def usage():
    print("usage: netfuncs.py infile.json", file=sys.stderr)


def read_routers(file_name):
    with open(file_name) as fp:
        json_data = fp.read()

    return json.loads(json_data)


def print_routers(routers):
    print("Routers:")

    routers_list = sorted(routers.keys())

    for router_ip in routers_list:

        # Get the netmask
        slash_mask = routers[router_ip]["netmask"]
        netmask_value = get_subnet_mask_value(slash_mask)
        netmask = value_to_ipv4(netmask_value)

        # Get the network number
        router_ip_value = ipv4_to_value(router_ip)
        network_value = get_network(router_ip_value, netmask_value)
        network_ip = value_to_ipv4(network_value)

        print(f" {router_ip:>15s}: netmask {netmask}: " f"network {network_ip}")


def print_same_subnets(src_dest_pairs):
    print("IP Pairs:")

    src_dest_pairs_list = sorted(src_dest_pairs)

    for src_ip, dest_ip in src_dest_pairs_list:
        print(f" {src_ip:>15s} {dest_ip:>15s}: ", end="")

        if ips_same_subnet(src_ip, dest_ip, "/24"):
            print("same subnet")
        else:
            print("different subnets")


def print_ip_routers(routers, src_dest_pairs):
    print("Routers and corresponding IPs:")

    all_ips = sorted(set([i for pair in src_dest_pairs for i in pair]))

    router_host_map = {}

    for ip in all_ips:
        router = str(find_router_for_ip(routers, ip))

        if router not in router_host_map:
            router_host_map[router] = []

        router_host_map[router].append(ip)

    for router_ip in sorted(router_host_map.keys()):
        print(f" {router_ip:>15s}: {router_host_map[router_ip]}")


def main(argv):
    if "my_tests" in globals() and callable(my_tests):
        my_tests()
        return 0

    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    src_dest_pairs = json_data["src-dest"]

    print_routers(routers)
    print()
    print_same_subnets(src_dest_pairs)
    print()
    print_ip_routers(routers, src_dest_pairs)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
