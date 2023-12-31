import socket
import threading
import queue
import csv
import time

HEADER = 64
PORT = 5055
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
BROADCAST_ADDRESS = '127.0.0.1'
BROADCAST_PORT = 5002
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5000

active_connections = []



def send_broadcast_message(msg):
    broadcast_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_SOCK.sendto(msg.encode(), (BROADCAST_ADDRESS, BROADCAST_PORT))
    broadcast_SOCK.close()

    
    with open("network_monitor.csv", 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        timestamp = int(time.time())
        row = ['Broadcast', timestamp, SERVER, BROADCAST_ADDRESS, PORT, BROADCAST_PORT, 'TCP', len(msg) * 4, 'flags']
        csvwriter.writerow(map(lambda x: [x], row))

def send_multicast_message(msg):
    multicast_SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    multicast_SOCK.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    multicast_SOCK.sendto(msg.encode(), (MULTICAST_GROUP, MULTICAST_PORT))

    multicast_SOCK.close()

    with open("network_monitor.csv", 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        timestamp = int(time.time())
        row = ['Multicast', timestamp, SERVER, MULTICAST_GROUP, PORT, MULTICAST_PORT, 'UDP', len(msg) * 4, 'flags']
        csvwriter.writerow(map(lambda x: [x], row))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    active_connections.append(conn)
    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
            
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                print(f"[{addr}] {msg}")
                conn.send("Task sent to client".encode(FORMAT))
        except ConnectionResetError:
            connected = False
    active_connections.remove(conn)
    conn.close()


def start():

    master_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_server.bind(ADDR)
    master_server.listen(5)
    filename = "network_monitor.csv"
    type = ""
    fields = ['Type', 'Time(ms)', 'Source_Ip', 'Destination_Ip', 'Source_Port', 'Destination_Port', 'Protocol',
              'Length (bytes)',  '']

    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
    print(f"[LISTENING] Master Server is listening on {SERVER}")
    print("How would you like to communciate?")
    print("[1] Broadcast protocol")
    print("[2] Multicast Protocol")
    option = input()
    if option == '1':
        message = input("Enter a messege for broadcast\n")
        type = "Broadcast"
        send_broadcast_message(message)
    elif option == '2':
        message = input("Enter a messge for multicast\n")
        type = "Multicast"
        send_multicast_message(message)
    else:
        print("PLease enter a valid option")
    while True:
        conn, addr = master_server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {len(active_connections)}")




if __name__ == "__main__":
    start()

