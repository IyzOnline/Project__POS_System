import socket
import json
import threading

HOST = "192.168.1.45"
PORT = 67

def send_json(connection, data):
    connection.sendall((json.dumps(data) + "\n").encode())

def listen(connection):
    buffer = ""
    while True:
        data = connection.recv(1024)
        if not data:
            break


        buffer += data.decode()

        while "\n" in buffer:
            raw, buffer = buffer.split("\n", 1)
            message = json.loads(raw)

            if message["type"] == "complete":
                print(f"\n order complete: {message['text']}\n")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.sendall(b"cashier")

threading.Thread(target=listen, args=(client,), daemon=True).start()

print("Cashier connected. \nType oders below: ")

while True:
    text = input("ORDER > ")

    if text.lower() == "exit":
        break

    send_json(client, {
        "type" : "order",
        "text" : text
    })

client.close()
