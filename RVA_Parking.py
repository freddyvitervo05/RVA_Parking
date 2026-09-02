import tkinter as tk

MAX_LEN = 7
MAX_MINUTES = 180


def check_plate():
    plate = user_input.get()

    if len(plate) == 0:
        result.config(text="Error: Please enter a license plate.")

    elif len(plate) > MAX_LEN:
        result.config(text="Error: Invalid license plate.")

    else:
        result.config(text=f"License plate {plate.upper()} accepted!")

        # Show time duration section
        time_label.pack(pady=5)
        time_input.pack(pady=5)
        time_button.pack(pady=5)


def submit_time():
    duration = time_input.get()

    if duration == "":
        time_result.config(text="Error: Please enter a time duration.")
        return

    try:
        # Split HH:MM
        hours, minutes = duration.split(":")

        hours = int(hours)
        minutes = int(minutes)

    except ValueError:
        time_result.config(text="Error: Use time format HH:MM.")
        return

    # Minutes must be valid
    if minutes < 0 or minutes >= 60:
        time_result.config(text="Error: Invalid minutes.")
        return

    # Must be in 5-minute intervals
    if minutes % 5 != 0:
        time_result.config(text="Error: Time must be in 5-minute intervals.")
        return

    # Convert everything to minutes
    total_minutes = (hours * 60) + minutes

    # Must be between 5 minutes and 3 hours
    if total_minutes < 5 or total_minutes > MAX_MINUTES:
        time_result.config(text="Error: Time must be between 00:05 and 03:00.")
        return

    # Format back into HH:MM
    formatted_time = f"{hours:02d}:{minutes:02d}"

    time_result.config(
        text=f"Parking duration: {formatted_time}"
    )


# Create window
window = tk.Tk()
window.title("Parking Calculator")
window.geometry("400x350")


# Title
title = tk.Label(
    window,
    text="Parking Calculator",
    foreground="white",
    background="black"
)
title.pack(pady=10)


# License plate
plate_label = tk.Label(
    window,
    text="Enter your license plate:"
)
plate_label.pack()

user_input = tk.Entry(window)
user_input.pack(pady=5)

plate_button = tk.Button(
    window,
    text="Submit License Plate",
    command=check_plate
)
plate_button.pack(pady=5)

result = tk.Label(window, text="")
result.pack(pady=5)


# Time duration
time_label = tk.Label(
    window,
    text="Enter parking duration (HH:MM):"
)

time_input = tk.Entry(window)

time_button = tk.Button(
    window,
    text="Submit Time",
    command=submit_time
)

time_result = tk.Label(window, text="")
time_result.pack(pady=10)


window.mainloop()


# hookup dmv via api
