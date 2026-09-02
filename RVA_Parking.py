import tkinter as tk

MAX_LEN = 7
MAX_Time = 3

def check_plate():
    plate = user_input.get()

    if len(plate) == 0:
        result.config(text="Error: Please enter a license plate.")
    elif len(plate) > MAX_LEN:
        result.config(text="Error: License plate is invalid.")
    else:
        result.config(text=f"License plate {plate.upper()} accepted!")

# GUI setup
# Create window
window = tk.Tk()
window.title("License Plate")
window.geometry("350x200")

# Title
title = tk.Label(
    window,
    text="License Plate",
    foreground="White",
    background="Black"
)
title.pack(pady=10)

# Instructions
label = tk.Label(window, text="Enter your license plate:")
label.pack()

# License plate input
user_input = tk.Entry(window)
user_input.pack(pady=10)

# Result message
result = tk.Label(window, text="")
result.pack()

# Submit button
button = tk.Button(window, text="Submit", command=check_plate)
button.pack(pady=10)

window.mainloop()