import tkinter as tk
from tkinter import ttk
import sqlite3
from pathlib import Path
import sys

class App(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("POS System")
    self.minsize(960, 540)

    self.__MenuItemRecords = {}
    self.__MenuItemInstances = {}

    self.initializeExitFS()
    self.initDB()
    self.initializeHomePage()

#UI Implementation
  def initializeExitFS(self):
    self.attributes('-fullscreen', True)
    self.bind('<Escape>', self.exit_fullscreen)

  def exit_fullscreen(self, event=None):
    self.attributes('-fullscreen', False)
  
  def initializeStyleObjects(self):
    pass

  def initializeHomePage(self):
    self.homeFrame = tk.Frame(self, bg="#ffffff")
    self.homeFrame.pack(expand=True, fill="both", padx=20, pady=20)

    self.sidebarFrame = tk.Frame(self.homeFrame, bg="#3498db")
    self.menuFrame = tk.Frame(self.homeFrame, bg="#49a3df")
    self.summaryFrame = tk.Frame(self.homeFrame, bg="#5faee3")

    self.sidebarFrame.place(relx=0, rely=0, relwidth=0.1, relheight=1.0)
    self.menuFrame.place(relx=0.1, rely=0, relwidth=0.6, relheight=1.0)
    self.summaryFrame.place(relx=0.72, rely=0, relwidth=0.28, relheight=1.0)

    self.initializeMenuArea()

  #Menu
  def initializeMenuArea(self):
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

    self.initializeMenuItems()
    self.initializeSearchArea()

  def initializeSearchArea(self):
    self.searchValue = tk.StringVar()
    self.searchValue.trace_add("write", self.searchThroughRecords)
    searchEntry = ttk.Entry(self.menuSearch, textvariable=self.searchValue, width=60, font=("Helvetica", 14))
    searchEntry.pack()

  def searchThroughRecords(self, *args):
    print("Records Searched!")

  def initializeMenuItems(self):
    if (len(self.__MenuItemRecords) == 0):
      self.initMenuItemsfromDB()
    for recordName, recordValues in self.__MenuItemRecords.items():
      print(recordValues)
      item = MenuItem(self.menuTable, recordValues)
      item.pack()

  def createMenuItem(self):
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

  def returnToHome(self, currentFrame):
    currentFrame.pack_forget()
    self.initializeHomePage()

  def editMenuItem(self):
    pass

  def deleteMenuItem(self):
    pass 

  #Sidebar
  def initializeSidebar_Proto(self):
    pass

  def initializeSidebar(self):
    pass

  #Receipt
  def initializeReceipt_Proto(self):
    pass

  def initializeReceipt(self):
    pass

#storage implementation
  def initDB(self):
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
                            name TEXT,
                            quantity INTEGER,
                            FOREIGN KEY(orderID) REFERENCES orders(orderID)
                          )
                          """)
    
    self.commitDBChanges("d: menu_items table saved in DB")

  def commitDBChanges(self, descrip):
      try:
        self.__conn.commit()
        print(descrip)
      except Exception as e:
        #PUT MORE ERROR HANDLING HERE
        print(e)
        self.__conn.rollback()
        sys.exit(1)

  def initMenuItemsfromDB(self):
      rows = self.__cursor.execute("SELECT * FROM menu_items")

      print("Initializing Menu Items...")
      for row in rows:
        MenuItemRecord = {
          "name": row[1],
          "price": row[2],
          "category": row[3],
        }

        self.__MenuItemRecords[MenuItemRecord['name']] = MenuItemRecord
        print(f"Item {row[0]}: {MenuItemRecord['name']}")

      print("Initialization of Menu Items Complete.")

  def addMenuItem(self, data):
    print(f"Here is data in adding: {data}")
    self.__cursor.execute("INSERT INTO menu_items (name, price, category) VALUES (?, ?, ?)", data)

    MenuItemRecord = {
      "name": data[0],
      "price": data[1],
      "category": data[2],
    }

    self.__MenuItemRecords[MenuItemRecord['name']] = MenuItemRecord

    self.commitDBChanges("d: prototype data saved to menu_items table in DB")

  def removeMenuItem(self):
    #need to ask for confirmation from user then delete from DB
    self.__cursor.execute("DELETE ")

  def editMenuItem(self):
    self.__cursor.execute("UPDATE ")

  def printMenuLength(self):
    print(len(self.__MenuItemRecords))

  def displayItemsInConsole(self):
    rows = self.__cursor.execute("SELECT * FROM menu_items")

    for row in rows:
      print("----\nItems in MenuItemRecord: ")
      print(f"Name: {row[1]}")

class MenuItem(tk.Frame):
  def __init__(self, parent, MenuItemRecord):
    super().__init__(parent)

    self.__name = tk.StringVar(value=MenuItemRecord['name'])
    self.__price = tk.IntVar(value=MenuItemRecord['price'])
    self.__category = tk.StringVar(value=MenuItemRecord['category'])
    self.quantity = tk.IntVar()

    self.nameLbl = tk.Label(self, textvariable=self.__name)
    self.priceLbl = tk.Label(self, textvariable=self.__price)
    self.categoryLbl = tk.Label(self, textvariable=self.__category)

    self.nameLbl.pack(side=tk.LEFT, padx=5, pady=5)
    self.priceLbl.pack(side=tk.LEFT, padx=5, pady=5)
    self.categoryLbl.pack(side=tk.LEFT, padx=5, pady=5)

    print("---\n\nd: Proto Frame saved successfully.\n\n---")

  def createAdminBtns(self):
    self.adminBtnFrame = tk.Frame(self)

    increaseBtn = ttk.Button(self.adminBtnFrame, text="+", command=self.increaseQuantity)
    quantityLbl = ttk.Label(self.adminBtnFrame, textvariable=self.quantity)
    decreaseBtn = ttk.Button(self.adminBtnFrame, text="-", command=self.decreaseQuantity)

    increaseBtn.bind("<Return>", self.increaseQuantity)
    decreaseBtn.bind("<Return>", self.decreaseQuantity)

    increaseBtn.pack(side=tk.LEFT, padx=5, pady=5)
    quantityLbl.pack(side=tk.LEFT, padx=5, pady=5)
    decreaseBtn.pack(side=tk.LEFT, padx=5, pady=5)

    self.adminBtnFrame.pack()

    print("d: Buttons for Proto Frame packed.")
    
  def decreaseQuantity(self, event=None):
    currentQuantity = self.quantity.get()
    if currentQuantity > 0:
      self.quantity.set(currentQuantity - 1)
      print(f"Quantity decreased to {currentQuantity - 1}")
    else:
      print(f"Quantity is already {currentQuantity}")
      
  def increaseQuantity(self, event=None):
    currentQuantity = self.quantity.get()
    if currentQuantity < 10:
      self.quantity.set(currentQuantity + 1)
      print(f"Quantity increased to {currentQuantity + 1}")
    else:
      print(f"Quantity is already at max -> {currentQuantity}")

class Order():
  def __init__(self):
    pass

  def addToOrder(self, itemName):
    pass

  def reduceFromOrder(self, itemName):
    pass

  def deleteFromOrder(self, itemName):
    pass

  def deleteEntireOrder(self):
    pass

  def checkoutOrder(self):
    pass

  def cancelOrder(self):
    pass

app = App()
app.mainloop()