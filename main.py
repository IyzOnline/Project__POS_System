import tkinter as tk
from tkinter import ttk
import sqlite3
from pathlib import Path
import sys
import datetime
import socket
import json
import threading
import os
from dotenv import load_dotenv

class App(tk.Tk) :
  def __init__(self):
    super().__init__()
    self.title("POS System")
    self.minsize(960, 540)

    self.initStyles()
    self.initializeExitFS()
    self.initDB()

    self.clientConnection = None
    self.__receivedOrderInfo = None
    self.__MenuItemRecords = {}
    self.__MenuItemInstances = {}
    self.__SavedItemQuantity = {}
    self.__ReceiptListInstances = {}
    self.__OrderRecords = {}
    self.__kitchenOrderInstances = {}
    self.total = tk.DoubleVar(value=0)
    self.order = Order(self.__MenuItemInstances, self.__conn, self.__cursor, self.commitDBChanges, self.resetForNewOrder)

    self.initializeSidebar()
    self.initializeMainFrame()
    self.initCashierMode()

#Networking
  def connectToKitchen(self) :
    self.connectToKitchenBtn.config(state=tk.DISABLED)
    self.connectionLbl.config(text="Status: Connecting to Kitchen...", fg="orange")
    self.startServerThread()

  def connectToCashier(self) :
    self.connectToCashierBtn.config(state=tk.DISABLED)
    self.startClientThread()

  def startServerThread(self) :
    serverThread = threading.Thread(target=self.runCashierServer)
    serverThread.daemon = True
    serverThread.start()
    self.checkServerConnection()

  def runCashierServer(self) :
    SERVER_IP = '0.0.0.0'
    PORT = 65432
    try :
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((SERVER_IP, PORT))
        serverSocket.listen()
        print(f"listening")
        print(socket.gethostbyname(socket.gethostname()))

        conn, addr = serverSocket.accept()

        self.clientConnection = conn
        self.serverConnected = True
        print("Connected to Kitchen!")
    except Exception as e :
      print(f"Server Error: {e}")

  def checkServerConnection(self):
    if self.serverConnected:
        self.connectToKitchenBtn.config(state=tk.NORMAL)
        self.connectionLbl.config(text="Status: Connected to Kitchen.", fg="green")
    else:
        self.after(100, self.checkServerConnection)

  def startClientThread(self) :
    serverThread = threading.Thread(target=self.runKitchenClient)
    serverThread.daemon = True
    serverThread.start()

  def runKitchenClient(self) :
    load_dotenv()
    targetIP = os.getenv("IP_ADDRESS")
    targetPORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
      try :
        clientSocket.connect((targetIP, targetPORT))
        print("Connected to Cashier!")

        while True :
          packet = clientSocket.recv(4096)

          if not packet :
            print("Server disconnected.")
            break

          self.__receivedOrderInfo = json.loads(packet.decode('utf-8'))

          print(f"RECEIVED ORDER: {self.__receivedOrderInfo}")
      except ConnectionRefusedError :
        print("Could not connect. Is the server listening?")
        self.connectToCashierBtn.config(state=tk.NORMAL)
      except Exception as e :
        print(f"An error occurred: {e}")
    
#UI Implementation
  def initStyles(self) :
    self.style = ttk.Style()
    self.style.configure("Cell.TLabel",
                    width=50,
                    relief="solid", 
                    borderwidth=2, 
                    bg="lightgray",
                    wraplength=200, 
                    justify=tk.CENTER
                    )
    
    self.style.configure("Cell.TButton",
                    relief="solid", 
                    width=50,
                    borderwidth=2, 
                    bg="lightgray",
                    bordercolor = "red"
                    )
    
    self.style.configure("OrderList.TFrame",
                    borderwidth=10, 
                    background="lightgray",
                    bordercolor="black"
                    )

  def initializeExitFS(self) :
    self.attributes('-fullscreen', True)
    self.bind('<Escape>', self.exit_fullscreen)

  def exit_fullscreen(self, event=None) :
    self.attributes('-fullscreen', False)

  def transitionFrame(self, initNewPage) :
    self.mainFrame.destroy()
    self.clearReceiptInstances()
    self.initializeMainFrame()
    initNewPage()

  #Main Frame
  def initializeMainFrame(self) :
    self.mainFrame = tk.Frame(self, bg="#ffffff")
    self.mainFrame.pack(side=tk.LEFT, expand=True, fill="both")

  #Cashier Mode
  def initCashierMode(self):
    self.menuFrame = tk.Frame(self.mainFrame, bg="#49a3df")
    self.receiptFrame = tk.Frame(self.mainFrame, bg="#5faee3")

    self.menuFrame.place(relx=0.0, rely=0, relwidth=0.82, relheight=1.0)
    self.receiptFrame.place(relx=0.82, rely=0, relwidth=0.18, relheight=1.0)

    self.initializeMenuArea()
    self.initializeReceipt()
  
  #Kitchen Mode
  def initKitchenMode(self) :
    kitchenModeFrame = tk.Frame(self.mainFrame, background="#333333")
    kitchenModeFrame.pack(expand=True, fill="both", padx=2, pady=2)
    
    kitchenModeLbl = ttk.Label(kitchenModeFrame, text="KITCHEN MODE")
    kitchenModeLbl.pack(pady=20)

    self.kitchenOrdersFrame = tk.Frame(kitchenModeFrame, background="#4d4d4d", highlightbackground="white", highlightthickness=2)
    self.kitchenOrdersFrame.pack(expand=True, fill="both", padx=10, pady=10)

    self.connectToCashierBtn = ttk.Button(kitchenModeFrame, text="Connect to Cashier PC", command=lambda: self.connectToCashier())
    self.connectToCashierBtn.pack(pady=20, anchor="center")

    if not self.kitchenOrdersFrame.winfo_children():
      self.tempKitchenOrderLbl = ttk.Label(self.kitchenOrdersFrame, text="Waiting for orders...")
      self.tempKitchenOrderLbl.pack()
      #self.kitchenOrdersFrame.grid_columnconfigure(0, weight=1)
      #tempKitchenOrderLbl.grid(column=0, row=0, pady=10)

  def displayKitchenOrderInstance(self) :
    if self.tempKitchenOrderLbl :
      self.tempKitchenOrderLbl.destroy()
    
    instanceFrame = tk.Frame(self.kitchenOrdersFrame, width=200, height=300)

    for orderNum, orderItems in self.__receivedOrderInfo.items() :
      tk.Label(instanceFrame, text=f"Order {orderNum}").pack()
      for itemName, itemData in orderItems.items():
        itemRowFrame = tk.Frame(instanceFrame)
        name = itemData[0]
        quantity = itemData[2]
        tk.Label(itemRowFrame, text=name).pack(side="left", padx=10)
        tk.Label(itemRowFrame, text=quantity).pack(side="right", pady=10)
        itemRowFrame.pack(fill="x", expand=True)

    buttonFrame = tk.Frame(instanceFrame)
    buttonFrame.pack(fill="x", expand=True)

    tk.Button(buttonFrame, text="Completed", command=instanceFrame.destroy).pack(side="left", padx=10)
    tk.Button(buttonFrame, text="Cancelled", command=instanceFrame.destroy).pack(side="right", pady=10)

    instanceFrame.pack()

  #History Page
  def initHistoryPage(self) :
    historyPageFrame = tk.Frame(self.mainFrame, padx=10, pady=10, background="#ffffff")
    historyPageFrame.pack()

    historyTableLbl = ttk.Label(historyPageFrame, text="Order History")
    historyTableLbl.pack()

    self.displayHistoryTableColumns(historyPageFrame)
    self.displayHistoryTable(historyPageFrame)

  def displayHistoryTableColumns(self, parent):
    columns = tk.Frame(parent)

    orderIDCol = ttk.Label(columns, text="Order ID", style="Cell.TLabel", anchor="center")
    dateCol = ttk.Label(columns, text="Date and Time", style="Cell.TLabel", anchor="center")
    nameCol = ttk.Label(columns, text="Name", style="Cell.TLabel", anchor="center")
    categoryCol = ttk.Label(columns, text="Category", style="Cell.TLabel", anchor="center")
    priceCol = ttk.Label(columns, text="Price", style="Cell.TLabel", anchor="center")
    quantityCol = ttk.Label(columns, text="Quantity", style="Cell.TLabel", anchor="center")
    totalCol = ttk.Label(columns, text="Total", style="Cell.TLabel", anchor="center")

    columns.grid_columnconfigure(0, weight=1)
    columns.grid_columnconfigure(1, weight=1)
    columns.grid_columnconfigure(2, weight=1)
    columns.grid_columnconfigure(3, weight=1)
    columns.grid_columnconfigure(4, weight=1)
    columns.grid_columnconfigure(5, weight=1)
    columns.grid_columnconfigure(6, weight=1)


    orderIDCol.grid(column=0, row=0, sticky="nsew")
    dateCol.grid(column=1, row=0, sticky="nsew")
    nameCol.grid(column=2, row=0, sticky="nsew")
    categoryCol.grid(column=3, row=0, sticky="nsew")
    priceCol.grid(column=4, row=0, sticky="nsew")
    quantityCol.grid(column=5, row=0, sticky="nsew")
    totalCol.grid(column=6, row=0, sticky="nsew")
    
    columns.pack(fill="x")

  def displayHistoryTable(self, parent):
    self.reqForOrderHistory()
    if not self.__OrderRecords:
      print("No orders recorded")
      return

    for key, orderData in self.__OrderRecords.items():
      for orderItemKey, orderItemData in orderData["items"].items():
        orderItemRow = tk.Frame(parent)

        orderIDCol = ttk.Label(orderItemRow, text=orderData["orderID"], style="Cell.TLabel", anchor="center")
        dateCol = ttk.Label(orderItemRow, text=orderData["date"].strftime("%Y-%m-%d - %H:%M:%S %p"), style="Cell.TLabel", anchor="center")
        nameCol = ttk.Label(orderItemRow, text=orderItemData["name"], style="Cell.TLabel", anchor="center")
        categoryCol = ttk.Label(orderItemRow, text=orderItemData["category"], style="Cell.TLabel", anchor="center")
        priceCol = ttk.Label(orderItemRow, text=f"₱{orderItemData['price']:.2f}", style="Cell.TLabel", anchor="center")
        quantityCol = ttk.Label(orderItemRow, text=orderItemData["quantity"], style="Cell.TLabel", anchor="center")

        total = orderItemData['quantity'] * orderItemData['price']

        totalCol = ttk.Label(orderItemRow, text=f"₱{total:.2f}", style="Cell.TLabel", anchor="center")

        for i in range(7):
           orderItemRow.grid_columnconfigure(i, weight=1)

        orderIDCol.grid(column=0, row=0, sticky="nsew")
        dateCol.grid(column=1, row=0, sticky="nsew")
        nameCol.grid(column=2, row=0, sticky="nsew")
        categoryCol.grid(column=3, row=0, sticky="nsew")
        priceCol.grid(column=4, row=0, sticky="nsew")
        quantityCol.grid(column=5, row=0, sticky="nsew")
        totalCol.grid(column=6, row=0, sticky="nsew")
        
        orderItemRow.pack(fill="x")

  #Sidebar
  def initializeSidebar(self) :
    self.sidebarFrame = tk.Frame(self, bg="#3498db")
    self.sidebarFrame.pack(side=tk.LEFT, fill="y")

    cashierPageBtn = ttk.Button(self.sidebarFrame, text="Cashier Mode", command=lambda: self.transitionFrame(self.initCashierMode))
    kitchenPageBtn = ttk.Button(self.sidebarFrame, text="Kitchen Mode", command=lambda: self.transitionFrame(self.initKitchenMode))
    historyPageBtn = ttk.Button(self.sidebarFrame, text="History Page", command=lambda: self.transitionFrame(self.initHistoryPage))

    cashierPageBtn.pack(padx=5, pady=5)
    kitchenPageBtn.pack(padx=5, pady=5)
    historyPageBtn.pack(padx=5, pady=5)

  #Menu
  def initializeMenuArea(self) :
    self.menuSearch = tk.Frame(self.menuFrame, bg="#333333", padx=10, pady=10)
    self.menuTable = tk.Frame(self.menuFrame, bg="#4d4d4d", padx=20, pady=20)
    self.menuLowerBtns = tk.Frame(self.menuFrame, bg="#333333", padx=10, pady=10)

    self.menuSearch.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)
    self.menuTable.place(relx=0, rely=0.1, relwidth=1.0, relheight=0.8)
    self.menuLowerBtns.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)

    createBtn = ttk.Button(self.menuLowerBtns, text="Add Menu Item", command=lambda: self.transitionFrame(self.initCreateMIPage))
    deleteBtn = ttk.Button(self.menuLowerBtns, text="Delete Menu Item", command=self.cantDeletePopUp)
    self.connectToKitchenBtn = ttk.Button(self.menuLowerBtns, text="Connect to Kitchen PC", command = lambda: self.connectToKitchen())
    self.connectionLbl = tk.Label(self.menuLowerBtns, text="Status: Not Connected to Kitchen...", fg="red")

    createBtn.pack(side=tk.LEFT, padx=5, pady=5)
    deleteBtn.pack(side=tk.LEFT, padx=5, pady=5)
    self.connectToKitchenBtn.pack(side=tk.LEFT, padx=5, pady=5)
    self.connectionLbl.pack(side=tk.LEFT, padx=5, pady=5)

    self.initMenuTableColumns()
    self.initializeMenuItems(None)
    self.initializeSearchArea()

  def initializeSearchArea(self) :
    self.searchValue = tk.StringVar()
    self.searchValue.trace_add("write", lambda *args: self.searchThroughRecords(self.searchValue.get()))
    searchEntry = ttk.Entry(self.menuSearch, textvariable=self.searchValue, width=60, font=("Helvetica", 14))
    searchEntry.pack(expand=True)

  def searchThroughRecords(self, searchString) :
    print(f"Current search string: {searchString}")
    for row in self.menuTable.winfo_children() :
      row.destroy()
    self.initializeMenuItems(searchString)
    print("Search complete.")

  def initMenuTableColumns(self) :
    columns = tk.Frame(self.menuTable)
    
    nameCol = ttk.Label(columns, text="Name", style="Cell.TLabel", anchor="center")
    priceCol = ttk.Label(columns, text="Price", style="Cell.TLabel", anchor="center")
    categoryCol = ttk.Label(columns, text="Category", style="Cell.TLabel", anchor="center")
    addCol = ttk.Label(columns, text="Add to Order", style="Cell.TButton", anchor="center")

    columns.grid_columnconfigure(0, weight=1)
    columns.grid_columnconfigure(1, weight=1)
    columns.grid_columnconfigure(2, weight=1)
    columns.grid_columnconfigure(3, weight=1)

    nameCol.grid(column=0, row=0, sticky="nsew")
    priceCol.grid(column=1, row=0, sticky="nsew")
    categoryCol.grid(column=2, row=0, sticky="nsew")
    addCol.grid(column=3, row=0, sticky="nsew")
    
    columns.pack(fill="x")

  def initializeMenuItems(self, searchString) :
    self.empty = None
    if (len(self.__MenuItemRecords) == 0):
      if not self.initMenuItemsfromDB():
        self.empty = tk.Label(self.menuTable, text="No records exist.")
        self.empty.pack(expand=True, fill="both")
    #else :
    #  if (self.empty) :
    #   self.empty.destroy()
    
    for recordName, recordValues in self.__MenuItemRecords.items():
      if searchString and searchString.strip().lower() not in recordValues["name"].lower() :
        continue

      initialQuantity = 0
      if recordName in self.__SavedItemQuantity :
        initialQuantity = self.__SavedItemQuantity[recordName].get()

      item = MenuItem(
        self.menuTable, 
        self, recordValues, 
        self.__MenuItemInstances, 
        self.updateReceiptArea, 
        initialQuantity
      )

      self.__SavedItemQuantity[recordName] = item.quantity
      item.pack(fill="x")
      
  def initCreateMIPage(self) :
    def passData():
      if not (nameEntry.get() and priceEntry.get() and categoryEntry.get()) :
        return None
      
      name = nameEntry.get().strip()
      price = 0
      category = categoryEntry.get().strip()

      try : 
        price = float(priceEntry.get())
      except ValueError :
        return "ValueError"
      
      data = (name, price, category)

      nameEntry.delete(0, tk.END)
      priceEntry.delete(0, tk.END)
      categoryEntry.delete(0, tk.END)

      print(data)
      return data

    createMIFrame = tk.Frame(self.mainFrame, background="#333333")
    createMIFrame.pack(expand=True, fill="both", anchor=tk.CENTER)

    contentFrame = tk.Frame(createMIFrame, background="#4d4d4d", padx=10, pady=10)
    contentFrame.pack(expand=True, anchor="center")

    nameEntry = ttk.Entry(contentFrame, width=30, font=("Helvetica", 14))
    priceEntry = ttk.Entry(contentFrame, width=30, font=("Helvetica", 14))
    categoryEntry = ttk.Entry(contentFrame, width=30, font=("Helvetica", 14))

    saveBtn = ttk.Button(contentFrame, text="Save to DB", command=lambda: self.addMenuItem(passData()))
    returnBtn = ttk.Button(contentFrame, text="Return to Menu", command=lambda: self.transitionFrame(self.initCashierMode))

    ttk.Label(contentFrame, text="- Name -").pack(anchor="center", pady=5)
    nameEntry.pack(anchor="center", pady=5)
    ttk.Label(contentFrame, text="- Price -").pack(anchor="center", pady=5)
    priceEntry.pack(anchor="center", pady=5)
    ttk.Label(contentFrame, text="- Category -").pack(anchor="center", pady=5)
    categoryEntry.pack(anchor="center", pady=5)

    saveBtn.pack(anchor="center", pady=5)
    returnBtn.pack(anchor="center", pady=5)

  def initDeleteMIPage(self) :
    deleteMIFrame = tk.Frame(self.mainFrame, background="#333333")
    deleteMIFrame.pack(expand=True, fill="both", anchor=tk.CENTER)

    contentFrame = tk.Frame(deleteMIFrame, background="#4d4d4d", padx=10, pady=10)
    contentFrame.pack(expand=True, anchor="center")

    deleteTableLbl = ttk.Label(contentFrame, text="Deletion Table")
    deleteTableLbl.pack(expand=True, anchor="center", pady=10)

    self.initDeleteMIColumns(contentFrame)

    for recordName, recordValues in self.__MenuItemRecords.items():
      itemRow = tk.Frame(contentFrame)

      itemName = ttk.Label(itemRow, text=recordValues["name"], style="Cell.TLabel", anchor="center")
      itemPrice = ttk.Label(itemRow, text=recordValues["price"], style="Cell.TLabel", anchor="center")
      itemCategory = ttk.Label(itemRow, text=recordValues["category"], style="Cell.TLabel", anchor="center")
      itemDeleteBtn = ttk.Button(itemRow, text="DELETE", style="Cell.TButton", command= lambda rowWidget=itemRow, name=recordName: self.deletionConfirmPopUp(rowWidget, name))

      itemRow.grid_columnconfigure(0, weight=1)
      itemRow.grid_columnconfigure(1, weight=1)
      itemRow.grid_columnconfigure(2, weight=1)
      itemRow.grid_columnconfigure(3, weight=1)

      itemName.grid(column=0, row=0, sticky="nsew")
      itemPrice.grid(column=1, row=0, sticky="nsew")
      itemCategory.grid(column=2, row=0, sticky="nsew")
      itemDeleteBtn.grid(column=3, row=0, sticky="nsew")
      
      itemRow.pack(fill="x")

    returnBtn = ttk.Button(contentFrame, text="Return to Menu", command=lambda: self.transitionFrame(self.initCashierMode))
    returnBtn.pack(anchor="center", pady=5)

  def initDeleteMIColumns(self, parent):
    columns = tk.Frame(parent)
    
    nameCol = ttk.Label(columns, text="Name", style="Cell.TLabel", anchor="center")
    priceCol = ttk.Label(columns, text="Price", style="Cell.TLabel", anchor="center")
    categoryCol = ttk.Label(columns, text="Category", style="Cell.TLabel", anchor="center")
    deleteCol = ttk.Label(columns, text="Delete Menu Item", style="Cell.TButton", anchor="center")

    columns.grid_columnconfigure(0, weight=1)
    columns.grid_columnconfigure(1, weight=1)
    columns.grid_columnconfigure(2, weight=1)
    columns.grid_columnconfigure(3, weight=1)

    nameCol.grid(column=0, row=0, sticky="nsew")
    priceCol.grid(column=1, row=0, sticky="nsew")
    categoryCol.grid(column=2, row=0, sticky="nsew")
    deleteCol.grid(column=3, row=0, sticky="nsew")
    
    columns.pack(fill="x")

  def cantDeletePopUp(self):
    if self.__MenuItemInstances:
      popUp = self.createPopUp(self.mainFrame)
      contentFrame = tk.Frame(popUp, padx=10, pady=10)
      contentFrame.pack(expand=True, anchor="center")

      ttk.Label(contentFrame, text="Order must first be empty.\nEither Cancel Current Order to Proceed or Return to Order.", wraplength=200, justify=tk.CENTER).pack(pady=10, anchor="center")
      ttk.Button(contentFrame, text="Cancel and Proceed", command=lambda: self.cancelCurrentOrder(popUp)).pack(pady=10, anchor="center")
      ttk.Button(contentFrame, text="Return to Order", command=popUp.destroy).pack(pady=10, anchor="center")
    else :
      self.transitionFrame(self.initDeleteMIPage)

  def cancelCurrentOrder(self, popUp):
    self.__MenuItemInstances = {}
    self.__SavedItemQuantity = {}
    self.__ReceiptListInstances = {}
    self.total = tk.DoubleVar(value=0)
    self.order = Order(self.__MenuItemInstances, self.__conn, self.__cursor, self.commitDBChanges, self.resetForNewOrder)
    popUp.destroy()
    self.transitionFrame(self.initDeleteMIPage)

  def deleteMenuItem(self, itemRow, name, popUp) :
    popUp.destroy()
    itemRow.destroy()
    self.__cursor.execute("DELETE FROM menu_items WHERE name = ?", (name,))
    self.commitDBChanges("Deletion of " + name + " done successfully.")
    del self.__MenuItemRecords[name]

  def deletionConfirmPopUp(self, itemRow, name) :
    print(name)
    popUp = self.createPopUp(self)
    contentFrame = tk.Frame(popUp, padx=10, pady=10)
    contentFrame.pack(expand=True, anchor="center")
    ttk.Label(contentFrame, text=f"Are you sure you want to delete Menu Item '{name}'?").pack(pady=10, anchor="center")
    ttk.Button(contentFrame, text="Confirm", command=lambda: self.deleteMenuItem(itemRow, name, popUp)).pack(pady=10, anchor="center")
    ttk.Button(contentFrame, text="Return to Deletion Page", command=popUp.destroy).pack(pady=10, anchor="center")

  #Receipt
  def initializeReceipt(self) :
    orderNumLbl = ttk.Label(self.receiptFrame, text=f"Order {self.order.orderNum}", style="Cell.TLabel", anchor="center")
    self.orderListFrame = ttk.Frame(self.receiptFrame, style="OrderList.TFrame")
    
    orderNumLbl.pack()
    self.orderListFrame.pack(expand=True, fill="both")

    self.updateReceiptArea()
    self.initTotal(self.receiptFrame)

    checkoutBtn = ttk.Button(self.receiptFrame, text="Checkout", command=self.initCheckoutPage)
    checkoutBtn.pack()
  
  def updateReceiptArea(self) :
    deletionKey = None
    print(f"Here are the menu item instances: {self.__MenuItemInstances}")
    if not self.__MenuItemInstances:
      print(f"No items in order yet.")

    for key, value in self.__MenuItemInstances.items() :
      if key in self.__ReceiptListInstances :
        print("Horray!")
        if value[3] == 0:
          print("destruction of instance")
          self.__ReceiptListInstances[key][4].destroy()          
          del self.__ReceiptListInstances[key]
          deletionKey = key
        elif self.__ReceiptListInstances[key][3] == value[3] :
          print("equal")
          print(self.__ReceiptListInstances[key])
        else :
          print("not equal")
          self.__ReceiptListInstances[key] = value + (self.__ReceiptListInstances[key][4],)

          savedQuantityLbl = self.__ReceiptListInstances[key][4].nametowidget("quantityLbl")
          savedSumLbl = self.__ReceiptListInstances[key][4].nametowidget("sumLbl")

          savedQuantityLbl.config(text=value[3])
          savedSumLbl.config(text=value[1]*value[3])
      else :
        print(f"Here is the SavedItemQuantity of {value[0]}: {self.__SavedItemQuantity[value[0]].get()}")
        orderItemFrame = ttk.Frame(self.orderListFrame)
        self.__ReceiptListInstances[key] = value + (orderItemFrame,)

        quantityLbl = ttk.Label(orderItemFrame, text=value[3], style="Cell.TLabel", anchor="center", name="quantityLbl")
        nameLbl = ttk.Label(orderItemFrame, text=value[0], style="Cell.TLabel", anchor="center", name="nameLbl")
        sumLbl = ttk.Label(orderItemFrame, text=value[1]*value[3], style="Cell.TLabel", anchor="center", name="sumLbl")

        orderItemFrame.grid_columnconfigure(0, weight=1)
        orderItemFrame.grid_columnconfigure(1, weight=1)
        orderItemFrame.grid_columnconfigure(2, weight=1)

        quantityLbl.grid(column=0, row=0, sticky="nsew")
        nameLbl.grid(column=1, row=0, sticky="nsew")
        sumLbl.grid(column=2, row=0, sticky="nsew")

        orderItemFrame.pack(fill="x")

    if (deletionKey) :
      del self.__MenuItemInstances[deletionKey]

    self.updateTotal()

  def updateTotal(self):
    self.total.set(0)
    
    for key, values in self.__MenuItemInstances.items():
      amountToAdd = values[1] * values[3]
      print(f"This is the amount to add of {values[0]}: {amountToAdd}")
      self.total.set(self.total.get() + amountToAdd)
  
  def initTotal(self, parent) :
    totalFrame = ttk.Frame(parent)
    totalTxtLbl = ttk.Label(totalFrame, text="Total:", anchor="center")
    totalSumLbl = ttk.Label(totalFrame, textvariable=self.total, anchor="center")
    
    totalFrame.grid_columnconfigure(0, weight=1)
    totalFrame.grid_columnconfigure(1, weight=1)
    
    totalTxtLbl.grid(column=0, row=0, sticky="nsew")
    totalSumLbl.grid(column=1, row=0, sticky="nsew")

    totalFrame.pack(fill="x", pady=10)

  #Checkout Page
  def initCheckoutPage(self) :
    if not self.__MenuItemInstances:
      self.cantCheckoutPopUp()
      return
    
    self.mainFrame.destroy()
    self.clearReceiptInstances()
    self.initializeMainFrame()

    checkoutFrame = tk.Frame(self.mainFrame,  background="#333333")
    checkoutFrame.pack(expand=True, fill="both", anchor="center", padx=10, pady=10)

    contentFrame = tk.Frame(checkoutFrame, padx=10, pady=10, width=500, height=700)
    contentFrame.pack(expand=True, anchor="center")

    orderLbl = tk.Label(contentFrame, text=f"Order {self.order.orderNum}")
    orderLbl.pack(fill="x", anchor="center", pady=20)

    tk.Label(contentFrame, text="=======================================================").pack(fill="x", anchor="center")

    for key, value in self.__MenuItemInstances.items() :
      orderItemFrame = ttk.Frame(contentFrame)

      quantityLbl = ttk.Label(orderItemFrame, text=value[3], anchor="center", name="quantityLbl", width=30)
      nameLbl = ttk.Label(orderItemFrame, text=value[0], anchor="center", name="nameLbl", width=30)
      productLbl = ttk.Label(orderItemFrame, text=f"₱{value[1]*value[3]}", anchor="center", name="sumLbl", width=30)

      orderItemFrame.grid_columnconfigure(0, weight=1)
      orderItemFrame.grid_columnconfigure(1, weight=1)
      orderItemFrame.grid_columnconfigure(2, weight=1)

      quantityLbl.grid(column=0, row=0, sticky="nsew")
      nameLbl.grid(column=1, row=0, sticky="nsew")
      productLbl.grid(column=2, row=0, sticky="nsew")

      orderItemFrame.pack(fill="x", pady=5)
    
    tk.Label(contentFrame, text="=======================================================").pack(fill="x", anchor="center")
    self.initTotal(contentFrame)

    returnBtn = ttk.Button(contentFrame, text="Return to Order", command=lambda: self.transitionFrame(self.initCashierMode))
    saveBtn = ttk.Button(contentFrame, text="Place Order", command=self.successfulOrderSavePopUp)

    saveBtn.pack(pady=10)
    returnBtn.pack(pady=10)

  def successfulOrderSavePopUp(self) :
    self.order.saveOrderToDB(self.clientConnection)
    popUp = self.createPopUp(self)
    contentFrame = tk.Frame(popUp, padx=10, pady=10)
    contentFrame.pack(expand=True, anchor="center")
    ttk.Label(contentFrame, text="Order Saved Successfully").pack(pady=10, anchor="center")
    ttk.Button(contentFrame, text="Return to Order", command=popUp.destroy).pack(pady=10, anchor="center")

  def cantCheckoutPopUp(self) :
    popUp = self.createPopUp(self)
    contentFrame = tk.Frame(popUp, padx=10, pady=10)
    contentFrame.pack(expand=True, anchor="center")
    ttk.Label(contentFrame, text="You must order something first.").pack(pady=10, anchor="center")
    ttk.Button(contentFrame, text="Return to Order", command=popUp.destroy).pack(pady=10, anchor="center")

  #Centralized Pop-Up Creation:
  def createPopUp(self, parentFrame):
    popUp = tk.Toplevel(parentFrame, bd=2)
    popUp.title("Notification")
    parent_x = parentFrame.winfo_x()
    parent_y = parentFrame.winfo_y()
    parent_width = parentFrame.winfo_width()
    parent_height = parentFrame.winfo_height()

    w = 300
    h = 200

    x = parent_x + (parent_width // 2) - (w // 2)
    y = parent_y + (parent_height // 2) - (h // 2)

    popUp.geometry(f"{w}x{h}+{x}+{y}")

    popUp.transient(parentFrame)
    popUp.grab_set()
    
    return popUp
    
#storage implementation
  def initDB(self) :
    self.__conn = sqlite3.connect(Path("db")/"menuitems.db")
    self.__cursor = self.__conn.cursor()

    self.__cursor.execute("""
                          CREATE TABLE IF NOT EXISTS menu_items (
                            menuItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL,
                            price REAL NOT NULL,
                            category TEXT NOT NULL
                          )
                          """)
    
    self.__cursor.execute("""
                          CREATE TABLE IF NOT EXISTS orders (
                            orderID INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT
                          )
                          """)
    
    self.__cursor.execute("""
                          CREATE TABLE IF NOT EXISTS order_items (
                            itemID INTEGER PRIMARY KEY AUTOINCREMENT, 
                            orderID INTEGER,
                            name TEXT NOT NULL,
                            price REAL NOT NULL,
                            category TEXT NOT NULL,
                            quantity INTEGER,
                            FOREIGN KEY(orderID) REFERENCES orders(orderID)
                          )
                          """)
    
    self.commitDBChanges("d: menu_items table saved in DB")

  def commitDBChanges(self, descrip) :
      try:
        self.__conn.commit()
        print(descrip)
      except Exception as e:
        #PUT MORE ERROR HANDLING HERE
        print(e)
        self.__conn.rollback()
        sys.exit(1)

  #Menu Items
  def initMenuItemsfromDB(self) :
      results = self.__cursor.execute("SELECT * FROM menu_items")
      rows = results.fetchall()

      print("Initializing Menu Items...")
      if len(rows):
        for row in rows:
          MenuItemRecord = {
            "name": row[1],
            "price": row[2],
            "category": row[3],
          }

          self.__MenuItemRecords[MenuItemRecord['name']] = MenuItemRecord
          print(f"Item {row[0]}: {MenuItemRecord['name']}")
        print("Initialization of Menu Items Complete.")
        return True
      else:
        return False

  def addMenuItem(self, data) :
    if not data:
      self.fieldsErrorPopUp("Fields must have proper input.")
      return
    elif data == "ValueError" :
      self.fieldsErrorPopUp("Input for price must be a real number.")
      return

    
    print(f"Here is data in adding: {data}")
    self.__cursor.execute("INSERT INTO menu_items (name, price, category) VALUES (?, ?, ?)", data)

    MenuItemRecord = {
      "name": data[0],
      "price": data[1],
      "category": data[2],
    }

    self.__MenuItemRecords[MenuItemRecord['name']] = MenuItemRecord

    self.commitDBChanges("d: prototype data saved to menu_items table in DB")

  def fieldsErrorPopUp(self, message) :
    popUp = self.createPopUp(self.mainFrame)
    contentFrame = tk.Frame(popUp, padx=10, pady=10)
    contentFrame.pack(expand=True, anchor="center")
    ttk.Label(contentFrame, text=message).pack(pady=10, anchor="center")
    ttk.Button(contentFrame, text="Return to Order", command=popUp.destroy).pack(pady=10, anchor="center")

  def removeMenuItem(self) :
    #need to ask for confirmation from user then delete from DB
    self.__cursor.execute("DELETE ")

  def editMenuItem(self) :
    self.__cursor.execute("UPDATE ")

  def printMenuLength(self) :
    print(len(self.__MenuItemRecords))

  def displayItemsInConsole(self) :
    rows = self.__cursor.execute("SELECT * FROM menu_items")

    for row in rows:
      print("----\nItems in MenuItemRecord: ")
      print(f"Name: {row[1]}")

  def clearReceiptInstances(self) :
    self.__ReceiptListInstances = {}

  #History Page DB Functionality
  def reqForOrderHistory(self) :
    self.__OrderRecords = {}
    orders = self.__cursor.execute("SELECT * FROM orders ORDER BY date DESC")
    results = orders.fetchall()

    for order in results :
      self.__OrderRecords[order[0]] = {
        "orderID": order[0], 
        "date": datetime.datetime.fromisoformat(order[1]),
        "items": {}
      }

      itemsInOrder = self.__cursor.execute("SELECT * FROM order_items WHERE orderID = ?", (order[0],))

      for item in itemsInOrder:
        self.__OrderRecords[order[0]]["items"][item[2]] = {
          "name": item[2],
          "price": item[3],
          "category": item[4],
          "quantity": item[5]
        }

  def resetForNewOrder(self) :
    self.__MenuItemInstances = {}
    self.__SavedItemQuantity = {}
    self.__ReceiptListInstances = {}
    self.total = tk.DoubleVar(value=0)
    self.order = Order(self.__MenuItemInstances, self.__conn, self.__cursor, self.commitDBChanges, self.resetForNewOrder)
    self.mainFrame.destroy()
    self.initializeMainFrame()
    self.initCashierMode()

class MenuItem(tk.Frame) :
  def __init__(self, parent, root, MenuItemRecord, MenuItemInstances, updateReceiptArea, initQuantity) :
    self.__MenuItemInstances = MenuItemInstances
    self.updateReceiptArea = updateReceiptArea
    self.root = root
    super().__init__(parent)
    self.initStyles()

    self.__name = tk.StringVar(value=MenuItemRecord['name'])
    self.__price = tk.DoubleVar(value=MenuItemRecord['price'])
    self.__category = tk.StringVar(value=MenuItemRecord['category'])

    self.__quantity = tk.IntVar(value=initQuantity)

    self.nameLbl = ttk.Label(self, textvariable=self.__name, style="Cell.TLabel")
    self.priceLbl = ttk.Label(self, textvariable=self.__price, style="Cell.TLabel")
    self.categoryLbl = ttk.Label(self, textvariable=self.__category, style="Cell.TLabel")
    self.addToOrderBtn = ttk.Button(self, text="ADD", style="Cell.TButton", command=lambda: self.addItemPopUp(root))

    self.grid_columnconfigure(0, weight=1)
    self.grid_columnconfigure(1, weight=1)
    self.grid_columnconfigure(2, weight=1)
    self.grid_columnconfigure(3, weight=1)

    self.nameLbl.grid(column=0, row=0, sticky="nsew")
    self.priceLbl.grid(column=1, row=0, sticky="nsew")
    self.categoryLbl.grid(column=2, row=0, sticky="nsew")
    self.addToOrderBtn.grid(column=3, row=0, sticky="nsew")

    print("---d: Menu Item row creation was successful.---")

  @property
  def quantity(self):
    return self.__quantity

  def initStyles(self) :
    self.style = ttk.Style()
    self.style.configure("Cell.TLabel",
                    width=50,
                    relief="solid", 
                    borderwidth=2, 
                    bg="lightgray"
                    )
    
    self.style.configure("Cell.TButton",
                    relief="solid", 
                    width=50,
                    borderwidth=2, 
                    bg="lightgray"
                    )

  def addItemPopUp(self, parent) :
    self.popUp = tk.Toplevel(parent, bd=2)
    parent_x = self.root.winfo_x()
    parent_y = self.root.winfo_y()
    parent_width = self.root.winfo_width()
    parent_height = self.root.winfo_height()

    w = 300
    h = 200

    x = parent_x + (parent_width // 2) - (w // 2)
    y = parent_y + (parent_height // 2) - (h // 2)

    self.popUp.geometry(f"{w}x{h}+{x}+{y}")

    self.popUp.transient(parent)
    self.popUp.grab_set()

    popNameLbl = ttk.Label(self.popUp, textvariable=self.__name)
    popPriceLbl = ttk.Label(self.popUp, textvariable=self.__price)
    popCategoryLbl = ttk.Label(self.popUp, textvariable=self.__category)

    popNameLbl.pack(padx=5, pady=5)
    popPriceLbl.pack(padx=5, pady=5)
    popCategoryLbl.pack(padx=5, pady=5)
    self.createBtns()

    self.increaseBtn.focus_set()

  def createBtns(self) :
    self.btnFrame = tk.Frame(self.popUp)
    quantityLbl = ttk.Label(self.btnFrame, textvariable=self.__quantity)
    self.increaseBtn = ttk.Button(self.btnFrame, text="+", command=self.increaseQuantity)
    self.decreaseBtn = ttk.Button(self.btnFrame, text="-", command=self.decreaseQuantity)
    self.finalAddBtn = ttk.Button(self.popUp, text="save", command=self.addToOrder)

    self.increaseBtn.bind("<Return>", self.increaseQuantity)
    self.decreaseBtn.bind("<Return>", self.decreaseQuantity)
    self.finalAddBtn.bind("<Return>", self.addToOrder)

    self.increaseBtn.pack(side=tk.LEFT, padx=5, pady=5)
    quantityLbl.pack(side=tk.LEFT, padx=5, pady=5)
    self.decreaseBtn.pack(side=tk.LEFT, padx=5, pady=5)

    self.btnFrame.pack()
    self.finalAddBtn.pack(padx=5, pady=5)

    print("d: Buttons for PopUp Frame packed.")

  def addToOrder(self, event=None) :
    name = self.__name.get()
    price = self.__price.get()
    category = self.__category.get()
    quantity = self.__quantity.get()

    if self.quantity.get() == 0 and name not in self.__MenuItemInstances:
      print("No quantity added. Returning to Menu.")
      self.popUp.destroy()
    else:
      self.__MenuItemInstances[name] = (name, price, category, quantity)
      self.updateReceiptArea()
      self.popUp.destroy()
    
  def decreaseQuantity(self, event=None) :
    currentQuantity = self.__quantity.get()
    if currentQuantity > 0 :
      self.__quantity.set(currentQuantity - 1)
      print(f"Quantity decreased to {currentQuantity - 1}")
    else:
      print(f"Quantity is already {currentQuantity}")
      
  def increaseQuantity(self, event=None) :
    currentQuantity = self.__quantity.get()
    if currentQuantity < 10 :
      self.__quantity.set(currentQuantity + 1)
      print(f"Quantity increased to {currentQuantity + 1}")
    else:
      print(f"Quantity is already at max -> {currentQuantity}")

class Order() :
  def __init__(self, MenuItemInstances, conn, cursor, commitDBChanges, clearAllInstances) :
    self.__ItemsInOrder = MenuItemInstances
    self.__conn = conn
    self.__cursor = cursor
    self.commitDBChanges = commitDBChanges
    self.clearAllInstances = clearAllInstances

    results = self.__cursor.execute("SELECT * FROM orders ORDER BY date DESC")
    latestResult = results.fetchone()
    if (latestResult) :
      self.orderNum = latestResult[0] + 1
    else:
      self.orderNum = 1

  def saveOrderToDB(self, clientConnection) :
    if not self.__ItemsInOrder:
      print("Order is empty!")
      return 
    
    data = {
      self.orderNum: {}
    }

    dateTimeOrder = datetime.datetime.now().isoformat()
    self.__cursor.execute("INSERT INTO orders (date) VALUES (?)", (dateTimeOrder,))

    self.commitDBChanges("Saved date-time of current order to orders table in DB.")

    for key, value in self.__ItemsInOrder.items():
      self.__cursor.execute("INSERT INTO order_items (orderID, name, price, category, quantity) VALUES (?, ?, ?, ?, ?)", (self.orderNum, *value))
      data[self.orderNum][value[0]] = [value[3]]

    self.commitDBChanges("Saved items in receipt to order_items table in DB.")
    print(f"Data to be transferred: {data}")

    if clientConnection :
      try :
        orderInfoToBytes = json.dumps(data).encode('utf-8')
        clientConnection.sendall(orderInfoToBytes)
      except Exception as e :
        print(f"Error sending data to Kitchen: {e}")
      
    self.clearAllInstances()
    print("Order saved! New order ready.")

app = App()
app.mainloop()