for i in range(10):
    file_name_1 = f"tcp_data/tcp_addrs_{i}.txt"
    file_name_2 = f"tcp_data/tcp_addrs_{i}.dat"
    if i < 5:
        print("PASS")
    else:
        print("FAIL")
