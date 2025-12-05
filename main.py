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

  def initializeMenuArea(self):
    self.menuSearch = tk.Frame(self.menuFrame, bg="#8049df")
    self.menuTable = tk.Frame(self.menuFrame, bg="#df4949")
    self.menuLowerBtns = tk.Frame(self.menuFrame, bg="#448743")

    self.menuSearch.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)
    self.menuTable.place(relx=0, rely=0.1, relwidth=1.0, relheight=0.8)
    self.menuLowerBtns.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)

    self.createBtn = ttk.Button(self.menuLowerBtns, text="+")
    self.deleteBtn = ttk.Button(self.menuLowerBtns, text="-")
    self.editBtn = ttk.Button(self.menuLowerBtns, text="/")

    self.createBtn.pack(side=tk.LEFT, padx=5, pady=5)
    self.deleteBtn.pack(side=tk.LEFT, padx=5, pady=5)
    self.editBtn.pack(side=tk.LEFT, padx=5, pady=5)

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
    
app = App()
app.mainloop()