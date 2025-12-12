from tkinter import *

class FlexFrame(Frame):
    def __init__(self, parent, item_width, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.item_width = item_width # The width of your "images"
        self.items = []              # List to hold the widgets
        
        # Bind the resize event to our recalculation function
        self.bind('<Configure>', self.rearrange)

    def add_item(self, widget):
        self.items.append(widget)

    def rearrange(self, event):
        # 1. Get current width of the container
        w = event.width
        
        # 2. Calculate how many items fit in a row
        # We use max(1, ...) to ensure we don't divide by zero or get 0 columns
        columns = max(1, w // self.item_width)
        
        # 3. Grid the items based on the calculated columns
        for i, widget in enumerate(self.items):
            row_num = i // columns
            col_num = i % columns
            
            # Reposition the widget
            widget.grid(row=row_num, column=col_num, padx=5, pady=5)

# --- Setup ---
root = Tk()
root.title("Tkinter Flex-Wrap Logic")
root.geometry("600x400")

# Create our custom container. 
# We assume every "image" is roughly 150px wide.
container = FlexFrame(root, item_width=150, bg="gray")
container.pack(fill=BOTH, expand=True)

# Create dummy "Images"
colors = ["#ff7979", "#badc58", "#f9ca24", "#686de0", "#e056fd", "#7ed6df"]

for i in range(12):
    # Create a frame to act as a placeholder for an image
    # We force the size to 140x100
    frame = Frame(container, bg=colors[i % len(colors)], width=140, height=100)
    frame.pack_propagate(False) # Stop frame from shrinking
    
    # Add a label inside just for clarity
    Label(frame, text=f"Img {i+1}", bg=colors[i % len(colors)]).pack(expand=True)
    
    # Register it with our FlexFrame
    container.add_item(frame)

root.mainloop()