import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sqlite3
import socket
import platform
from datetime import datetime
import re
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from helpers.settings import *
# import session
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def create_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            salt TEXT,
            pc_name TEXT,
            os TEXT,
            last_login DATETIME,
            reset_token TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest(), salt

def verify_password(stored_password, stored_salt, provided_password):
    return stored_password == hashlib.sha256((provided_password + stored_salt).encode()).hexdigest()

def register_user(username, email, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    pc_name = socket.gethostname()
    os_name = platform.system() + " " + platform.release()
    hashed_password, salt = hash_password(password)
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, salt, pc_name, os, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, hashed_password, salt, pc_name, os_name, datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user and verify_password(user[3], user[4], password):
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user[0]))
        conn.commit()
        conn.close()
        return user
    conn.close()
    return None

def send_reset_email(email, token):
    # Configure this with your email settings
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = "Password Reset"

    body = f"Use this token to reset your password: {token}"
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)

def generate_reset_token(email):
    token = secrets.token_hex(16)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET reset_token = ? WHERE email = ?', (token, email))
    conn.commit()
    conn.close()
    return token



class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.username = ctk.StringVar()
        self.password = ctk.StringVar()

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Login", font=("Roboto", 24)).grid(row=0, column=0, pady=20)
        ctk.CTkLabel(self, text="Username").grid(row=1, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.username).grid(row=2, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(self, text="Password").grid(row=3, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.password, show="*").grid(row=4, column=0, pady=5, padx=20, sticky="ew")

        ctk.CTkButton(self, text="Login", command=self.login).grid(row=5, column=0, pady=10)
        ctk.CTkButton(self, text="Create Account", command=lambda: parent.show_frame(RegisterFrame)).grid(row=6, column=0, pady=10)
        ctk.CTkButton(self, text="Forgot Password", command=lambda: parent.show_frame(ForgotPasswordFrame)).grid(row=7, column=0, pady=10)

    def login(self):
        user = login_user(self.username.get(), self.password.get())
        if user:
            CTkMessagebox(title="Success", message="Login successful!", icon="check")
            self.master.frames[DashboardFrame].load_user_data(user)
            self.master.show_frame(DashboardFrame)
        else:
            CTkMessagebox(title="Error", message="Invalid credentials.", icon="cancel")

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.username = ctk.StringVar()
        self.email = ctk.StringVar()
        self.confirm_email = ctk.StringVar()
        self.password = ctk.StringVar()
        self.confirm_password = ctk.StringVar()

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Register", font=("Roboto", 24)).grid(row=0, column=0, pady=20)
        ctk.CTkLabel(self, text="Username").grid(row=1, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.username).grid(row=2, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(self, text="Email").grid(row=3, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.email).grid(row=4, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(self, text="Confirm Email").grid(row=5, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.confirm_email).grid(row=6, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(self, text="Password").grid(row=7, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.password, show="*").grid(row=8, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(self, text="Confirm Password").grid(row=9, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.confirm_password, show="*").grid(row=10, column=0, pady=5, padx=20, sticky="ew")

        ctk.CTkButton(self, text="Register", command=self.register).grid(row=11, column=0, pady=10)
        ctk.CTkButton(self, text="Back to Login", command=lambda: parent.show_frame(LoginFrame)).grid(row=12, column=0, pady=10)

    def register(self):
        if not self.validate_input():
            return
        if register_user(self.username.get(), self.email.get(), self.password.get()):
            CTkMessagebox(title="Success", message="Account created successfully!", icon="check")
            self.master.show_frame(LoginFrame)
        else:
            CTkMessagebox(title="Error", message="Username or email already exists.", icon="cancel")

    def validate_input(self):
        if self.email.get() != self.confirm_email.get():
            CTkMessagebox(title="Error", message="Emails do not match.", icon="cancel")
            return False
        if self.password.get() != self.confirm_password.get():
            CTkMessagebox(title="Error", message="Passwords do not match.", icon="cancel")
            return False
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email.get()):
            CTkMessagebox(title="Error", message="Invalid email format.", icon="cancel")
            return False
        if len(self.password.get()) < 8:
            CTkMessagebox(title="Error", message="Password must be at least 8 characters long.", icon="cancel")
            return False
        return True

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)

        self.username_label = ctk.CTkLabel(self, text="", font=("Roboto", 18))
        self.username_label.grid(row=0, column=0, pady=20)
        self.email_label = ctk.CTkLabel(self, text="")
        self.email_label.grid(row=1, column=0, pady=5)
        self.pc_name_label = ctk.CTkLabel(self, text="")
        self.pc_name_label.grid(row=2, column=0, pady=5)
        self.os_label = ctk.CTkLabel(self, text="")
        self.os_label.grid(row=3, column=0, pady=5)
        self.last_login_label = ctk.CTkLabel(self, text="")
        self.last_login_label.grid(row=4, column=0, pady=5)

        ctk.CTkButton(self, text="Change Password", command=self.change_password).grid(row=5, column=0, pady=10)
        ctk.CTkButton(self, text="Logout", command=self.logout).grid(row=6, column=0, pady=10)

    def load_user_data(self, user):
        self.username_label.configure(text=f"Welcome, {user[1]}!")
        self.email_label.configure(text=f"Email: {user[2]}")
        self.pc_name_label.configure(text=f"PC Name: {user[5]}")
        self.os_label.configure(text=f"OS: {user[6]}")
        self.last_login_label.configure(text=f"Last Login: {user[7]}")

    def change_password(self):
        # Implement password change functionality
        CTkMessagebox(title="Info", message="Password change feature coming soon!", icon="info")

    def logout(self):
        self.master.show_frame(LoginFrame)

class ForgotPasswordFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.email = ctk.StringVar()

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Forgot Password", font=("Roboto", 24)).grid(row=0, column=0, pady=20)
        ctk.CTkLabel(self, text="Email").grid(row=1, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.email).grid(row=2, column=0, pady=5, padx=20, sticky="ew")

        ctk.CTkButton(self, text="Send Reset Link", command=self.send_reset_link).grid(row=3, column=0, pady=10)
        ctk.CTkButton(self, text="Back to Login", command=lambda: parent.show_frame(LoginFrame)).grid(row=4, column=0, pady=10)

    def send_reset_link(self):
        email = self.email.get()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            CTkMessagebox(title="Error", message="Invalid email format.", icon="cancel")
            return

        token = generate_reset_token(email)
        try:
            send_reset_email(email, token)
            CTkMessagebox(title="Success", message="Password reset link sent to your email.", icon="check")
            self.master.show_frame(LoginFrame)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to send reset email: {str(e)}", icon="cancel")

class ResetPasswordFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.token = ctk.StringVar()
        self.new_password = ctk.StringVar()
        self.confirm_password = ctk.StringVar()

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Reset Password", font=("Roboto", 24)).grid(row=0, column=0, pady=20)
        ctk.CTkLabel(self, text="Reset Token").grid(row=1, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.token).grid(row=2, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(self, text="New Password").grid(row=3, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.new_password, show="*").grid(row=4, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(self, text="Confirm New Password").grid(row=5, column=0, pady=5)
        ctk.CTkEntry(self, textvariable=self.confirm_password, show="*").grid(row=6, column=0, pady=5, padx=20, sticky="ew")

        ctk.CTkButton(self, text="Reset Password", command=self.reset_password).grid(row=7, column=0, pady=10)
        ctk.CTkButton(self, text="Back to Login", command=lambda: parent.show_frame(LoginFrame)).grid(row=8, column=0, pady=10)

    def reset_password(self):
        if self.new_password.get() != self.confirm_password.get():
            CTkMessagebox(title="Error", message="Passwords do not match.", icon="cancel")
            return

        if len(self.new_password.get()) < 8:
            CTkMessagebox(title="Error", message="Password must be at least 8 characters long.", icon="cancel")
            return

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE reset_token = ?', (self.token.get(),))
        user = cursor.fetchone()

        if user:
            hashed_password, salt = hash_password(self.new_password.get())
            cursor.execute('UPDATE users SET password = ?, salt = ?, reset_token = NULL WHERE id = ?', (hashed_password, salt, user[0]))
            conn.commit()
            CTkMessagebox(title="Success", message="Password has been reset successfully!", icon="check")
            self.master.show_frame(LoginFrame)
        else:
            CTkMessagebox(title="Error", message="Invalid reset token.", icon="cancel")

        conn.close()

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{app_name}: Account Management")
        self.geometry("960x640")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, RegisterFrame, DashboardFrame, ForgotPasswordFrame, ResetPasswordFrame):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Check if user is already logged in
        if self.is_user_logged_in():
            self.show_frame(DashboardFrame)  # Go directly to the dashboard
        else:
            self.show_frame(LoginFrame)



    # def is_user_logged_in(self):
    #     return session.get('user_id') is not None
    #     def show_frame(self, cont):
    #         frame = self.frames[cont]
    #         frame.tkraise()

if __name__ == "__main__":
    create_db()
    app = LoginApp()
    app.mainloop()
