import socket
import threading

DISCOVERY_SERVER = 'discovery'
DISCOVERY_PORT = 5000

def send_to_server(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((DISCOVERY_SERVER, DISCOVERY_PORT))
        s.sendall(command.encode())
        response = s.recv(4096).decode()
        print(f"Server response:\n{response}")

def start_listener(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen()
    print(f"Listening for incoming messages on port {port}")
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_peer_connection, args=(conn, addr), daemon=True).start()

def handle_peer_connection(conn, addr):
    try:
        data = conn.recv(1024).decode()
        if data:
            print(f"\n[Message from {addr}]: {data}\n> ", end="")
    except Exception as e:
        print(f"[Error receiving message from {addr}]: {e}")
    finally:
        conn.close()

def send_message():
    target_ip = input("Enter target peer IP: ").strip()
    message = input("Enter message:").strip()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, 5001))
            s.sendall(message.encode())
        print(f"Sent message to {target_ip}:5001")
    except Exception as e:
        print(f"[Error sending message]: {e}")    
    return    

if __name__ == "__main__":
    name = input("Enter Username:")
    send_to_server(f"REGISTER {name}")

    listener_thread = threading.Thread(target=start_listener, args=(5001,), daemon=True)
    listener_thread.start()

    while True:
        cmd = input("Enter command (LIST / SEND / EXIT): ").strip()
        if cmd.upper() == "EXIT":
            break
        elif cmd.upper() == "LIST":
            send_to_server("LIST")
        elif cmd.upper() == "SEND":
            send_message()