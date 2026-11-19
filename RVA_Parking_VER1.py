import tkinter as tk
from tkinter import messagebox
import re
import webbrowser

MAX_LEN = 7
MAX_MINUTES = 180

# Demo in-memory account storage.
accounts = {}

# Holds registration information until DUO verification is completed.
pending_registration = {}

# Tracks the currently logged-in user and selected vehicle.
current_username = None
selected_vehicle = None


def valid_email(email):
    """Only allow VCU email addresses."""
    return re.fullmatch(
        r"[A-Za-z0-9._%+-]+@vcu\.edu",
        email,
        re.IGNORECASE
    ) is not None


def valid_non_vcu_email(email):
    # Must be a valid email
    valid_format = re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    )

    if valid_format is None:
        return False

    # Non-VCU users cannot register with @vcu.edu
    return not email.lower().endswith("@vcu.edu")


def valid_plate(plate):
    """License plate must contain 1-7 letters/numbers."""
    cleaned = plate.strip()
    return 1 <= len(cleaned) <= MAX_LEN and cleaned.isalnum()


def create_non_vcu_account():
    global current_username

    username = pending_registration["username"]

    accounts[username] = {
        "email": pending_registration["email"],
        "password": pending_registration["password"],
        "account_type": "Non-VCU",
        "verified": True,
        "vehicles": [
            pending_registration["license_plate"]
        ]
    }

    current_username = username

    messagebox.showinfo(
        "Registration",
        "Account created successfully!"
    )

    add_more = messagebox.askyesno(
        "Add Vehicle",
        "Would you like to add another vehicle?"
    )

    if add_more:
        show_frame(add_vehicle_frame)
    else:
        go_to_login_after_registration()


def show_frame(frame):
    """Hide all screens and display the requested screen."""
    for item in (
        home_frame,
        registration_frame,
        duo_frame,
        login_frame,
        add_vehicle_frame,
        vehicle_frame,
        parking_frame,
        map_frame
    ):
        item.pack_forget()

    frame.pack(fill="both", expand=True, padx=20, pady=10)

def cancel_registration():
    """Cancelling registation clears pending registration data and returns to the registration screen."""
    global pending_registration
    answer = messagebox.askyesno(
        title= 'Confirmation', 
        message='Are you sure you want to cancel registation? All entered information will be lost.'
        )
    if answer:
        pending_registration.clear()
        show_frame(registration_frame)
        messagebox.showinfo(
            "Registration Cancelled",
            "Your registration has been cancelled."
        )

def start_registration():
    """Validate registration information and route by account type."""
    global pending_registration

    username = reg_username.get().strip()
    email = reg_email.get().strip()
    plate = reg_plate.get().strip().upper()
    account_type = account_type_var.get()
    password = reg_password.get()

    if not username:
        registration_result.config(text="Error: Please enter a username.")
        return

    if account_type in ("VCU Student", "VCU Staff"):
        if not valid_email(email):
            registration_result.config(
                text="Error: VCU students and staff must use an @vcu.edu email."
            )
            return
    elif account_type == "Non-VCU":
        if not valid_non_vcu_email(email):
            registration_result.config(
                text="Error: Non-VCU users must use a valid non-VCU email address."
            )
            return
    else:
        registration_result.config(text="Error: Please select an account type.")
        return

    if not valid_plate(plate):
        registration_result.config(
            text="Error: License plate must be 1-7 letters/numbers."
        )
        return

    if not password:
        registration_result.config(text="Error: Please enter a password.")
        return

    if username in accounts:
        registration_result.config(text="Error: Username already exists.")
        return

    pending_registration = {
        "username": username,
        "email": email,
        "license_plate": plate,
        "account_type": account_type,
        "password": password
    }

    if account_type in ("VCU Student", "VCU Staff"):
        duo_code_entry.delete(0, tk.END)
        duo_result.config(text="")
        show_frame(duo_frame)
    else:
        create_non_vcu_account()

def verify_duo_code():
    """Demo DUO verification: code must contain exactly 5 digits."""
    global current_username

    code = duo_code_entry.get().strip()

    if len(code) != 5 or not code.isdigit():
        duo_result.config(
            text="Error: DUO code must be exactly 5 digits."
        )
        return

    username = pending_registration["username"]

    # Create the account after successful verification.
    accounts[username] = {
        "email": pending_registration["email"],
        "password": pending_registration["password"],
        "account_type": pending_registration["account_type"],
        "verified": True,
        "vehicles": [pending_registration["license_plate"]]
    }

    current_username = username

    messagebox.showinfo(
        "VCU Verification",
        "VCU verification successful. Account created!"
    )

    # Ask whether the user wants to register another vehicle.
    add_more = messagebox.askyesno(
        "Add Vehicle",
        "Would you like to add another vehicle?"
    )

    if add_more:
        additional_plate_entry.delete(0, tk.END)
        additional_vehicle_result.config(text="")
        show_frame(add_vehicle_frame)
    else:
        go_to_login_after_registration()


def add_vehicle():
    """Add another vehicle to the newly registered/current account."""
    plate = additional_plate_entry.get().strip().upper()

    if not valid_plate(plate):
        additional_vehicle_result.config(
            text="Error: License plate must be 1-7 letters/numbers."
        )
        return

    vehicles = accounts[current_username]["vehicles"]

    if plate in vehicles:
        additional_vehicle_result.config(
            text="Error: This vehicle is already registered."
        )
        return

    vehicles.append(plate)

    additional_vehicle_result.config(
        text=f"Vehicle {plate} added successfully!"
    )

    additional_plate_entry.delete(0, tk.END)

    add_more = messagebox.askyesno(
        "Add Another Vehicle",
        "Would you like to add another vehicle?"
    )

    if not add_more:
        go_to_login_after_registration()


def go_to_login_after_registration():
    """Send the newly registered user to the login screen."""
    username = current_username

    login_username.delete(0, tk.END)
    login_username.insert(0, username)
    login_password.delete(0, tk.END)
    login_result.config(
        text="Registration complete. Please log in."
    )
    show_frame(login_frame)


def login_user():
    """Log in and then let the user choose one of their vehicles."""
    global current_username

    username = login_username.get().strip()
    password = login_password.get()

    account = accounts.get(username)

    if account is None or account["password"] != password:
        login_result.config(
            text="Error: Invalid username or password."
        )
        return

    if not account["verified"]:
        login_result.config(
            text="Error: VCU account has not been verified."
        )
        return

    current_username = username
    login_result.config(text="Login successful!")
    show_vehicle_selection()


def show_vehicle_selection():
    """Display a button for every vehicle saved to the user's account."""
    for widget in vehicle_buttons_frame.winfo_children():
        widget.destroy()

    vehicle_title.config(
        text=f"{current_username}, select your vehicle"
    )

    vehicles = accounts[current_username]["vehicles"]

    for plate in vehicles:
        tk.Button(
            vehicle_buttons_frame,
            text=plate,
            width=20,
            command=lambda p=plate: select_vehicle(p)
        ).pack(pady=5)

    show_frame(vehicle_frame)


def select_vehicle(plate):
    global selected_vehicle

    selected_vehicle = plate

    vehicle_frame.pack_forget()
    parking_frame.pack(fill="both", expand=True)

    dashboard_welcome.config(
        text=f"Parking Vehicle: {plate}"
    )

    # Automatically use the selected vehicle
    user_input.delete(0, tk.END)
    user_input.insert(0, plate)

    result.config(
        text=f"Selected vehicle: {plate}"
    )

    # Hide plate entry because the user already selected a car
    plate_label.pack_forget()
    user_input.pack_forget()
    plate_button.pack_forget()

    # Immediately ask for parking time
    time_label.pack(pady=5)
    time_input.pack(pady=5)
    time_button.pack(pady=5)

    time_input.delete(0, tk.END)
    time_result.config(text="")


def continue_as_guest():
    """Guests skip registration/login and enter plate, time, then zone."""
    global current_username, selected_vehicle

    current_username = None
    selected_vehicle = None

    dashboard_welcome.config(text="Guest Parking")

    # IMPORTANT: registered users hide these widgets after choosing a saved car,
    # so a guest must explicitly show them again.
    plate_label.pack()
    user_input.pack(pady=5)
    plate_button.pack(pady=5)

    # Make sure the license-plate Entry can be edited.
    user_input.config(state="normal")
    user_input.delete(0, tk.END)

    result.config(text="Enter your license plate to continue.")

    reset_time_section()
    show_frame(parking_frame)


def reset_time_section():
    """Reset and hide the time controls until a plate is accepted."""
    time_input.delete(0, tk.END)
    time_result.config(text="")

    time_label.pack_forget()
    time_input.pack_forget()
    time_button.pack_forget()


def check_plate():
    """Validate the plate and then allow the user to enter parking time."""
    plate = user_input.get().strip().upper()

    if len(plate) == 0:
        result.config(
            text="Error: Please enter a license plate."
        )
        return

    if not valid_plate(plate):
        result.config(
            text="Error: Invalid license plate."
        )
        return

    result.config(
        text=f"License plate {plate} accepted!"
    )

    time_label.pack(pady=5)
    time_input.pack(pady=5)
    time_button.pack(pady=5)


def submit_time():
    """Validate parking duration."""
    duration = time_input.get().strip()

    if duration == "":
        time_result.config(
            text="Error: Please enter a time duration."
        )
        return

    try:
        hours, minutes = duration.split(":")
        hours = int(hours)
        minutes = int(minutes)
    except ValueError:
        time_result.config(
            text="Error: Use time format HH:MM."
        )
        return

    if hours < 0 or minutes < 0 or minutes >= 60:
        time_result.config(
            text="Error: Invalid time."
        )
        return

    if minutes % 5 != 0:
        time_result.config(
            text="Error: Time must be in 5-minute intervals."
        )
        return

    total_minutes = (hours * 60) + minutes

    if total_minutes < 5 or total_minutes > MAX_MINUTES:
        time_result.config(
            text="Error: Time must be between 00:05 and 03:00."
        )
        return

    formatted_time = f"{hours:02d}:{minutes:02d}"

    time_result.config(
        text=f"Parking duration: {formatted_time}"
    )

    # After a valid parking duration, ask for the 6-digit parking zone.
    street_entry.delete(0, tk.END)
    
    show_frame(map_frame)

RICHMOND_MAP_URL = (
    "https://cor.maps.arcgis.com/apps/webappviewer/index.html"
    "?id=a49210548bc24ad08d7dc0bf1e2c77b3"
)


def open_parking_map():
    """Open the city's interactive parking map in the default browser."""
    webbrowser.open(RICHMOND_MAP_URL)


#def continue_to_zone():
 #   """Move from the map step to the parking zone entry screen."""
  #  show_frame(zone_frame)


def submit_street():
    """Confirm parking using the selected street."""

    street = street_entry.get().strip()

    # Makes sure the user entered a street
    if not street:
        messagebox.showerror(
            "Invalid Street",
            "Please enter the street where you are parking."
        )
        return

    # Gets the selected license plate
    plate = selected_vehicle

    if plate is None:
        plate = user_input.get().strip().upper()

    # Gets the parking duration
    duration = time_input.get().strip()

    # Displays the parking session details
    messagebox.showinfo(
        "Parking Session Confirmed",
        f"Parking Session Complete!\n\n"
        f"License Plate: {plate}\n"
        f"Parking Duration: {duration}\n"
        f"Street: {street}"
    )


def exit_to_registration():
    # Clear parking information
    street_entry.delete(0, tk.END)
    

    time_input.delete(0, tk.END)
    time_result.config(text="")

    user_input.delete(0, tk.END)
    result.config(text="")

    # Return to registration screen
    show_frame(registration_frame)


def logout():
    """Return a registered user to the login screen."""
    global current_username, selected_vehicle

    current_username = None
    selected_vehicle = None

    login_password.delete(0, tk.END)
    show_frame(login_frame)


# ---------------- GUI ----------------

window = tk.Tk()
window.title("RVA Parking")
window.geometry("520x650")

header = tk.Label(
    window,
    text="RVA Parking",
    font=("Arial", 18, "bold")
)
header.pack(pady=(12, 2))

nav = tk.Frame(window)
nav.pack(pady=5)

registration_frame = tk.Frame(window)
home_frame = tk.Frame(window)
duo_frame = tk.Frame(window)
login_frame = tk.Frame(window)
add_vehicle_frame = tk.Frame(window)
vehicle_frame = tk.Frame(window)
parking_frame = tk.Frame(window)
map_frame = tk.Frame(window)


def labeled_entry(parent, label, show=None):
    tk.Label(parent, text=label).pack(anchor="w")

    entry = tk.Entry(
        parent,
        width=42,
        show=show
    )
    entry.pack(pady=(0, 7))

    return entry

# ---------------- HOME SCREEN ----------------

tk.Label(
    home_frame,
    text="Welcome to RVA Parking",
    font=("Arial", 15, "bold")
).pack(pady=12)

tk.Label(
    home_frame,
    text="Please register or log in to continue."
).pack(pady=5)

tk.Button(
    home_frame,
    text="Register",
    command=lambda: show_frame(registration_frame)
).pack(pady=5)

tk.Button(
    home_frame,
    text="Login",
    command=lambda: show_frame(login_frame)
).pack(pady=5)

tk.Button(
    home_frame,
    text="Continue as Guest",
    command=continue_as_guest
).pack(pady=5)

# ---------------- REGISTRATION SCREEN ----------------

tk.Label(
    registration_frame,
    text="Rva parking Registration",
    font=("Arial", 15, "bold")
).pack(pady=8)

reg_username = labeled_entry(
    registration_frame,
    "Username / Name:"
)

reg_email = labeled_entry(
    registration_frame,
    "Enter Email Address:"
)

reg_plate = labeled_entry(
    registration_frame,
    "License Plate:"
)

tk.Label(
    registration_frame,
    text="Account Type:"
).pack(anchor="w")

account_type_var = tk.StringVar(value="VCU Student")

tk.OptionMenu(
    registration_frame,
    account_type_var,
    "VCU Student",
    "VCU Staff",
    "Non-VCU"
).pack(anchor="w", pady=(0, 7))

reg_password = labeled_entry(
    registration_frame,
    "Password:",
    show="*"
)

tk.Button(
    registration_frame,
    text="Continue Registration",
    command=start_registration
).pack(pady=8)

tk.Button(
    registration_frame,
    text="Cancel Registration",
    command=lambda: cancel_registration()
).pack(pady=5)

tk.Button(
    registration_frame,
    text="Continue as Guest",
    command=continue_as_guest
).pack(pady=5)

registration_result = tk.Label(
    registration_frame,
    text="",
    wraplength=450
)
registration_result.pack(pady=5)


# ---------------- DUO SCREEN ----------------

tk.Label(
    duo_frame,
    text="VCU DUO Verification",
    font=("Arial", 15, "bold")
).pack(pady=8)

tk.Label(
    duo_frame,
    text="Enter the 5-digit verification code from DUO:"
).pack(pady=5)

duo_code_entry = tk.Entry(
    duo_frame,
    width=20
)
duo_code_entry.pack(pady=5)

tk.Button(
    duo_frame,
    text="Verify Code",
    command=verify_duo_code
).pack(pady=8)

duo_result = tk.Label(
    duo_frame,
    text="",
    wraplength=450
)
duo_result.pack(pady=5)


# ---------------- ADD VEHICLE SCREEN ----------------

tk.Label(
    add_vehicle_frame,
    text="Add Another Vehicle",
    font=("Arial", 15, "bold")
).pack(pady=8)

tk.Label(
    add_vehicle_frame,
    text="Enter the additional vehicle's license plate:"
).pack(pady=5)

additional_plate_entry = tk.Entry(
    add_vehicle_frame,
    width=30
)
additional_plate_entry.pack(pady=5)

tk.Button(
    add_vehicle_frame,
    text="Add Vehicle",
    command=add_vehicle
).pack(pady=8)

additional_vehicle_result = tk.Label(
    add_vehicle_frame,
    text=""
)
additional_vehicle_result.pack(pady=5)


# ---------------- LOGIN SCREEN ----------------

tk.Label(
    login_frame,
    text="Login",
    font=("Arial", 15, "bold")
).pack(pady=8)

login_username = labeled_entry(
    login_frame,
    "Username:"
)

login_password = labeled_entry(
    login_frame,
    "Password:",
    show="*"
)

tk.Button(
    login_frame,
    text="Log In",
    command=login_user
).pack(pady=8)

tk.Button(
    login_frame,
    text="Continue as Guest",
    command=continue_as_guest
).pack(pady=5)

login_result = tk.Label(
    login_frame,
    text="",
    wraplength=450
)
login_result.pack(pady=5)


# ---------------- VEHICLE SELECTION SCREEN ----------------

vehicle_title = tk.Label(
    vehicle_frame,
    text="Select Your Vehicle",
    font=("Arial", 15, "bold")
)
vehicle_title.pack(pady=8)

tk.Label(
    vehicle_frame,
    text="Which vehicle are you parking today?"
).pack(pady=5)

vehicle_buttons_frame = tk.Frame(vehicle_frame)
vehicle_buttons_frame.pack(pady=10)


# ---------------- PARKING SCREEN ----------------

dashboard_welcome = tk.Label(
    parking_frame,
    text="Dashboard",
    font=("Arial", 15, "bold")
)
dashboard_welcome.pack(pady=8)

plate_label = tk.Label(
    parking_frame,
    text="Enter your license plate:"
)
plate_label.pack()

user_input = tk.Entry(parking_frame)
user_input.pack(pady=5)

plate_button = tk.Button(
    parking_frame,
    text="Submit License Plate",
    command=check_plate
)
plate_button.pack(pady=5)

result = tk.Label(
    parking_frame,
    text=""
)
result.pack(pady=5)

time_label = tk.Label(
    parking_frame,
    text="Enter parking duration (HH:MM):"
)

time_input = tk.Entry(parking_frame)

time_button = tk.Button(
    parking_frame,
    text="Submit Time",
    command=submit_time
)

time_result = tk.Label(
    parking_frame,
    text=""
)
time_result.pack(pady=10)

tk.Button(
    parking_frame,
    text="Return to Login",
    command=lambda: show_frame(login_frame)
).pack(pady=15)


# ---------------- Richmond Paid Parking Map ----------------

tk.Label(
    map_frame,
    text="Richmond Parking Map",
    font=("Arial", 15,"bold")
).pack(pady=12)

tk.Label(
    map_frame,
    text="View the map before beggining your parking session",
    wraplength=450,
    justify="center"
).pack(pady=12)

tk.Button(
    map_frame,
    text="Open Interactive Parking Map",
    command=open_parking_map
).pack(pady=8)

tk.Label(
    map_frame,
    text="Return to RVA Parking after viewing the map.",
    wraplength=450,
    justify="center"
).pack(pady=12)

# Asks the user for their parking street
tk.Label(
    map_frame,
    text="Enter the street where you are parking:"
).pack(pady=5)

# Stores the street entered by the user
street_entry = tk.Entry(
    map_frame,
    width=35
)
street_entry.pack(pady=5)

# Completes the parking session
tk.Button(
    map_frame,
    text="Complete Parking Session",
    command=submit_street
).pack(pady=15)


tk.Button(
    map_frame,
    text="Exit",
    command=exit_to_registration
).pack(pady=10)


# ---------------- PARKING ZONE SCREEN ----------------

#tk.Label(
   # zone_frame,
  #  text="Enter Parking Zone",
 #   font=("Arial", 15, "bold")
#).pack(pady=10)

#tk.Label(
  #  zone_frame,
 #   text="Enter the 6-digit parking zone number:"
#).pack(pady=5)

#zone_entry = tk.Entry(zone_frame, width=20)
#zone_entry.pack(pady=5)

#tk.Button(
  #  zone_frame,
 #   text="Submit Zone",
    #command=submit_zone
#).pack(pady=8)

#tk.Button(
   # zone_frame,
  #  text="Exit",
 #   command=exit_to_registration
#).pack(pady=10)

#zone_result = tk.Label(
   # zone_frame,
  #  text="",
 #   wraplength=450
#)
#zone_result.pack(pady=5)


# ---------------- TOP NAVIGATION ----------------

tk.Button(
    nav,
    text="Home",
    command=lambda: show_frame(home_frame)
).pack(side="left", padx=5)

tk.Button(
    nav,
    text="Register",
    command=lambda: show_frame(registration_frame)
).pack(side="left", padx=5)

tk.Button(
    nav,
    text="Login",
    command=lambda: show_frame(login_frame)
).pack(side="left", padx=5)

#tk.Button(
  #  nav,
   ## command=continue_as_guest
#).pack(side="left", padx=5)""


show_frame(home_frame)

window.mainloop()

# NOTE:
# Link DUO
