import socket
import json
import threading
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk
from pathlib import Path

root = tk.Tk()
root.geometry("500x500")
receivedOrderInfo = {}
clientConnection = None
serverConnected = False

data = {
  1: {
    "Hamburger": 5,
    "Fries": 5,
    "Pizza": 1
  }
}

def initCashierMode() :
  cashierModeBtn.config(state=tk.DISABLED)
  kitchenModeBtn.config(state=tk.DISABLED)
  statusLabel.config(text="Status: Cashier is Connecting to Kitchen...")
  cashierMode = tk.Frame(root, bg="black")
  cashierMode.pack()
  startCashierThread()

def startCashierThread() :
  serverThread = threading.Thread(target=runCashierServer)
  serverThread.daemon = True
  serverThread.start()
  checkServerConnection()

def runCashierServer() :
    global clientConnection, serverConnected
    
    SERVER_IP = '0.0.0.0'
    PORT = 65432
    try :
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        serverSocket.bind((SERVER_IP, PORT))
        serverSocket.listen()
        print(f"listening")
        print(socket.gethostbyname(socket.gethostname()))

        conn, addr = serverSocket.accept()

        clientConnection = conn
        serverConnected = True

        if clientConnection :
          print("Connected to Kitchen!")
          try :
            orderInfoToBytes = json.dumps(data).encode('utf-8')
            clientConnection.sendall(orderInfoToBytes)
          except Exception as e :
            print(f"Error sending data: {e}")
    except Exception as e :
      print(f"Server Error: {e}")

def checkServerConnection():
  if serverConnected:
      kitchenModeBtn.config(state=tk.NORMAL)
      cashierModeBtn.config(state=tk.NORMAL)
      statusLabel.config(text="Status: Kitchen and Cashier are Connected.", fg="green")
  else:
      root.after(100, checkServerConnection)

def initKitchenMode() :
  cashierModeBtn.config(state=tk.DISABLED)
  kitchenModeBtn.config(state=tk.DISABLED)
  statusLabel.config(text="Status: Kitchen is Connecting to Cashier...")
  kitchenMode = tk.Frame(root, bg="green")
  kitchenMode.pack()
  startKitchenThread()

def startKitchenThread() :
  serverThread = threading.Thread(target=runKitchenClient)
  serverThread.daemon = True
  serverThread.start()
  checkServerConnection()

def runKitchenClient() :
    load_dotenv()
    targetIP = os.getenv("IP_ADDRESS")
    targetPORT = 65432
    print("Horray!")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
      print("Hmmm")
      try :
        print("Start connection")
        clientSocket.connect(('10.0.0.1', 65432))
        print("Connected to Cashier!")

        while True :
          packet = clientSocket.recv(4096)

          if not packet :
            print("Server disconnected.")
            break

          receivedOrderInfo = json.loads(packet.decode('utf-8'))

          print(f"RECEIVED ORDER: {receivedOrderInfo}")
      except ConnectionRefusedError :
        print("Could not connect. Is the server listening?")
      except Exception as e :
        print(f"An error occurred: {e}")


cashierModeBtn = tk.Button(root, text="You're in Cashier Mode - Connect to Kitchen", command=initCashierMode)
kitchenModeBtn = tk.Button(root, text="You're in Kitchen Mode - Connect to Cashier", command=initKitchenMode)
statusLabel = tk.Label(root, text="Status: Kitchen and Cashier are disconnected.")

cashierModeBtn.pack()
kitchenModeBtn.pack()
statusLabel.pack()


root.mainloop()
