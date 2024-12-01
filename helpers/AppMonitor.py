import os
import time
import json
from helpers.settings import *
from datetime import datetime, timedelta
from PIL import ImageGrab
import psutil
import pygetwindow as gw
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from tkinter import Tk, ttk, messagebox
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import threading
import sqlite3
import requests
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from helpers.ActivityClassifier import ActivityClassifier
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from helpers.summary_log import automation_log

class AppMonitor:
    def __init__(self):
        self.load_config()

        self.active_window = None
        self.active_window_raw = None
        self.window_start_time = None
        self.time_spent = {}
        self.last_screenshot_time = time.time()
        self.classifier = ActivityClassifier()
        self.create_database()
        self.running = False
        self.streak = 0
        self.last_productive_day = None
        self.alert_thread = None
        if not os.path.exists(SCREENSHOT_DIR):
            os.makedirs(SCREENSHOT_DIR)

    def load_config(self):
        try:
            with open('helpers/sources/config.json', 'r') as f:
                config = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            config = {
                "screenshot_interval": 60,
                "focus_mode": True,
                "productivity_goal": 240,
                "break_reminder": 60,
                "database_file": "helpers/sources/activity_log.db",
                "screenshot_dir": "screenshots",
                "export_file": "helpers/sources/activity_log.csv",
                "training_data_file": "helpers/sources/activity_training_data.csv",
                "trash_file": "helpers/sources/Trash_log.csv",
                "pomodoro_work": 25,
                "pomodoro_break": 5
            }

            # Create the config file if it doesn't exist and write the default config to it
            with open('helpers/helpers/sources/config.json', 'w') as f:
                json.dump(config, f, indent=4)

        self.screenshot_interval = config.get("screenshot_interval", 60)
        self.focus_mode = config.get("focus_mode", True)
        self.productivity_goal = config.get("productivity_goal", 240)  # in minutes
        self.break_reminder = config.get("break_reminder", 45)  # in minutes
        self.pomodoro_work = config.get("pomodoro_work", 25)  # in minutes
        self.pomodoro_break = config.get("pomodoro_break", 5)  # in minutes
        self.database_file = config.get("database_file", "helpers/sources/activity_log.db")
        self.screenshot_dir = config.get("screenshot_dir", "screenshots")
        self.export_file = config.get("export_file", "helpers/sources/activity_log.csv")
        self.training_data_file = config.get("training_data_file", "helpers/sources/activity_training_data.csv")
        self.trash_file = config.get("trash_file", "helpers/sources/Trash_log.csv")
    def get_today_folder(self):

        today = datetime.now().strftime("%Y-%m-%d")
        folder_path = os.path.join(SCREENSHOT_DIR, today)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def create_database(self):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                window_title TEXT,
                duration INTEGER,
                classification TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log_raw (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                window_title TEXT,
                duration INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def take_screenshot(self):
        current_time = time.time()
        if current_time - self.last_screenshot_time >= self.screenshot_interval:
            screenshot = ImageGrab.grab()
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            folder_path = self.get_today_folder()
            file_path = os.path.join(folder_path, f"screenshot_{timestamp}.png")
            screenshot.save(file_path)
            self.last_screenshot_time = current_time

    def get_active_window(self):
        window = gw.getActiveWindow()
        return window.title if window else "No active window"

    def update_time_spent(self):
        new_window_raw = self.get_active_window()
        new_window = self.classifier.preprocess_window_title(new_window_raw)
        current_time = time.time()

        if new_window != self.active_window and new_window != "Ignored" and new_window != default_app:
            if self.active_window:
                time_in_window = current_time - self.window_start_time
                self.time_spent[self.active_window] = self.time_spent.get(self.active_window, 0) + time_in_window
                self.log_activity(self.active_window, time_in_window, self.active_window_raw)

            # Stop the previous alert thread if it exists
            if self.alert_thread and self.alert_thread.is_alive():
                self.alert_thread.stop()

            self.active_window = new_window
            self.active_window_raw = new_window_raw
            self.window_start_time = current_time

            # print(f"Active window: {self.active_window} , time spent: {self.time_spent[self.active_window]}")
            # Start a new alert thread for the new window
            self.alert_thread = AlertThread(self, self.active_window)
            self.alert_thread.start()


    def on_window_poisoned(self, window_title, time_in_window):
        print(f"Window {window_title} has been poisoned for {time_in_window} seconds.")
        if 0 < time_in_window <= 5:
            print("First Alert: Please close this window!")
            self.first_alert(window_title)
        elif 5 < time_in_window <= 10:
            print("Second Alert: Closing apps soon if this window remains open!")
            self.second_alert(window_title)
        elif 10 < time_in_window <= 15:
            print("Closing poisoned window!")
            self.close_apps(window_title)
        elif 15 < time_in_window <= 20:
            print("Freezing PC!")
            self.freeze_or_password(window_title)
        else:
            print("Final Countdown!")
            self.final_countdown(window_title)


    def first_alert(self , window_title):
        messagebox.showinfo("Alert", f"First Alert: Please close this window! {window_title}")
        # self.show_notification("Alert", "First Alert: Please close this window!")
    def second_alert(self , window_title):
        messagebox.showinfo("Alert", f"Second Alert: Closing apps soon if this window remains open! {window_title}")

    def close_apps(self , window_title):
        messagebox.showinfo("Alert", "Closing poisoned window!")
        window_title = self.get_active_window_title()
        # List of apps to close (customize as needed)
        apps_to_close = ['chrome.exe', 'firefox.exe', 'vlc.exe']  # Add more apps here

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in apps_to_close:
                    proc.terminate()  # Terminate the app
                    print(f"Closed {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    def freeze_or_password(self , window_title):
        thread = threading.Thread(target=self.freeze_pc, args=(self.active_window))
        thread.start()
        # self.freeze_pc()
        if messagebox.askyesno("Security", "Do you want to enter the parental password?"):
            self.ask_password()

    def final_countdown(self, window_title):
        for i in range(10, 0, -1):
            if messagebox.askyesno("Alert", f"Please close this window in {i} seconds"):
                self.close_apps(window_title)
                return
            time.sleep(1)
        self.shut_down_pc()

    def ask_password(self):
        password_window = ctk.CTkToplevel(self.root)
        password_window.title("Enter Password")

        ctk.CTkLabel(password_window, text="Parental Password:").pack(pady=10)
        password_entry = ctk.CTkEntry(password_window, show="*")
        password_entry.pack(pady=10)

        def check_password():
            if password_entry.get() == "parent123":  # Example password
                ctk.messagebox.show_info("Access Granted", "Correct password!")
                password_window.destroy()
            else:
                ctk.messagebox.show_error("Access Denied", "Incorrect password!")

        submit_button = ctk.CTkButton(password_window, text="Submit", command=check_password)
        submit_button.pack(pady=10)

    def freeze_pc(self , window_title):
        messagebox.showinfo("Freeze", "PC will freeze for 10 minutes!")
        self.root.after(1000, self.execute_freeze)

    def execute_freeze(self , window_title):
        if os.name == 'nt':  # Windows
            print("Windows")
            os.system('rundll32.exe user32.dll,LockWorkStation')  # Lock the PC
        elif os.name == 'posix':  # Linux/Mac
            print("Linux/Mac")
            os.system('gnome-screensaver-command -l')  # Lock PC (Linux)
        time.sleep(600)  # 10 minutes freeze
    def shut_down_pc(self):
        messagebox.showinfo("Shutdown", "PC will shut down in 10 seconds!")
        if os.name == 'nt':  # Windows
            os.system('shutdown /s /t 10')
        elif os.name == 'posix':  # Linux/Mac
            os.system('shutdown -h +0.1')
    def get_productive_time(self):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Get the start of the current day
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Query the database for productive activities today
        cursor.execute('''
            SELECT SUM(duration)
            FROM activity_log
            WHERE classification = "Productive"
            AND datetime(timestamp) >= ?
        ''', (today,))

        result = cursor.fetchone()[0]

        conn.close()

        # Return the total productive time in seconds, or 0 if no productive time was logged
        return result if result is not None else 0

    def log_activity(self, window_title, duration , raw_window_title):
        classification = self.classifier.classify_activity(window_title)
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        if  self.classifier.is_relevant_activity(window_title):
            cursor.execute('''
                INSERT INTO activity_log (timestamp, window_title, duration, classification)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now(), window_title, duration, classification))
            cursor.execute('''
                INSERT INTO activity_log_raw (timestamp, window_title)
                VALUES (?, ?)
            ''', (datetime.now(), raw_window_title,))
            conn.commit()
        conn.close()

    def focus_mode_run(self):
        self.focus_mode = True
        while self.focus_mode:
            current_window = self.get_active_window()
            current_window = self.classifier.preprocess_window_title(current_window)
            if self.focus_mode and self.classifier.classify_activity(current_window) == "Unproductive":
                return True
            return False


    def check_productivity_goal(self):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        today = datetime.now().date()
        cursor.execute('''
            SELECT SUM(duration) FROM activity_log
            WHERE date(timestamp) = ? AND classification = 'Productive'
        ''', (today,))
        productive_time = cursor.fetchone()[0] or 0
        conn.close()

        if productive_time >= self.productivity_goal * 60:
            self.update_streak()
            return "Congratulations! You've reached your productivity goal for today."
        return None

    def update_streak(self):
        today = datetime.now().date()
        if self.last_productive_day == today - timedelta(days=1):
            self.streak += 1
        elif self.last_productive_day != today:
            self.streak = 1
        self.last_productive_day = today

    def remind_break(self):
        return "It's time to take a short break. Stand up, stretch, or take a quick walk!"


    def generate_daily_summary(self , selected = [1,1,1,1,1,1,1,1]):
        conn = sqlite3.connect(DATABASE_FILE)
        df = pd.read_sql_query('''
            SELECT window_title, SUM(duration) as total_time, classification, strftime('%H', timestamp) as hour
            FROM activity_log
            WHERE date(timestamp) = date('now')
            GROUP BY window_title, classification, strftime('%H', timestamp)
        ''', conn)
        conn.close()

        def format_time(seconds):
                if seconds >= 3600:
                    return f"{seconds / 3600:.1f} h"
                elif seconds >= 60:
                    return f"{seconds / 60:.1f} m"
                else:
                    return f"{seconds:.0f} s"


        # Create the folder for charts if it doesn't exist
        folder_path = os.path.join(self.get_today_folder(), "charts")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Set a modern style for all plots
        plt.style.use('seaborn-whitegrid')
        colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff99cc"]

        # Helper function for adding value labels with formatting
        def add_value_labels(ax, spacing=5):

            for rect in ax.patches:
                value = rect.get_width()
                formatted_value = format_time(value)
                text = f'{formatted_value}'

                if int(rect.get_height()) != 0:
                    y = rect.get_y() + rect.get_height() / 2
                else:
                    y = rect.get_y() + rect.get_height()
                x = rect.get_x() + rect.get_width()
                ax.text(x, y, text, ha='left', va='center', fontsize=10)

        if selected[0] == 1 :
            # 1. Horizontal Bar Plot (Modernized)
            plt.figure(figsize=(12, 8))
            ax = sns.barplot(x='total_time', y='window_title', hue='classification', data=df, orient='h', palette=colors)
            plt.title("Time Spent on Apps Today", fontsize=16, fontweight='bold')
            plt.xlabel("Time", fontsize=12)
            plt.ylabel("Application", fontsize=12)
            ax.legend(title="Classification", title_fontsize='12', fontsize='10', bbox_to_anchor=(1.05, 1), loc='upper left')
            # add_value_labels(ax)
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_horizontal_bar.png"), dpi=300, bbox_inches='tight')
            plt.close()

        if selected[1] == 1 :
            # Vertical Bar Plot (Modernized)
            plt.figure(figsize=(14, 8))
            ax = sns.barplot(x='window_title', y='total_time', hue='classification', data=df, palette=colors)
            plt.title("Time Spent on Apps Today", fontsize=16, fontweight='bold')
            plt.xlabel("Application", fontsize=12)
            plt.ylabel("Time", fontsize=12)
            plt.xticks(rotation=45, ha='right')
            ax.legend(title="Classification", title_fontsize='12', fontsize='10', bbox_to_anchor=(1.05, 1), loc='upper left')
            for i in ax.containers:
                ax.bar_label(i, labels=[format_time(v) for v in i.datavalues])
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_vertical_bar.png"), dpi=300, bbox_inches='tight')
            plt.close()

        if selected[2] == 1 :
            # Pie Chart (Modernized)
            plt.figure(figsize=(10, 10))
            df_total = df.groupby('classification')['total_time'].sum().reset_index()
            plt.pie(df_total['total_time'], labels=df_total['classification'], autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops=dict(width=0.6))
            plt.title("Time Spent by Classification", fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_donut.png"), dpi=300, bbox_inches='tight')
            plt.close()

        if selected[3] == 1 :
            # Stacked Area Chart
            plt.figure(figsize=(12, 6))
            df_pivot = df.pivot_table(values='total_time', index='hour', columns='classification', fill_value=0)
            df_pivot = df_pivot.reindex(np.arange(24).astype(str))
            df_pivot.plot.area(stacked=True, color=colors)
            plt.title("Time Spent on Apps Throughout the Day", fontsize=16, fontweight='bold')
            plt.xlabel("Hour of Day", fontsize=12)
            plt.ylabel("Time", fontsize=12)
            plt.legend(title="Classification", title_fontsize='12', fontsize='10')
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_stacked_area.png"), dpi=300, bbox_inches='tight')
            plt.close()

        if selected[4] == 1 :
            # Line Plot
            plt.figure(figsize=(12, 6))
            sns.lineplot(x='window_title', y='total_time', hue='classification', data=df, marker='o')
            plt.title("Time Spent on Apps Today - Line Plot")
            plt.xlabel("Application")
            plt.ylabel("Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_line.png"))
            plt.close()

        if selected[5] == 1 :
        # Heatmap
            plt.figure(figsize=(10, 8))
            heatmap_data = df.pivot_table(values='total_time', index='window_title', columns='classification', fill_value=0)
            sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt=".1f")
            plt.title("Time Spent on Apps Today - Heatmap")
            plt.xlabel("Classification")
            plt.ylabel("Application")
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_heatmap.png"))
            plt.close()

        if selected[6] == 1 :
        # Calendar Heatmap (Modernized)
            df_heatmap = df.pivot_table(values='total_time', index='window_title', columns='hour', fill_value=0)
            df_heatmap = df_heatmap.reindex(np.arange(24).astype(str), axis=1, fill_value=0)

            plt.figure(figsize=(16, 10))
            custom_cmap = LinearSegmentedColormap.from_list("", ["#f7fbff", "#08306b"])
            ax = sns.heatmap(df_heatmap, cmap=custom_cmap, annot=True, fmt=".0f", cbar_kws={'label': 'Time'})
            plt.title("App Usage Throughout the Day", fontsize=16, fontweight='bold')
            plt.xlabel("Hour of Day", fontsize=12)
            plt.ylabel("Application", fontsize=12)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_calendar_heatmap.png"), dpi=300, bbox_inches='tight')
            plt.close()

        if selected[7] == 1 :
            # Grouped Bar Chart (New addition for comparison)
            plt.figure(figsize=(14, 8))
            df_grouped = df.groupby(['classification', 'window_title'])['total_time'].sum().unstack()
            ax = df_grouped.plot(kind='bar', stacked=False, figsize=(14, 8), width=0.8, color=colors)
            plt.title("Time Spent on Apps by Classification", fontsize=16, fontweight='bold')
            plt.xlabel("Classification", fontsize=12)
            plt.ylabel("Time", fontsize=12)
            plt.legend(title="Application", title_fontsize='12', fontsize='10', bbox_to_anchor=(1.05, 1), loc='upper left')
            for container in ax.containers:
                formated_time = [format_time(v) for v in container.datavalues]
                if any(not s.endswith("secs") for s in formated_time):
                    ax.bar_label(container, label_type='center', labels=formated_time)
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, "daily_summary_grouped_bar.png"), dpi=300, bbox_inches='tight')
            plt.close()

    def export_activity_log(self, filename=None ,  filename_raw=None  , filename_all = None):
        if not filename:
            today = datetime.now().strftime("%Y-%m-%d")
            filename = os.path.join(self.get_today_folder(), f"activity_log_{today}.csv")
        conn = sqlite3.connect(DATABASE_FILE)
        df = pd.read_sql_query("SELECT * FROM activity_log WHERE date(timestamp) = date('now')", conn)
        df_raw = pd.read_sql_query("SELECT * FROM activity_log_raw", conn)
        df_all = pd.read_sql_query("SELECT * FROM activity_log", conn)
        conn.close()
        df.to_csv(filename, index=False)
        df_raw.to_csv(filename_raw, index=False)
        df_all.to_csv(filename_all, index=False)
        automation_log()

    def run(self):
        self.running = True
        while self.running:
            self.take_screenshot()
            self.update_time_spent()
            time.sleep(1)

    def stop(self):
        self.running = False



class AlertThread(threading.Thread):
    def __init__(self, app_monitor, window_title ):
        threading.Thread.__init__(self)
        self.app_monitor = app_monitor
        self.window_title = window_title
        self.start_time = time.time()
        self.time_spent = app_monitor.time_spent
        self.running = True

    def run(self):
        while self.running:
            if self.window_title in self.time_spent.keys():
                time_in_window = time.time() - self.start_time + self.time_spent[self.window_title]

            else:
                time_in_window = time.time() - self.start_time
            if self.app_monitor.classifier.classify_activity(self.window_title) == "Poisoned":
                self.app_monitor.on_window_poisoned(self.window_title, time_in_window)
            time.sleep(1)  # Check every second

        print(f"Window {self.window_title} has been poisoned for {self.time_spent} seconds.")

    def stop(self):
        self.running = False
