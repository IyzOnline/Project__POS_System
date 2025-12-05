import tkinter as tk
from tkinter import ttk
import sqlite3
from pathlib import Path
import sys
from PIL import Image, ImageTk

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
    self.initializeMenuItems()

  def initializeMenuArea(self):
    self.menuSearch = tk.Frame(self.menuFrame, bg="#8049df")
    self.menuTable = tk.Frame(self.menuFrame, bg="#df4949")
    self.menuLowerBtns = tk.Frame(self.menuFrame, bg="#448743")

    self.menuSearch.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)
    self.menuTable.place(relx=0, rely=0.1, relwidth=1.0, relheight=0.8)
    self.menuLowerBtns.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)

    self.createBtn = ttk.Button(self.menuLowerBtns, text="+", command=self.createMenuItem)
    self.deleteBtn = ttk.Button(self.menuLowerBtns, text="-")
    self.editBtn = ttk.Button(self.menuLowerBtns, text="/")

    self.createBtn.pack(side=tk.LEFT, padx=5, pady=5)
    self.deleteBtn.pack(side=tk.LEFT, padx=5, pady=5)
    self.editBtn.pack(side=tk.LEFT, padx=5, pady=5)

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
      data = (self.nameEntry.get(), 
              int(self.priceEntry.get()), 
              self.categoryEntry.get(), 
              str(Path("images") / "pikachu.png")
            )
      
      self.nameEntry.delete(0, tk.END)
      self.priceEntry.delete(0, tk.END)
      self.categoryEntry.delete(0, tk.END)

      print(data)
      return data

    self.createMIFrame = tk.Frame(self)

    self.nameEntry = ttk.Entry(self.createMIFrame, width=30, font=("Helvetica", 14))
    self.priceEntry = ttk.Entry(self.createMIFrame, width=30, font=("Helvetica", 14))
    self.categoryEntry = ttk.Entry(self.createMIFrame, width=30, font=("Helvetica", 14))

    self.createMIFrame.pack()

    self.returnBtn = ttk.Button(self.createMIFrame, text="return", command=lambda: self.returnToHome(self.createMIFrame))
    self.saveBtn = ttk.Button(self.createMIFrame, text="Save to DB", command=lambda: self.addMenuItem(passData()))

    ttk.Label(self.createMIFrame, text="- Name -").pack()
    self.nameEntry.pack()
    ttk.Label(self.createMIFrame, text="- Price -").pack()
    self.priceEntry.pack()
    ttk.Label(self.createMIFrame, text="- Category -").pack()
    self.categoryEntry.pack()

    self.returnBtn.pack()
    self.saveBtn.pack()

  def returnToHome(self, currentFrame):
    currentFrame.pack_forget()
    self.initializeHomePage()

#storage implementation
  def initDB(self):
    self.__conn = sqlite3.connect(Path("db")/"menuitems.db")
    self.__cursor = self.__conn.cursor()

    self.__cursor.execute("""
                          CREATE TABLE IF NOT EXISTS menu_items (
                            menuItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL,
                            price INTEGER NOT NULL,
                            category TEXT NOT NULL,
                            imageFileName TEXT NOT NULL
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
          "imagePath": row[4]
        }

        self.__MenuItemRecords[MenuItemRecord['name']] = MenuItemRecord
        print(f"Item {row[0]}: {MenuItemRecord['name']}")

      print("Initialization of Menu Items Complete.")

  def addMenuItem(self, data):
    print(f"Here is data in adding: {data}")
    self.__cursor.execute("INSERT INTO menu_items (name, price, category, imageFileName) VALUES (?, ?, ?, ?)", data)

    MenuItemRecord = {
      "name": data[0],
      "price": data[1],
      "category": data[2],
      "imagePath": data[3]
    }

    self.__MenuItemRecords[MenuItemRecord['name']] = MenuItemRecord

    self.commitDBChanges("d: prototype data saved to menu_items table in DB")

class MenuItem(tk.Frame):
  def __init__(self, parent, MenuItemRecord):
    super().__init__(parent)

    self.__name = tk.StringVar(value=MenuItemRecord['name'])
    self.__price = tk.IntVar(value=MenuItemRecord['price'])
    self.__category = tk.StringVar(value=MenuItemRecord['category'])

    originalImage = Image.open(MenuItemRecord['imagePath'])
    resizeImage = originalImage.resize((150, 150), Image.LANCZOS)
    self.__imagePath = ImageTk.PhotoImage(resizeImage)

    #print("--\nPrinting New Menu Item")
    #print(f"String Var Name: {self.__name.get()}")
    #print(f"Int Var Price: {self.__price.get()}")
    #print(f"String Var Category: {self.__category.get()}")

    self.nameLbl = tk.Label(self, textvariable=self.__name)
    self.priceLbl = tk.Label(self, textvariable=self.__price)
    self.categoryLbl = tk.Label(self, textvariable=self.__category)
    self.imageLbl = tk.Label(self, image=self.__imagePath)

    self.imageLbl.pack()
    self.nameLbl.pack()
    self.priceLbl.pack()
    self.categoryLbl.pack()
    self.createBtns()

    print("d: Proto Frame saved successfully.")

  def createBtns(self):
    self.btnFrame = tk.Frame(self)
    self.quantity = tk.IntVar()

    self.increaseBtn = ttk.Button(self.btnFrame, text="+", command=self.increaseQuantity)
    self.quantityLbl = ttk.Label(self.btnFrame, textvariable=self.quantity)
    self.decreaseBtn = ttk.Button(self.btnFrame, text="-", command=self.decreaseQuantity)

    self.increaseBtn.bind("<Return>", self.increaseQuantity)
    self.decreaseBtn.bind("<Return>", self.decreaseQuantity)

    self.increaseBtn.pack(side=tk.LEFT, padx=5, pady=5)
    self.quantityLbl.pack(side=tk.LEFT, padx=5, pady=5)
    self.decreaseBtn.pack(side=tk.LEFT, padx=5, pady=5)

    self.btnFrame.pack()

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

app = App()
app.mainloop()