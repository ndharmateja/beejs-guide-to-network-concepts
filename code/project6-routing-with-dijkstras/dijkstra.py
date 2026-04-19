import json
import math  # If you want to use math.inf for infinity
import sys
from queue import PriorityQueue

from netfuncs import ips_same_subnet


def find_subnet_ip(routers, ip):
    for router_ip, router_data in routers.items():
        # If the given IP is the same as the IP of the subnet, we directly return it
        if ip == router_ip:
            return ip

        # If the given IP is on the same subnet as the IP of the subnet,
        # we return the IP of the subnet
        slash = router_data["netmask"]
        if ips_same_subnet(router_ip, ip, slash):
            return router_ip

    return None


def get_nearest_non_visited_node(distances, visited):
    min_dist_ip = None
    min_dist = math.inf
    for ip, dist in distances.items():
        if ip not in visited and dist < min_dist:
            min_dist = dist
            min_dist_ip = ip

    return min_dist_ip


def dijkstras_shortest_path(routers, src_ip, dest_ip):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """
    # Find the subnets of the src and dest IPs
    src_ip_subnet = find_subnet_ip(routers, src_ip)
    dest_ip_subnet = find_subnet_ip(routers, dest_ip)
    if not src_ip_subnet or not dest_ip_subnet:
        raise ValueError("src and/or dest IPs are not on any of the given subnets")

    # If they are both on the same subnet, then no routers are involved
    if src_ip_subnet == dest_ip_subnet:
        return []

    # Init the data structures
    distances = {ip: math.inf for ip in routers.keys()}
    parents = {}
    visited = set()

    # Set the values for the src_ip
    distances[src_ip_subnet] = 0
    parents[src_ip_subnet] = None

    # Add all vertices to the priority queue
    while True:
        # Get the ip with the shortest distance
        min_dist_ip = get_nearest_non_visited_node(distances, visited)
        if not min_dist_ip:
            break

        # Mark the ip as visited and relax all its edges
        visited.add(min_dist_ip)
        for neighbour_ip, neighbour_data in routers[min_dist_ip]["connections"].items():
            if (
                neighbour_ip not in visited
                and distances[min_dist_ip] + neighbour_data["ad"]
                < distances[neighbour_ip]
            ):
                parents[neighbour_ip] = min_dist_ip
                distances[neighbour_ip] = distances[min_dist_ip] + neighbour_data["ad"]

    # Construct path from the dest_ip_subnet to the src_ip_subnet
    curr_ip = dest_ip_subnet
    path = []
    while curr_ip:
        path.append(curr_ip)
        curr_ip = parents[curr_ip]

    # Reverse and return the path
    path.reverse()
    return path


# ------------------------------
# DO NOT MODIFY BELOW THIS LINE
# ------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)


def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")


def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)


def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1
    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
