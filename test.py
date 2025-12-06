import tkinter as tk

root = tk.Tk()
root.title("Table with Cell Borders (tk.Label)")

# Create a container frame for centering
table_container = tk.Frame(root)
table_container.pack(expand=True, anchor="center", padx=10, pady=10)

data = [
    ("Name", "Age", "City"),
    ("Alice", 30, "NY"),
    ("Bob", 25, "LA")
]

# Iterate to create and configure each cell
for r_index, row in enumerate(data):
    for c_index, item in enumerate(row):
        # 1. Create the Label (the cell)
        cell = tk.Label(
            table_container,
            text=str(item),
            width=15,
            anchor="center",
            padx=5,
            pady=3
        )
        
        # 2. Add the individual black border to the cell
        cell.config(
            relief="solid",      # Key for a visible black border
            borderwidth=1,       # Key for border thickness
            bg="lightgray" if r_index % 2 == 0 else "white" # Alternating row color
        )
        
        # 3. Use grid to place the cell
        # sticky="nsew" ensures the cell fills its grid space
        cell.grid(row=r_index, column=c_index, sticky="nsew")

# Configure the grid rows/columns to expand nicely (optional but good practice)
for i in range(len(data[0])):
    table_container.grid_columnconfigure(i, weight=1)

root.mainloop()