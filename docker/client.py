import socket
import threading
import json

DISCOVERY_SERVER = 'discovery'
DISCOVERY_PORT   = 5000

PUBSUB_SERVER = 'pubsub'
PUBSUB_PORT   = 6000

LISTENER_PORT = 5001

def send_to_discovery(cmd: str):
    """Send a plain-text command to the discovery server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((DISCOVERY_SERVER, DISCOVERY_PORT))
        s.sendall(cmd.encode())
        resp = s.recv(4096).decode()
    print(f"[Discovery] {resp}")

def send_to_pubsub(payload: dict):
    """Send a JSON command to the pubsub server and print JSON response."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PUBSUB_SERVER, PUBSUB_PORT))
        s.sendall(json.dumps(payload).encode())
        resp = s.recv(4096).decode()
    try:
        data = json.loads(resp)
        print(f"[PubSub] {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        print(f"[PubSub] {resp}")

def start_discovery_listener(port: int):
    """A simple listener thread for incoming peer-to-peer messages."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen()
    print(f"[Listener] Listening on port {port}")
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()

def handle_peer(conn: socket.socket, addr):
    """Print any direct P2P messages from another peer."""
    try:
        data = conn.recv(1024).decode().strip()
        if data:
            print(f"\n[Message from {addr}] {data}\n> ", end='')
    finally:
        conn.close()

def send_direct_message():
    """Prompt for IP, message, and send it peer-to-peer."""
    ip = input("Target peer IP: ").strip()
    port = int(input("Target peer port: ").strip())
    msg = input("Your message: ").strip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(msg.encode())
    print(f"[Sent] → {ip}:{port}")

if __name__ == "__main__":
    # 1) Register with discovery
    name = input("Enter your username: ").strip()
    send_to_discovery(f"REGISTER {name}")

    # 2) Start the background listener thread for P2P messages
    listener = threading.Thread(
        target=start_discovery_listener, args=(LISTENER_PORT,), daemon=True
    )
    listener.start()

    # 3) Main command loop
    HELP = """
Commands:
  DISCOVERY
    - REGISTER <name>
    - LIST

  PUBSUB
    - SUBSCRIBE <topic>
    - UNSUBSCRIBE <topic>
    - PUBLISH <topic> <message>
    - LIST_TOPICS
    - LIST_LISTENERS <topic>

  P2P
    - SEND  (direct peer-to-peer message)

  EXIT
    - Exit the client
"""
    print(HELP)

    while True:
        raw = input("> ").strip()
        if not raw:
            continue
        parts = raw.split()
        cmd = parts[0].upper()

        if cmd == "EXIT":
            break

        # Discovery commands
        elif cmd == "REGISTER" or cmd == "LIST":
            send_to_discovery(raw)

        # Pub/Sub commands
        elif cmd in ("SUBSCRIBE", "UNSUBSCRIBE"):
            topic = parts[1]
            send_to_pubsub({"type": cmd.lower(), "topic": topic, "from": name})

        elif cmd == "PUBLISH":
            topic = parts[1]
            message = " ".join(parts[2:])
            send_to_pubsub({
                "type": "publish",
                "topic": topic,
                "from": name,
                "message": message
            })

        elif cmd == "LIST_TOPICS":
            send_to_pubsub({"type": "list_topics", "from": name})

        elif cmd == "LIST_LISTENERS":
            topic = parts[1]
            send_to_pubsub({
                "type": "list_listeners",
                "topic": topic,
                "from": name
            })

        # Peer-to-peer direct messaging
        elif cmd == "SEND":
            send_direct_message()

        else:
            print("Unknown command. Type HELP for usage.")
