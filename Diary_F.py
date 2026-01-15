import tkinter
from tkinter import messagebox, filedialog
import mysql.connector
from datetime import datetime

# Database connection
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="", 
            database="digital_diary"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# Check if user exists
def user_exists(username):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return result is not None
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            connection.close()
    return False

# Register new user
def register_user(username, password):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            values = (username, password)
            cursor.execute(query, values)
            connection.commit()
            messagebox.showinfo("Success", "User registered successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

# Login functionality
def login():
    username = username_entry.get()
    password = password_entry.get()

    if user_exists(username):
        connection = connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                result = cursor.fetchone()
                if result:
                    messagebox.showinfo("Login Success", f"Welcome, {username}!")
                    show_frame(input_page)
                else:
                    messagebox.showerror("Error", "Invalid password")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
    else:
        if messagebox.askyesno("User Not Found", "User not found. Would you like to register?"):
            register_user(username, password)

# Register functionality
def register():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Username and password are required!")
        return

    if user_exists(username):
        messagebox.showerror("Error", "Username already exists!")
    else:
        register_user(username, password)

# Encoding and decoding logic using shift
def encode(content, shift):
    encoded = ""
    for char in content:
        encoded += chr((ord(char) + shift) % 256)
    return encoded

def decode(encoded_content, shift):
    decoded = ""
    for char in encoded_content:
        decoded += chr((ord(char) - shift) % 256)
    return decoded

# Save input to file in encoded form
def save_input():
    username = username_entry.get()
    date = date_entry.get()  
    mood = mood_entry.get()
    content = text.get("1.0", tkinter.END).strip()

    if not username or not date or not mood or not content:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    shift = 3

    # Encode the content using the encode function
    encoded_content = encode(content, shift)

    # Save to file with the format username_date.txt
    filename = f"{username}_{date}.txt"
    with open(filename, "w") as file:
        file.write(f"Username: {username}\n")
        file.write(f"Date: {date}\n")
        file.write(f"Mood: {mood}\n")
        file.write(f"Content: {encoded_content}\n")

    messagebox.showinfo("Success", f"Input saved to {filename} in encoded form!")

# Clear input fields
def clear_input():
    date_entry.delete(0, tkinter.END)
    mood_entry.delete(0, tkinter.END)
    text.delete("1.0", tkinter.END)

# View files in encoded form
def view_files():
    filepath = filedialog.askopenfilename(title="Select a file", filetypes=[("Text Files", "*.txt")])
    if filepath:
        with open(filepath, "r") as file:
            lines = file.readlines()
            encoded_content = lines[3].split("Content: ")[1].strip()  # Extract the encoded content

       
        shift = 3

        # Decode the content using the decode function
        decoded_content = decode(encoded_content, shift)
        messagebox.showinfo("File Content (Decoded)", decoded_content)

# Navigate between frames
def show_frame(frame):
    frame.tkraise()

# Forgot Password functionality
def forgot_password():
    def reset_password():
        username = username_forgot_entry.get()
        new_password = new_password_entry.get()

        if not username or not new_password:
            messagebox.showerror("Error", "Username and new password are required!")
            return

        if user_exists(username):
            connection = connect_to_db()
            if connection:
                try:
                    cursor = connection.cursor()
                    query = "UPDATE users SET password = %s WHERE username = %s"
                    cursor.execute(query, (new_password, username))
                    connection.commit()
                    messagebox.showinfo("Success", "Password reset successfully!")
                    forgot_password_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error: {err}")
                finally:
                    cursor.close()
                    connection.close()
        else:
            messagebox.showerror("Error", "Username not found!")

    forgot_password_window = tkinter.Toplevel(window)
    forgot_password_window.title("Forgot Password")
    forgot_password_window.configure(bg='pink')
    forgot_password_window.geometry("400x200")

    tkinter.Label(forgot_password_window, text="Username:", bg="pink", fg="black", font=("Algerian", 14)).grid(row=0, column=0, pady=5, sticky="e")
    username_forgot_entry = tkinter.Entry(forgot_password_window, font=("Arial", 14))
    username_forgot_entry.grid(row=0, column=1, pady=5, padx=10)

    tkinter.Label(forgot_password_window, text="New Password:", bg="pink", fg="black", font=("Algerian", 14)).grid(row=1, column=0, pady=5, sticky="e")
    new_password_entry = tkinter.Entry(forgot_password_window, font=("Arial", 14), show="*")
    new_password_entry.grid(row=1, column=1, pady=5, padx=10)

    tkinter.Button(forgot_password_window, text="Reset Password", font=("Algerian", 14), command=reset_password).grid(row=2, column=0, columnspan=2, pady=20)

# Main Window
window = tkinter.Tk()
window.title("Digital Diary")
window.configure(bg='pink')
window.geometry("950x600")

# Define frames for different pages
login_page = tkinter.Frame(window, bg='pink')
input_page = tkinter.Frame(window, bg='pink')

for frame in (login_page, input_page):
    frame.grid(row=0, column=0, sticky="nsew")

# --- Login Page ---
tkinter.Label(login_page, text="Login Page", bg="pink", fg="black", font=("Algerian", 20)).grid(row=0, column=0, pady=20)

tkinter.Label(login_page, text="Username:", bg="pink", fg="black", font=("Algerian", 14)).grid(row=1, column=0, pady=5, sticky="e")
username_entry = tkinter.Entry(login_page, font=("Arial", 14))
username_entry.grid(row=1, column=1, pady=5, padx=10)

tkinter.Label(login_page, text="Password:", bg="pink", fg="black", font=("Algerian", 14)).grid(row=2, column=0, pady=5, sticky="e")
password_entry = tkinter.Entry(login_page, font=("Arial", 14), show="*")
password_entry.grid(row=2, column=1, pady=5, padx=10)

# Login, Register, and Forgot Password buttons
tkinter.Button(login_page, text="Login", font=("Algerian", 14), command=login).grid(row=3, column=0, pady=20, padx=10, sticky="e")
tkinter.Button(login_page, text="Register", font=("Algerian", 14), command=register).grid(row=3, column=1, pady=20, padx=10, sticky="w")
tkinter.Button(login_page, text="Forgot Password", font=("Algerian", 14), command=forgot_password).grid(row=4, column=0, columnspan=2, pady=10)

# --- Input Page ---
tkinter.Label(input_page, text="Input Page", font=("Algerian", 24), bg="pink", fg="black").grid(row=0, column=0, pady=20)

# Date Entry
tkinter.Label(input_page, text="Enter Date (YYYY-MM-DD):", font=("Algerian", 14), bg="pink", fg="black").grid(row=1, column=0, pady=5, sticky="e")
date_entry = tkinter.Entry(input_page, font=("Arial", 14))
date_entry.grid(row=1, column=1, pady=5, padx=10)

# Mood Entry
tkinter.Label(input_page, text="Enter Mood:", font=("Algerian", 14), bg="pink", fg="black").grid(row=2, column=0, pady=5, sticky="e")
mood_entry = tkinter.Entry(input_page, font=("Arial", 14))
mood_entry.grid(row=2, column=1, pady=5, padx=10)

# Content Entry
text = tkinter.Text(input_page, wrap="word", font=("Algerian", 14), height=15, width=40)
text.grid(row=3, column=0, columnspan=2, pady=10, padx=10)

# Buttons
tkinter.Button(input_page, text="Save", font=("Algerian", 14), command=save_input).grid(row=4, column=0, padx=20, pady=10, sticky="w")
tkinter.Button(input_page, text="Clear", font=("Algerian", 14), command=clear_input).grid(row=4, column=1, padx=20, pady=10, sticky="w")
tkinter.Button(input_page, text="View Files", font=("Algerian", 14), command=view_files).grid(row=4, column=2, padx=20, pady=10, sticky="w")

# Show the initial login page
show_frame(login_page)

# Run the application
window.mainloop()