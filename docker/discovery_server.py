import socket
import threading

clients = set()
HOST = '0.0.0.0'
PORT = 5000

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode().strip()
        parts = data.split()
        cmd = parts[0].upper()
        if cmd == "REGISTER":
            name = parts[1]
            client_ip = addr[0]
            clients.add((client_ip, name))
            conn.sendall(f"Registered {client_ip} as {name}\n".encode())

        elif cmd == "LIST":
            client_list = "\n".join([f"{ip} ({name})" for ip, name in clients])
            conn.sendall(client_list.encode())

        else:
            conn.sendall("Invalid command.\n".encode())

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        conn.close()

def start_server():
    print(f"[!] Discovery Server running on port {PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
