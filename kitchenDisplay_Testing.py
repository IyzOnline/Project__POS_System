import tkinter as tk

root = tk.Tk()
root.minsize(960, 540)

data = {
  1: {
    "Hamburger": 3,
    "Fries": 2,
    "Pepsi": 1
  },
  2: {
    "Hamburger": 3,
    "Fries": 9,
    "Pepsi": 4
  },
  3: {
    "Hamburger": 3,
    "Fries": 2,
  },
  4: {
    "Fries": 5,
    "Pepsi": 3
  },
  5: {
    "Hamburger": 6,
    "Pepsi": 2
  }
}

#global variables
kitchenOrderInstances = {}
instanceWidth = 200

for orderNum, itemsInOrder in data.items():
  print(f"Order Number {orderNum}: ")
  instance = tk.Frame(root, width=instanceWidth, height=300, background="white")
  instance.pack_propagate(False)
  
  contentFrame = tk.Frame(instance)
  contentFrame.pack(expand=True, fill="both", padx=10, pady=10)
  tk.Label(contentFrame, text=f"Order Number {orderNum}").pack(fill="x", pady=10)

  for itemName, quantity in itemsInOrder.items():
    print(itemName, quantity)
    itemFrame = tk.Frame(contentFrame)

    tk.Label(itemFrame, text=itemName).pack(side="left", padx=10)
    tk.Label(itemFrame, text=quantity).pack(side="right", padx=10)

    itemFrame.pack(fill="x", pady=5)

  buttonsFrame = tk.Frame(instance)
  tk.Button(buttonsFrame, text="DONE", command=lambda num=orderNum, currentInstance=instance: tempRemoveInstance(num, currentInstance)).pack(side="left", padx=10)
  tk.Button(buttonsFrame, text="CANCEL", command=lambda num=orderNum, currentInstance=instance: tempRemoveInstance(num, currentInstance)).pack(side="left", padx=10)
  buttonsFrame.pack()
  print("======")
  kitchenOrderInstances[orderNum] = instance

def rearrangeInstances(event=None) :
  w = root.winfo_width()
  #print("width:" + str(w))

  columns = max(1, w // (instanceWidth + 30))
  #print("column amount: " + str(columns))

  for i, (orderNum, instance) in enumerate(kitchenOrderInstances.items()) :
    row_no = i // columns
    col_no = i % columns

    instance.grid(column=col_no, row=row_no, padx=15, pady=50)

def tempRemoveInstance(key, currentInstance) :
  print(key)
  currentInstance.destroy()
  del kitchenOrderInstances[key]
  rearrangeInstances()
  print("deleted!")

root.bind('<Configure>', rearrangeInstances)

root.mainloop()