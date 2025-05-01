#!/usr/bin/env python3
import socket
import threading
import json
import redis

# Redis connection (hostname “redis” matches your docker-compose service)
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

HOST = '0.0.0.0'
PORT = 6000

def handle_client(conn, addr):
    try:
        raw = conn.recv(4096).decode()
        cmd = json.loads(raw)
        typ   = cmd.get("type", "").lower()
        topic = cmd.get("topic", "")
        peer  = cmd.get("from", "")
        resp  = {}

        if typ == "subscribe":
            # add peer to topic’s subscriber set
            r.sadd(f"subscribers:{topic}", peer)
            resp = {"status":"ok", "detail":f"{peer} subscribed to {topic}"}

        elif typ == "unsubscribe":
            r.srem(f"subscribers:{topic}", peer)
            resp = {"status":"ok", "detail":f"{peer} unsubscribed from {topic}"}

        elif typ == "publish":
            message = cmd.get("message", "")
            # publish the message to all redis pub/sub listeners
            count = r.publish(topic, message)
            resp = {"status":"ok",
                    "detail":f"published to {count} subscribers"}

        elif typ == "list_topics":
            keys = r.keys("subscribers:*")
            topics = [k.split(":",1)[1] for k in keys]
            resp = {"status":"ok", "topics": topics}

        elif typ == "list_listeners":
            members = list(r.smembers(f"subscribers:{topic}"))
            resp = {"status":"ok", "listeners": members}

        else:
            resp = {"status":"error", "detail":"unknown command"}

        conn.sendall(json.dumps(resp).encode())

    except Exception as e:
        err = {"status":"error", "detail":str(e)}
        conn.sendall(json.dumps(err).encode())

    finally:
        conn.close()

def start_server():
    print(f"[PubSub] Listening on port {PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client,
                         args=(conn, addr),
                         daemon=True).start()

if __name__ == "__main__":
    start_server()
