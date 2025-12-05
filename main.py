import tkinter as tk

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

app = App()
app.mainloop()