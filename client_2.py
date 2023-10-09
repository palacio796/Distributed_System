import socket
import sys
import threading

HEADER = 10
PORT = 5053  # Adjust the port number
BROADCAST_PORT = 5002
MULTICAST_PORT = 5000
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

def recv_broadcast_message():
    broadcast_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_SOCK.bind(ADDR)
    while True:
        data, addr = broadcast_SOCK.recvfrom(1024)
        print(f"[BROADCAST RECEIVED] {data.decode()} from {addr}")

def recv_multicast_message():
    multi_address = '224.1.1.1'
    multi_interface = SERVER
    multicast_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    multicast_SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    multicast_SOCK.bind((multi_address, MULTICAST_PORT))
    multicast_SOCK.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multi_address) + socket.inet_aton(multi_interface))
    while True:
        data, addr = multicast_SOCK.recvfrom(1024)
        print(f"[MULTICAST RECEIVED] {data.decode()} from {addr}")

def start():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(ADDR)
    client.listen(5)
    print("[Hello! This is Server 2]")
    print(f"Client Server is running on address: {SERVER} PORT: {PORT}..")
    while True:
        conn, addr = client.accept()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    multicast_thread = threading.Thread(target=recv_multicast_message)
    multicast_thread.start()

    broadcast_thread = threading.Thread(target=recv_broadcast_message)
    broadcast_thread.start()

    start()