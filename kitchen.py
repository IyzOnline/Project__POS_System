import socket
import json
import threading

HOST = "192.168.1.45"
PORT = 67

def send_json(connection, data):
    connection.sendall((json.dumps(data) + "\n").encode())

orders = []

def listen(connection):
    global orders
    buffer = ""

    while True:
        data = connection.recv(1024)
        if not data:
            break


        buffer += data.decode()

        while "\n" in buffer:
            raw, buffer = buffer.split("\n", 1)
            message = json.loads(raw)

            if message["type"] == "order":
                orders.append(message["text"])
                print(f"\n new order: {message['text']}")
                print("type 'done' to mark the lastest order as completed \n")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST,PORT))
client.sendall(b"kitchen")

threading.Thread(target=listen, args=(client,), daemon=True).start()

print("Kitchen connected. Waiting for orders")

while True:
    command = input("> ")
    
    if command == "done" and orders:
        completed = orders.pop(0)
        send_json(client, {
            "type" : "complete",
            "text" : completed
        })
        print(f"mark complete: {completed}")
