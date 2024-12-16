import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random
import string
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import os
import hashlib
import json
import platform
import sys

# Resource path function for PyInstaller compatibility
def resource_path(relative_path):
    """ Get the absolute path to a resource. Works for PyInstaller and during development."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

# Directory and File Setup
# Determine the directory dynamically based on the OS
def get_user_data_directory():
    if platform.system() == "Windows":
        # Use AppData for Windows
        base_dir = os.getenv("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    else:
        # Use ~/.config for macOS/Linux
        base_dir = os.path.expanduser("~/.config")

    # Append the application folder name
    app_dir = os.path.join(base_dir, "PassGuardian")

    # Ensure the directory exists
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    return app_dir

USER_DATA_DIR = get_user_data_directory()
USER_DATA_FILE = os.path.join(USER_DATA_DIR, "user_data.json")
KEY_FILE = os.path.join(USER_DATA_DIR, "key.key")

# Generate or Load Encryption Key
def generate_key():
    return Fernet.generate_key()

def load_or_generate_key():
    if not os.path.exists(KEY_FILE):
        key = generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

# Initialize key
key = load_or_generate_key()

# Load or initialize user data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Hashing function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Encryption/Decryption functions
def encrypt_password(key, password):
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(key, encrypted_password):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

# Password generation
def generate_random_password():
    length = 12  # Default length for a strong password
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    random_password_entry.delete(0, tk.END)
    random_password_entry.insert(0, password)

# Store passwords in a list
passwords = []

# Save passwords for the logged-in user
def save_user_passwords():
    user_data = load_user_data()
    user_data[logged_in_user]['passwords'] = passwords
    save_user_data(user_data)

# Load passwords for the logged-in user
def load_user_passwords():
    global passwords
    user_data = load_user_data()
    passwords = user_data.get(logged_in_user, {}).get('passwords', [])

# Add a new password
def add_password():
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if service and username and password:
        encrypted_password = encrypt_password(key, password)
        passwords.append({'service': service, 'username': username, 'password': encrypted_password})
        save_user_passwords()  # Save passwords
        messagebox.showinfo("Success", "Password added successfully!")
        service_entry.delete(0, tk.END)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Error", "Please fill in all the fields.")

# Retrieve and show saved passwords with search functionality
def get_password():
    def search_password():
        service_name = search_entry.get().strip()
        if service_name:
            matching_passwords = [
                entry for entry in passwords if service_name.lower() in entry['service'].lower()
            ]
            if matching_passwords:
                search_results = ""
                for entry in matching_passwords:
                    decrypted_password = decrypt_password(key, entry['password'])
                    search_results += f"Service: {entry['service']}\nUsername: {entry['username']}\nPassword: {decrypted_password}\n\n"
                results_label.config(text=search_results)
            else:
                results_label.config(text="No results found for the given service name.")
        else:
            results_label.config(text="Please enter a service name to search.")

    # Create a new window for password retrieval and search
    password_window = tk.Toplevel(window)
    password_window.title("Saved Passwords")
    password_window.geometry("600x400")

    tk.Label(password_window, text="Search by Service Name:", font=("Garamond", 14)).pack(pady=10)
    search_entry = ttk.Entry(password_window, width=40, font=("Georgia", 12))
    search_entry.pack(pady=5)

    ttk.Button(password_window, text="Search", command=search_password).pack(pady=10)

    results_label = tk.Label(password_window, text="", font=("Georgia", 12), justify="left", wraplength=500)
    results_label.pack(pady=10)

    if passwords:
        all_passwords = ""
        for entry in passwords:
            decrypted_password = decrypt_password(key, entry['password'])
            all_passwords += f"Service: {entry['service']}\nUsername: {entry['username']}\nPassword: {decrypted_password}\n\n"
        results_label.config(text=all_passwords)
    else:
        results_label.config(text="No passwords saved yet.")

# Clear all saved passwords
def clear_passwords():
    global passwords
    passwords = []
    save_user_passwords()
    messagebox.showinfo("Success", "All passwords cleared!")

# Toggle visibility of the password
def toggle_password_visibility(entry, toggle_button):
    current_show = entry.cget('show')
    if current_show == '*':
        entry.config(show='')  # Show the password
        toggle_button.config(text="Hide")
    else:
        entry.config(show='*')  # Hide the password
        toggle_button.config(text="Show")

# User login page
def show_login_page():
    login_window = tk.Tk()
    login_window.title("User Login")
    login_window.state('zoomed')  # Make the window fullscreen

    # Set background image
    background_image = Image.open(resource_path(r"C:\Users\Omkar Pandey\Pictures\Passguardian\neon.png"))
    background_image = background_image.resize((login_window.winfo_screenwidth(), login_window.winfo_screenheight()), Image.Resampling.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(login_window, image=background_photo)
    background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Centered frame for login inputs
    login_frame = ttk.Frame(login_window, padding="20")
    login_frame.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(login_frame, text="Username:", font=("Garamond", 14)).grid(row=0, column=0, pady=10, padx=10, sticky="E")
    username_entry = ttk.Entry(login_frame, width=30, font=("Georgia", 12))
    username_entry.grid(row=0, column=1, pady=10, padx=10)

    ttk.Label(login_frame, text="Master Password:", font=("Garamond", 14)).grid(row=1, column=0, pady=10, padx=10, sticky="E")
    password_entry = ttk.Entry(login_frame, width=30, font=("Georgia", 12), show="*")
    password_entry.grid(row=1, column=1, pady=10, padx=10)

    # Password visibility toggle button
    toggle_button = ttk.Button(login_frame, text="Show")
    toggle_button.config(command=lambda: toggle_password_visibility(password_entry, toggle_button))
    toggle_button.grid(row=1, column=2, padx=5)

    ttk.Button(login_frame, text="Login", command=lambda: login(username_entry, password_entry, login_window)).grid(row=2, column=0, columnspan=3, pady=15)
    ttk.Button(login_frame, text="Register", command=lambda: register(username_entry, password_entry)).grid(row=3, column=0, columnspan=3, pady=5)

    login_window.mainloop()

# Login Functionality
def login(username_entry, password_entry, login_window):
    username = username_entry.get()
    password = password_entry.get()
    user_data = load_user_data()

    if username in user_data and user_data[username]['password'] == hash_password(password):
        global logged_in_user
        logged_in_user = username
        messagebox.showinfo("Success", f"Welcome, {username}!")
        login_window.destroy()
        load_user_passwords()
        show_main_window()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# Register Functionality
def register(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()
    user_data = load_user_data()

    if username in user_data:
        messagebox.showerror("Error", "Username already exists.")
    elif not username or not password:
        messagebox.showerror("Error", "Both fields are required.")
    else:
        user_data[username] = {'password': hash_password(password), 'passwords': []}
        save_user_data(user_data)
        messagebox.showinfo("Success", "User registered successfully!")

# Main window
def show_main_window():
    global window, service_entry, username_entry, password_entry, random_password_entry
    window = tk.Tk()
    window.title("PassGuardian")
    window.state('zoomed')  # Make the window fullscreen

    # Set background image
    background_image = Image.open(resource_path(r"C:\Users\Omkar Pandey\Pictures\Passguardian\too.png"))
    background_image = background_image.resize((window.winfo_screenwidth(), window.winfo_screenheight()), Image.Resampling.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(window, image=background_photo)
    background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Display logged-in user's name
    user_name_label = tk.Label(window, text=f"Logged in as: {logged_in_user}", font=("Georgia", 14), bg="#1f1f1f", fg="white")
    user_name_label.place(relx=0.85, rely=0.05, anchor="ne")  # Top-right corner

    # Central frame
    center_frame = ttk.Frame(window, padding="30")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    instruction_label = ttk.Label(center_frame, text="Store your passwords securely with PassGuardian!", wraplength=500, font=("Times New Roman", 16, "italic"))
    instruction_label.grid(row=0, column=0, columnspan=2, pady=20)

    ttk.Label(center_frame, text="Account:", font=("Garamond", 14)).grid(row=1, column=0, sticky="E", pady=10, padx=10)
    service_entry = ttk.Entry(center_frame, width=35, font=("Georgia", 12))
    service_entry.grid(row=1, column=1, pady=10)

    ttk.Label(center_frame, text="Username:", font=("Garamond", 14)).grid(row=2, column=0, sticky="E", pady=10, padx=10)
    username_entry = ttk.Entry(center_frame, width=35, font=("Georgia", 12))
    username_entry.grid(row=2, column=1, pady=10)

    ttk.Label(center_frame, text="Password:", font=("Garamond", 14)).grid(row=3, column=0, sticky="E", pady=10, padx=10)
    password_entry = ttk.Entry(center_frame, width=35, font=("Georgia", 12), show="*")
    password_entry.grid(row=3, column=1, pady=10)

    # Add toggle button for password visibility in the main window
    toggle_main_button = ttk.Button(center_frame, text="Show", command=lambda: toggle_password_visibility(password_entry, toggle_main_button))
    toggle_main_button.grid(row=3, column=2, padx=5)

    ttk.Label(center_frame, text="Generated Password:", font=("Garamond", 14)).grid(row=4, column=0, sticky="E", pady=10, padx=10)
    random_password_entry = ttk.Entry(center_frame, width=35, font=("Georgia", 12))
    random_password_entry.grid(row=4, column=1, pady=10)

    ttk.Button(center_frame, text="Generate Password", command=generate_random_password).grid(row=5, column=0, columnspan=2, pady=10)
    ttk.Button(center_frame, text="Add Password", command=add_password).grid(row=6, column=0, columnspan=2, pady=15)
    ttk.Button(center_frame, text="Get Passwords", command=get_password).grid(row=7, column=0, columnspan=2, pady=10)
    ttk.Button(center_frame, text="Clear Saved Passwords", command=clear_passwords).grid(row=8, column=0, columnspan=2, pady=10)

    window.mainloop()

# Show splash screen
def show_splash_screen():
    global splash_window
    splash_window = tk.Tk()
    splash_window.title("Welcome")

    # Set splash screen size and position
    screen_width = splash_window.winfo_screenwidth()
    screen_height = splash_window.winfo_screenheight()
    splash_window.geometry(f"{screen_width}x{screen_height}")
    splash_window.overrideredirect(True)

    # Load and set the splash image
    splash_image = Image.open(resource_path(r"C:\Users\Omkar Pandey\Pictures\Passguardian\outside.png"))
    splash_image = splash_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    splash_photo = ImageTk.PhotoImage(splash_image)
    splash_label = tk.Label(splash_window, image=splash_photo)
    splash_label.pack()

    # Create a rounded rectangle effect using a Canvas
    canvas = tk.Canvas(splash_window, width=210, height=60, bg="white", highlightthickness=0)
    canvas.place(relx=0.5, rely=0.8, anchor="center")
    canvas.create_oval(0, 0, 210, 60, fill="#4CAF50", outline="#4CAF50")

    # Place the button directly over the canvas
    enter_button = tk.Button(
        splash_window,
        text="ENTER INSIDE",
        font=("Garamond", 16, "bold"),
        bg="#4CAF50",
        fg="white",
        relief="flat",
        borderwidth=0,
        activebackground="#45A049",
        activeforeground="white",
        command=lambda: (splash_window.destroy(), show_login_page())
    )
    enter_button.place(relx=0.5, rely=0.8, anchor="center", width=200, height=50)

    splash_window.mainloop()

# Start the program with the splash screen
show_splash_screen()
