import socket
import threading
import json
import uuid

HOST = "192.168.1.45"
PORT = 67

kitchens = []
cashiers = []

order = {}

def send_json(connection, data):
    connection.sendall((json.dumps(data) + "\n").encode())

def broadcast_to_cashiers(message):
    for cashier in cashiers:
        send_json(cashier, message)

def handle_client(connection, address):
    print(f"[CONNECTED]{address}")

    role = connection.recv(1024).decode()

    if role == "kitchen":
        kitchens.append(connection)
        print(f"[REGISTERED KITCHEN] {address}")

    elif role == "cashier":
        cashiers.append(connection)
        print(f"[REGISTERED CASHIER] {address}")

        for order_id, info in orders.items():
            send_json(connection, {"type" : "update", "order_id" : order_id, "text" : info["text"], "status" : info["status"]})

    else:
        connection.close()
        return()

    buffer = ""

    while True:
        try:
            data = connection.recv(1024)
            if not data:
                break
            
            buffer += data.decode()
            while "\n" in buffer:
                raw, buffer = buffer.split("\n", 1)
                message = json.loads(raw)

                message_type = message["type"]


                if role == "cashier" and message_type == "order":
                    order_id = str(uuid.uuid4())
                    order[order_id] = {"text" : message["text"], "status" : "PREPARING"}
                    print(f"[ORDER] {orders[order_id]}")

                    for kitchen in kitchens:
                        send_json(kitchen, {"type" : "new_order", "order_id" : order_id, "text" : message["text"], "status" : "PREPARING"})

                    broadcast_to_cashiers({"type" : "update", "order_id" : order_id, "text" : message["text"], "status" : "PREPARING"})


                elif role == "kitchen" and message_type == "update":
                    order_id = message["order_id"]
                    if order_id in orders:
                        orders[order_id]["status"] = message["status"]
                    print(f"[UPDATE] {orders[order_id]}")

                    broadcast_to_cashiers({"type" : "update", "order_id" : order_id, "text" : orders[order_id][text], "status" : orders[order_id]["status"]})
                    
        except ConnectionResetError:
            break

    print(f"[DISCONNECTED] {address}")
    connection.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER STARTED] {HOST}:{PORT}")

    while True:
        connection, address = server.accept()
        threading.Thread(target=handle_client, args=(connection, address), daemon=True).start()

if __name__ == "__main__":
    start()
