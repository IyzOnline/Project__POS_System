import tkinter as tk

class App(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("POS System")
    self.minsize(960, 540)

    self.__MenuItemRecords = {}
    self.__MenuItemInstances = {}

    self.initializeExitFS()
    
  def initializeExitFS(self):
    self.attributes('-fullscreen', True)
    self.bind('<Escape>', self.exit_fullscreen)

  def exit_fullscreen(self, event=None):
    self.attributes('-fullscreen', False)
  

app = App()
app.mainloop()