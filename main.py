import tkinter as tk
from tkinter import ttk
import sqlite3
from pathlib import Path
import sys
import datetime

class App(tk.Tk) :
  def __init__(self):
    super().__init__()
    self.title("POS System")
    self.minsize(960, 540)

    self.__MenuItemRecords = {}
    self.__MenuItemInstances = {}
    self.__SavedItemQuantity = {}
    self.__ReceiptListInstances = {}
    self.total = tk.DoubleVar(value=0)

    self.initStyles()
    self.initializeExitFS()
    self.initDB()
    self.initializeHomePage()

#UI Implementation
  def initStyles(self) :
    self.style = ttk.Style()
    self.style.configure("Cell.TLabel",
                    width=50,
                    relief="solid", 
                    borderwidth=2, 
                    bg="lightgray",
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

  def initializeHomePage(self) :
    self.homeFrame = tk.Frame(self, bg="#ffffff")
    self.homeFrame.pack(expand=True, fill="both", padx=20, pady=20)

    self.sidebarFrame = tk.Frame(self.homeFrame, bg="#3498db")
    self.menuFrame = tk.Frame(self.homeFrame, bg="#49a3df")
    self.receiptFrame = tk.Frame(self.homeFrame, bg="#5faee3")

    self.sidebarFrame.place(relx=0, rely=0, relwidth=0.1, relheight=1.0)
    self.menuFrame.place(relx=0.1, rely=0, relwidth=0.6, relheight=1.0)
    self.receiptFrame.place(relx=0.72, rely=0, relwidth=0.28, relheight=1.0)

    self.initializeMenuArea()
    self.initializeReceipt()

  #Menu
  def initializeMenuArea(self) :
    self.menuSearch = tk.Frame(self.menuFrame, bg="#8049df")
    self.menuTable = tk.Frame(self.menuFrame, bg="#df4949")
    self.menuLowerBtns = tk.Frame(self.menuFrame, bg="#448743")

    self.menuSearch.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)
    self.menuTable.place(relx=0, rely=0.1, relwidth=1.0, relheight=0.8)
    self.menuLowerBtns.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)

    createBtn = ttk.Button(self.menuLowerBtns, text="+", command=self.createMenuItem)
    deleteBtn = ttk.Button(self.menuLowerBtns, text="-")
    editBtn = ttk.Button(self.menuLowerBtns, text="/")

    createBtn.pack(side=tk.LEFT, padx=5, pady=5)
    deleteBtn.pack(side=tk.LEFT, padx=5, pady=5)
    editBtn.pack(side=tk.LEFT, padx=5, pady=5)

    self.initMenuTableColumns()
    self.initializeMenuItems()
    self.initializeSearchArea()

  def initializeSearchArea(self) :
    self.searchValue = tk.StringVar()
    self.searchValue.trace_add("write", self.searchThroughRecords)
    searchEntry = ttk.Entry(self.menuSearch, textvariable=self.searchValue, width=60, font=("Helvetica", 14))
    searchEntry.pack(expand=True)

  def searchThroughRecords(self, *args):
    print("Records Searched!")

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
    
    columns.pack()

  def initializeMenuItems(self) :
    self.empty = None
    if (len(self.__MenuItemRecords) == 0):
      if not self.initMenuItemsfromDB():
        self.empty = tk.Label(self.menuTable, text="No records exist.")
        self.empty.pack(expand=True, fill="both")
    else :
      if (self.empty) :
        self.empty.destroy()
    
    for index, (recordName, recordValues) in enumerate(self.__MenuItemRecords.items()):
      print(recordValues)
      if recordName in self.__SavedItemQuantity :
        updatedQuantity = self.__SavedItemQuantity[recordName].get()
        item = MenuItem(self.menuTable, recordValues, index, self.__MenuItemInstances, self.updateReceiptArea, updatedQuantity)
      else :
        item = MenuItem(self.menuTable, recordValues, index, self.__MenuItemInstances, self.updateReceiptArea, 0)
      
      self.__SavedItemQuantity[recordName] = item.quantity
      item.pack(fill="x")

  def createMenuItem(self) :
    self.homeFrame.pack_forget()

    def passData():
      data = (nameEntry.get(), 
              int(priceEntry.get()), 
              categoryEntry.get()
            )
      
      nameEntry.delete(0, tk.END)
      priceEntry.delete(0, tk.END)
      categoryEntry.delete(0, tk.END)

      print(data)
      return data

    createMIFrame = tk.Frame(self)

    nameEntry = ttk.Entry(createMIFrame, width=30, font=("Helvetica", 14))
    priceEntry = ttk.Entry(createMIFrame, width=30, font=("Helvetica", 14))
    categoryEntry = ttk.Entry(createMIFrame, width=30, font=("Helvetica", 14))

    createMIFrame.pack()

    returnBtn = ttk.Button(createMIFrame, text="return", command=lambda: self.returnToHome(createMIFrame))
    saveBtn = ttk.Button(createMIFrame, text="Save to DB", command=lambda: self.addMenuItem(passData()))

    ttk.Label(createMIFrame, text="- Name -").pack()
    nameEntry.pack()
    ttk.Label(createMIFrame, text="- Price -").pack()
    priceEntry.pack()
    ttk.Label(createMIFrame, text="- Category -").pack()
    categoryEntry.pack()

    returnBtn.pack()
    saveBtn.pack()

  def returnToHome(self, currentFrame) :
    currentFrame.pack_forget()
    self.clearReceiptInstances()
    self.initializeHomePage()

  def editMenuItem(self) :
    pass

  def deleteMenuItem(self) :
    pass 

  #Sidebar
  def initializeSidebar_Proto(self) :
    pass

  def initializeSidebar(self) :
    pass

  #Receipt
  def initializeReceipt(self) :
    order = Order(self.__MenuItemInstances, self.__conn, self.__cursor, self.commitDBChanges)
    
    orderNumLbl = ttk.Label(self.receiptFrame, text=f"Order {order.orderNum}", style="Cell.TLabel", anchor="center")
    self.orderListFrame = ttk.Frame(self.receiptFrame, style="OrderList.TFrame")
    
    orderNumLbl.pack()
    self.orderListFrame.pack(expand=True, fill="both")

    self.updateReceiptArea()
    self.initTotal()

    checkoutBtn = ttk.Button(self.receiptFrame, text="Checkout", command=order.saveOrderToDB)
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

          self.total.set(self.total.get() - (self.__ReceiptListInstances[key][1] * self.__ReceiptListInstances[key][3]))
          
          del self.__ReceiptListInstances[key]
          deletionKey = key
        elif self.__ReceiptListInstances[key][3] == value[3] :
          print("equal")
          print(self.__ReceiptListInstances[key])
        else :
          print("not equal")

          self.total.set(self.total.get() - (self.__ReceiptListInstances[key][1] * self.__ReceiptListInstances[key][3]))

          self.__ReceiptListInstances[key] = value + (self.__ReceiptListInstances[key][4],)

          self.total.set(self.total.get() + (self.__ReceiptListInstances[key][1] * self.__ReceiptListInstances[key][3]))

          savedQuantityLbl = self.__ReceiptListInstances[key][4].nametowidget("quantityLbl")
          savedSumLbl = self.__ReceiptListInstances[key][4].nametowidget("sumLbl")

          savedQuantityLbl.config(text=value[3])
          savedSumLbl.config(text=value[1]*value[3])
      else :
        orderItemFrame = ttk.Frame(self.orderListFrame)
        self.__ReceiptListInstances[key] = value + (orderItemFrame,)

        quantityLbl = ttk.Label(orderItemFrame, text=value[3], style="Cell.TLabel", anchor="center", name="quantityLbl")
        nameLbl = ttk.Label(orderItemFrame, text=value[0], style="Cell.TLabel", anchor="center", name="nameLbl")
        sumLbl = ttk.Label(orderItemFrame, text=value[1]*value[3], style="Cell.TLabel", anchor="center", name="sumLbl")

        self.total.set(self.total.get() + (self.__ReceiptListInstances[key][1] * self.__ReceiptListInstances[key][3]))

        orderItemFrame.grid_columnconfigure(0, weight=1)
        orderItemFrame.grid_columnconfigure(1, weight=1)
        orderItemFrame.grid_columnconfigure(2, weight=1)

        quantityLbl.grid(column=0, row=0, sticky="nsew")
        nameLbl.grid(column=1, row=0, sticky="nsew")
        sumLbl.grid(column=2, row=0, sticky="nsew")

        orderItemFrame.pack(fill="x")

    if (deletionKey) :
      del self.__MenuItemInstances[deletionKey]

  def initTotal(self):
    totalFrame = ttk.Frame(self.receiptFrame)
    totalTxtLbl = ttk.Label(totalFrame, text="Total:", anchor="center")
    totalSumLbl = ttk.Label(totalFrame, textvariable=self.total, anchor="center")
    
    totalFrame.grid_columnconfigure(0, weight=1)
    totalFrame.grid_columnconfigure(1, weight=1)
    
    totalTxtLbl.grid(column=0, row=0, sticky="nsew")
    totalSumLbl.grid(column=1, row=0, sticky="nsew")

    totalFrame.pack(fill="x")

  def clearReceiptInstances(self) :
    self.__ReceiptListInstances = {}

#storage implementation
  def initDB(self) :
    self.__conn = sqlite3.connect(Path("db")/"menuitems.db")
    self.__cursor = self.__conn.cursor()

    self.__cursor.execute("""
                          CREATE TABLE IF NOT EXISTS menu_items (
                            menuItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL,
                            price INTEGER NOT NULL,
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
                            price INTEGER NOT NULL,
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
    print(f"Here is data in adding: {data}")
    self.__cursor.execute("INSERT INTO menu_items (name, price, category) VALUES (?, ?, ?)", data)

    MenuItemRecord = {
      "name": data[0],
      "price": data[1],
      "category": data[2],
    }

    self.__MenuItemRecords[MenuItemRecord['name']] = MenuItemRecord

    self.commitDBChanges("d: prototype data saved to menu_items table in DB")

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

class MenuItem(tk.Frame) :
  def __init__(self, parent, MenuItemRecord, count, MenuItemInstances, updateReceiptArea, initQuantity) :
    self.__MenuItemInstances = MenuItemInstances
    self.updateReceiptArea = updateReceiptArea
    super().__init__(parent)
    self.initStyles()

    print(f"Count: " + str(count))
    self.__name = tk.StringVar(value=MenuItemRecord['name'])
    self.__price = tk.IntVar(value=MenuItemRecord['price'])
    self.__category = tk.StringVar(value=MenuItemRecord['category'])

    self.__quantity = tk.IntVar(value=initQuantity)

    self.nameLbl = ttk.Label(self, textvariable=self.__name, style="Cell.TLabel")
    self.priceLbl = ttk.Label(self, textvariable=self.__price, style="Cell.TLabel")
    self.categoryLbl = ttk.Label(self, textvariable=self.__category, style="Cell.TLabel")
    self.addToOrderBtn = ttk.Button(self, text="ADD", style="Cell.TButton", command=lambda: self.addItemPopUp(parent))

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
    self.popUp = tk.Frame(parent, bd=2, relief="raised")

    popNameLbl = ttk.Label(self.popUp, textvariable=self.__name)
    popPriceLbl = ttk.Label(self.popUp, textvariable=self.__price)
    popCategoryLbl = ttk.Label(self.popUp, textvariable=self.__category)

    popNameLbl.pack(padx=5, pady=5)
    popPriceLbl.pack(padx=5, pady=5)
    popCategoryLbl.pack(padx=5, pady=5)
    self.createBtns()

    self.popUp.place(relx=0.5, rely=0.5, anchor="center", width=300, height=200)
    self.popUp.lift()
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
        print("Quantity cannot be zero")
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
  def __init__(self, MenuItemInstances, conn, cursor, commitDBChanges) :
    self.__ItemsInOrder = MenuItemInstances
    self.__conn = conn
    self.__cursor = cursor
    self.commitDBChanges = commitDBChanges

    results = self.__cursor.execute("SELECT * FROM orders ORDER BY date DESC")
    latestResult = results.fetchone()
    if (latestResult) :
      self.orderNum = latestResult[0] + 1
    else:
      self.orderNum = 1

  def saveOrderToDB(self) :
    if not self.__ItemsInOrder:
      print("Order is empty!")
      return 

    dateTimeOrder = datetime.datetime.now().isoformat()
    self.__cursor.execute("INSERT INTO orders (date) VALUES (?)", (dateTimeOrder,))

    self.commitDBChanges("Inserted date-time of current order to DB.")

    for key, value in self.__ItemsInOrder.items():
      self.__cursor.execute("INSERT INTO order_items (orderID, name, price, category, quantity) VALUES (?, ?, ?)", (self.orderNum, *value))

    self.commitDBChanges("Inserted item rows inside of order_items table in DB.")

    self.__ItemsInOrder.clear()

  def reduceFromOrder(self, itemName):
    pass

  def deleteFromOrder(self, itemName):
    pass

  def deleteEntireOrder(self):
    pass

  def cancelOrder(self):
    pass

app = App()
app.mainloop()