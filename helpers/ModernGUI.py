import winsound
from tkinter import PhotoImage
import tkinter as tk
import customtkinter as ctk
import random as rd
from tkinter import messagebox, simpledialog, filedialog, ttk
import threading
import os
import pandas as pd
from PIL import Image, ImageTk
from datetime import datetime
import time
import sqlite3
from CTkListbox import *
from helpers.ActivityClassifier import ActivityClassifier
import csv
from helpers.settings import *
from plyer import notification
import matplotlib
from helpers import summary_log as summary
from helpers.LegoFunction import AppAutomation, AppEvent  # Assuming previous code is saved as automation_system.py
from CTkMessagebox import CTkMessagebox
matplotlib.use('Agg')  # Use non-GUI backend for plotting
import json
from pathlib import Path
# from lucide_icons import icons
class ModernGUI(ctk.CTk):
    def __init__(self, monitor):
        super().__init__()
        self.title(app_name)
        self.geometry("960x640")
        self.isStart = False
        self.config = monitor.load_config()
        self.monitor = monitor
        self.automation = AppAutomation()
        self.window_classifications = {}
        self.window_listbox = None  # Initialize window_listbox as None
        self.search_var = None  # To store the search term
        self.Cl_search_var = None  # To store the search term
        # Set modern appearance
        self.theme = "dark"
        ctk.set_appearance_mode(self.theme)
        ctk.set_default_color_theme("blue")
        self.classifier = ActivityClassifier()
        self.previous_app = None
        # Initialize main UI
        self.create_widgets()
        self.text = {}
        self.svgs = {}
        # self.palette = pallete_theme
        # Initialize threads
        self.monitor_thread = None
        self.update_ui_thread = None
        #files
        self.archive_file = "helpers/sources/Trash_log.csv"
        self.archive_active = False
        # Pomodoro variables
        self.pomodoro_active = False
        self.pomodoro_paused = False
        self.pomodoro_time = 25 * 60  # 25 minutes in seconds
        self.break_time = 5 * 60  # 5 minutes in seconds
        self.pomodoro_counter = 0
        self.break_counter = 0
        self.long_break_interval = 3  # Long break after every 4 pomodoros
        self.long_break_time = 15 * 60  # 15 minutes in seconds
        self.auto_start_breaks = True
        self.auto_start_pomodoros = False
        self.paused = False
        # You can adjust these to your desired Pomodoro and break durations
        self.break_duration = 300  # 5 minutes by default
        self.auto_break = True  # Auto-start break after Pomodoro

        #optomazite performance
        self.last_ui_update = time.time()
        self.update_interval = 5  # Update UI every 5 seconds
        self.cached_screenshots = {}
        self.cached_log_data = None
        self.last_log_update = None

        #side_bar
        self.sidebar_open = True
        self.sidebar_width = 230
        self.sidebar_width_collapsed = 50
        self.sidebar_open = True

        #notifications
        self.sent_notifications = set()

        #User acount
        self.islogin = False
        self.isregister = False
    #WORKING HERE
    def toggle_sidebar(self):
        if self.sidebar_open:
            new_width = self.sidebar_width_collapsed
            self.toggle_button.configure(image=self.get_icon("sm-arrow-right", size=0.03))
            for btn in self.sidebar_buttons:
                btn.configure(text="", width=40, height=50)  # Hide text but keep the button's icon visible
            # self.logo_label.pack_forget()  # Hide the logo
        else:
            new_width = self.sidebar_width
            self.toggle_button.configure(image=self.get_icon("sm-arrow-left", size=0.03))
            for btn, (text, _, _) in zip(self.sidebar_buttons, self.buttons_info):
                btn.configure(text=text, width=200, height=50)  # Show text and set button back to full size
            # self.logo_label.pack(pady=(30, 20))  # Show the logo when expanded

        self.sidebar_open = not self.sidebar_open
        self.animate_sidebar(new_width)



    def create_widgets(self):


        # Create main content area
        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Main content area with Notebook (tabs)
        self.notebook = ctk.CTkTabview(self.main_content)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Adding tabs
        self.create_dashboard_tab()
        self.create_User_tab()
        self.create_classify_activity_tab()
        self.create_Legos_tab()
        self.create_log_tab()
        self.create_settings_tab()


        # Create sidebar
        self.sidebar_width = 220
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)  # Prevent the sidebar from shrinking

        # Sidebar toggle button (position it at the top)
        self.toggle_button = ctk.CTkButton(
            self.sidebar,
            image=self.get_icon("sm-arrow-left", size=0.03),
            text="",
            command=self.toggle_sidebar,
            width=30,
            height=30,
            fg_color="transparent",
            hover_color= Hover_color_dark
        )
        self.toggle_button.pack(pady=(10, 20), anchor="ne")  # Fixed position at the top with some padding

        # Sidebar logo or title (position below the toggle button)
        # self.logo_label = ctk.CTkLabel(self.sidebar, text="PC Monitor", font=ctk.CTkFont(size=24, weight="bold"))
        # self.logo_label.pack(pady=(10, 20))  # Adjust the padding as needed

        # Create sidebar buttons (below the logo)
        self.create_sidebar_buttons()
    def create_sidebar_buttons(self):
        self.buttons_info = [
            ("Start Monitoring", "chart2", self.toggle_monitoring),
            ("Start Pomodoro", "play", self.toggle_pomodoro),
            ("Export Activity Log", "save", self.export_activity_log),
            ("Generate Summary", "chart", self.generate_daily_summary),
        ]

        self.sidebar_buttons = []  # Clear previous buttons
        for text, icon_name, command in self.buttons_info:
            btn = ctk.CTkButton(
                self.sidebar,
                image=self.get_icon(icon_name),
                text=text,
                compound="left",  # Icon and text together when expanded
                command=command,
                anchor="w",
                fg_color="transparent",
                hover_color= Hover_color_dark,
                height=50,
                width=200  # Full width for expanded sidebar
            )
            btn.tkraise()  # Ensure the button stays on top

            btn.pack(pady=10, padx=20, fill="x", anchor="w")  # Padding to ensure spacing
            self.sidebar_buttons.append(btn)



    def update_button_states(self):
        for btn, (text, icon_name, _) in zip(self.sidebar_buttons, self.buttons_info):
            if self.sidebar_open:
                btn.configure(image=self.get_icon(icon_name), text=text, compound="left")
            else:
                btn.configure(image=self.get_icon(icon_name), text="", compound="left")

    def toggle_monitoring(self):
        if not self.isStart:
            self.start_monitoring()
            self.sidebar.winfo_children()[1].configure(text="Stop Monitoring" if self.sidebar_open else "")
        else:
            self.stop_monitoring()
            self.sidebar.winfo_children()[1].configure(text="Start Monitoring" if self.sidebar_open else "")

    def refresher(self):
        #refresh the data (training) and cleaning duplicates
        self.monitor.classifier.train_classifier()
        self.monitor.classifier.clean_duplicates_inplace()
        # self.monitor.classifier.save_classifier()
        # print(self.classifier.trash_file)
        # print(self.monitor.classifier.productivity_goal)

    def start_monitoring(self):
        self.isStart = True
        self.monitor_thread = threading.Thread(target=self.monitor.run)
        self.monitor_thread.start()
        self.update_ui_thread = threading.Thread(target=self.update_ui)
        self.update_ui_thread.start()

    def stop_monitoring(self):
        self.isStart = False
        self.monitor.stop()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join()
        if self.update_ui_thread and self.update_ui_thread.is_alive():
            self.update_ui_thread.join()

    def create_classify_activity_tab(self):

        self.notebook.add("Classify Activity")

        # Get the created Dashboard tab and place elements in it
        page = self.notebook.tab("Classify Activity")
        # Create search bar
        self.Cl_search_var = tk.StringVar()

        search_entry = ctk.CTkEntry(page, textvariable=self.Cl_search_var, placeholder_text="Search windows")
        search_entry.pack(pady=10, padx=20, fill="x")

        search_button = ctk.CTkButton(page, text="Search", command=self.filter_listbox)
        search_button.pack(pady=10, padx=20, fill="x")

        windows = self.monitor.classifier.export_window_titles_to_array(self.monitor.classifier.data_file).keys()
        self.window_classifications = {window: self.monitor.classifier.classify_activity(window) for window in windows}
        # self.window_listbox = CTkListbox(page, width=50, height=20)

        # Create Listbox and populate it
        self.window_listbox = tk.Listbox(page, width=50, height=20)
        self.populate_listbox(self.window_classifications)


        self.window_listbox.pack(pady=10, padx=20, fill="both", expand=True)
        #add new windows button

        # Create a frame to hold the buttons
        button_frame = ctk.CTkFrame(page, fg_color="transparent")
        button_frame.pack(pady=10, anchor="center")  # Center the frame on the page

        # Add buttons to the frame
        self.new_button = ctk.CTkButton(button_frame, text="", image=self.get_icon("add"), fg_color="transparent", width=35, command=self.add_custom_classification , hover_color=Hover_color_dark)
        self.new_button.pack(side="left", padx=5)

        self.edit_button = ctk.CTkButton(button_frame, text="", image=self.get_icon("edit"), fg_color="transparent", width=35, command=self.edit_classification , hover_color=Hover_color_dark)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(button_frame, text="", image=self.get_icon("delete"), fg_color="transparent", width=35, command=self.delete_classification , hover_color=Hover_color_dark)
        self.delete_button.pack(side="left", padx=5)

        self.archive_button = ctk.CTkButton(button_frame, text="", image=self.get_icon("archive"), fg_color="transparent", width=35, command=self.show_archived_classifactions , hover_color=Hover_color_dark)
        self.archive_button.pack(side="left", padx=5)


    def populate_listbox(self, classifications):
        """Helper function to populate the Listbox with window titles and classifications."""
        self.window_listbox.delete(0, tk.END)  # Clear the Listbox

        for window, classification in classifications.items():
            self.window_listbox.insert("end", f"{window}, {classification}")

    def filter_listbox(self):
        """Filters the Listbox based on the search term."""
        search_term = self.Cl_search_var.get().lower()

        filtered_classifications = {window: classification for window, classification in self.window_classifications.items() if search_term in window.lower()}

        self.populate_listbox(filtered_classifications)

    def edit_classification(self):
        selected = self.window_listbox.curselection()
        if selected:
            window = self.window_listbox.get(selected).split(",")[0].strip()

            # Create the classification window
            classification_window = ctk.CTkToplevel(self)
            classification_window.title("Select Classification")
            classification_window.geometry("400x200")
            classification_window.resizable(False, False)

            # Center the classification window on the screen
            classification_window.update_idletasks()
            window_width = classification_window.winfo_width()
            window_height = classification_window.winfo_height()
            screen_width = classification_window.winfo_screenwidth()
            screen_height = classification_window.winfo_screenheight()
            position_top = int(screen_height / 2 - window_height / 2)
            position_right = int(screen_width / 2 - window_width / 2)
            classification_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

            # Block interaction with the main window until classification is confirmed or closed
            classification_window.grab_set()

            # Create a label for instruction
            label = ctk.CTkLabel(classification_window, text="Select the classification:")
            label.pack(pady=10)

            # Create a combobox with the classification options
            classifications = self.classifier.get_classifications()
            combobox = ctk.CTkComboBox(classification_window, values=classifications)
            combobox.pack(pady=10)

            # Entry for new classification
            new_classification_var = ctk.StringVar()
            new_classification_entry = ctk.CTkEntry(classification_window, textvariable=new_classification_var, placeholder_text="New Classification")
            new_classification_entry.pack(pady=10)

            # Function to confirm selection
            def confirm_selection():
                classification = combobox.get() or new_classification_var.get()
                if classification:
                    # Update the classification data
                    self.window_classifications[window] = classification
                    self.window_listbox.delete(selected)
                    self.window_listbox.insert(selected, f"{window}: {classification}")
                    # Update the classifier and clean duplicates
                    self.monitor.classifier.add_custom_classification(window, classification)
                    self.monitor.classifier.clean_duplicates_inplace()
                # Close the classification window after confirming
                classification_window.destroy()

            # Button to confirm selection
            button = ctk.CTkButton(classification_window, text="Confirm", command=confirm_selection)
            button.pack(pady=10)

            # Centering and setting focus on the dialog
            classification_window.transient(self)
            classification_window.grab_set()
            classification_window.focus_set()

    def delete_classification(self):
        selected = self.window_listbox.curselection()
        if selected:
            window = self.window_listbox.get(selected)
            window, classification = window.rsplit(",", 1)  # Split the string by the last comma
            classification = classification.strip()  # Remove any extra whitespace
            self.monitor.classifier.add_custom_classification(window, classification, self.archive_file )
            self.monitor.classifier.delete_windows(window )
            self.window_listbox.delete(selected)

    def restored_archived(self):
        selected = self.window_listbox.curselection()
        if selected:
            window = self.window_listbox.get(selected)
            window, classification = window.rsplit(",", 1)  # Split the string by the last comma
            classification = classification.strip()  # Remove any extra whitespace
            self.monitor.classifier.add_custom_classification(window, classification)
            self.monitor.classifier.delete_windows(window , self.archive_file)
            self.window_listbox.delete(selected)
        pass
    def delete_archive(self):
        selected = self.window_listbox.curselection()
        if selected:
            window = self.window_listbox.get(selected)
            window  = window.split(",")[0].strip()
            self.monitor.classifier.delete_windows(window , self.archive_file)
            self.window_listbox.delete(selected)
    def show_archived_classifactions(self):
        #change the icons
        if not self.archive_active:
            self.archive_button.configure(image=self.get_icon("online"))
            self.delete_button.configure(command=self.delete_archive , image=self.get_icon("box-delete"))
            self.edit_button.configure(command=self.restored_archived  , image=self.get_icon("box-ok"))
            windows = self.monitor.classifier.export_window_titles_to_array(self.archive_file).keys()
            self.new_button.configure(image='')
            self.window_classifications = {window: self.monitor.classifier.classify_activity(window , self.archive_file) for window in windows}
            # self.populate_listbox(self.window_classifications)

        else:
            self.new_button.configure(image=self.get_icon("add"))
            self.archive_button.configure(image=self.get_icon("archive"))
            self.edit_button.configure(command=self.edit_classification  , image=self.get_icon("edit"))
            windows = self.monitor.classifier.export_window_titles_to_array(self.monitor.classifier.data_file).keys()
            self.window_classifications = {window: self.monitor.classifier.classify_activity(window) for window in windows}
            self.delete_button.configure(command=self.delete_classification , image=self.get_icon("delete"))

        self.populate_listbox(self.window_classifications)
        self.archive_active = not self.archive_active


    def add_custom_classification(self):
        window_title = ctk.CTkInputDialog(text="Enter the window title:").get_input()
        if window_title:
            def confirm_selection():
                classification = combobox.get()
                if classification in self.classifier.get_classifications():
                    self.monitor.classifier.add_custom_classification(window_title, classification)
                    classification_window.destroy()
                    self.window_listbox.insert("end", f"{window_title}, {classification}")
                    self.show_notification("New App" , f"Custom classification added for '{window_title}' as '{classification}'")


            # Create the classification window
            classification_window = ctk.CTkToplevel()
            classification_window.title("Select Classification")
            classification_window.geometry("400x200")
            # Create a label for instruction
            label = ctk.CTkLabel(classification_window, text="Select the classification:")
            label.pack(pady=10)

            # Create a combobox with the classification options
            combobox = ctk.CTkComboBox(classification_window, values=self.classifier.get_classifications())
            combobox.pack(pady=10)

            # Button to confirm selection
            button = ctk.CTkButton(classification_window, text="Confirm", command=confirm_selection)
            button.pack(pady=10)
    def get_icon(self, icon_name, size=0.05 , invert=False):
        self.svgs = {}
        appearance_mode = ctk.get_appearance_mode()
        mode_suffix = "-dark" if appearance_mode == "Dark" else "-light"
        full_icon_name = icon_name + mode_suffix

        if full_icon_name not in self.svgs:
            if full_icon_name in img_paths:
                self.svgs[full_icon_name] = SvgImage(file=img_paths[full_icon_name], scale=size)

        return self.svgs.get(full_icon_name)

    def clear_icon(self, icon_name):
        # Clear both light and dark versions of the icon
        for mode_suffix in ["-dark", "-light"]:
            full_icon_name = icon_name + mode_suffix
            if full_icon_name in self.svgs:
                del self.svgs[full_icon_name]
    def create_User_tab(self):
        self.notebook.add("User Account")
        User_Account_tab = self.notebook.tab("User Account")

        # Create a Scrollable Frame for the whole tab content
        scrollable_frame = ctk.CTkScrollableFrame(User_Account_tab, width=600, height=400)
        scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)

        users_frame = ctk.CTkFrame(scrollable_frame)
        users_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(users_frame, text="UserName:").grid(row=0, column=0, padx=10, pady=5)
        self.username = ctk.CTkEntry(users_frame)
        self.username.grid(row=0, column=1, padx=10, pady=5)
        self.username.insert(0, "************")

        ctk.CTkLabel(users_frame, text="Gmail:").grid(row=1, column=0, padx=10, pady=5)
        self.gmail = ctk.CTkEntry(users_frame)
        self.gmail.grid(row=1, column=1, padx=10, pady=5)
        self.gmail.insert(0, "**********")

        ctk.CTkLabel(users_frame, text="Password:").grid(row=2, column=0, padx=10, pady=5)
        self.password = ctk.CTkEntry(users_frame)
        self.password.grid(row=2, column=1, padx=10, pady=5)
        self.password.insert(0, "*********")

        ctk.CTkLabel(users_frame, text="Confirm Password:").grid(row=3, column=0, padx=10, pady=5)
        self.c_passwrod = ctk.CTkEntry(users_frame)
        self.c_passwrod.grid(row=3, column=1, padx=10, pady=5)
        self.c_passwrod.insert(0, "************")

        self.auto_start_breaks_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(users_frame, text="Agree to the rules and terms", variable=self.auto_start_breaks_var).grid(row=4, column=0, padx=10, pady=5)

        apply_button = ctk.CTkButton(users_frame, text="Apply Settings", command=self.apply_pomodoro_settings)
        apply_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # Statistics Frame
        summary_frame = ctk.CTkFrame(scrollable_frame)
        summary_frame.pack(pady=20, padx=20, fill="x")

        label_summary = ctk.CTkLabel(summary_frame, text="Last Day Summary:")
        label_summary.pack(pady=1)
        self.textbox = ctk.CTkTextbox(summary_frame, width=500, height=150)
        self.textbox.pack(padx=20, pady=20)

        # Insert the paragraph text
        paragraph = summary.summary_return()
        self.textbox.insert("1.0", paragraph)
        self.textbox.configure(state="disabled")  # Make the text read-only

        # Stats Frame
        stats_frame = ctk.CTkFrame(scrollable_frame)
        stats_frame.pack(pady=20, padx=20, fill="x")

        self.pomodoro_count_label = ctk.CTkLabel(stats_frame, text="Pomodoros Completed: 0")
        self.pomodoro_count_label.pack(pady=2)

        self.total_focus_time_label = ctk.CTkLabel(stats_frame, text="Total Focus Time: 0 minutes")
        self.total_focus_time_label.pack(pady=3)



    def export_activity_log(self):
        # Get the current date for the filename
        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"Activiy_log_{today_date}.csv"
        filename_raw = f"Activiy_log_raw_{today_date}.csv"
        filename_all = f"Activiy_log_all.csv"
        # Create the folder for charts if it doesn't exist
        folder_path = os.path.join(self.monitor.get_today_folder(), "charts")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if not os.path.exists(SUMMARY_DIR):
            os.makedirs(SUMMARY_DIR)

        # Full path for the file
        file_path = os.path.join(folder_path, filename)
        file_path_raw = os.path.join(folder_path, filename_raw)
        file_path_all = os.path.join(SUMMARY_DIR, filename_all)

        # Save the file
        self.monitor.export_activity_log(file_path ,file_path_raw  ,file_path_all )

        # Notify the user
        self.show_notification("Export", f"Activity log exported to {file_path}")

    import threading

    def generate_daily_summary(self):
        selection_window = ctk.CTkToplevel(self)
        selection_window.title("Select Charts forms")
        selection_window.geometry("300x400")
        selection_window.attributes("-topmost", True)  # Always on top
        selection_frame = ctk.CTkFrame(selection_window)
        selection_frame.pack(pady=20, padx=20, fill="x")

        checkboxes = []
        for i, day in enumerate(["Horizontal Bar", "Vertical Bar", "Pie Chart", "Line Chart", "Area Chart", "Scatter Chart", "Bubble Chart", "Heatmap Chart"]):
            var = ctk.BooleanVar(value=1)
            checkbox = ctk.CTkCheckBox(selection_frame, text=day, variable=var)
            checkbox.grid(row=i, column=0, padx=10, pady=5)
            checkboxes.append(var)

        def select():
            selected = [var.get() for var in checkboxes]
            selection_window.destroy()

            # Start the summary generation in a separate thread
            thread = threading.Thread(target=self.monitor.generate_daily_summary, args=(selected,))
            thread.start()

            # Show notification without waiting for the task to complete
            self.show_notification("Summary", "Daily summaries are being generated!")

        select_button = ctk.CTkButton(selection_frame, text="Select", command=select)
        select_button.grid(row=len(checkboxes), column=0, columnspan=2, padx=10, pady=10)


    def apply_pomodoro_settings(self):
        try:
            self.pomodoro_time = int(self.pomodoro_duration.get()) * 60
            self.break_time = int(self.short_break_duration.get()) * 60
            self.long_break_time = int(self.long_break_duration.get()) * 60
            self.long_break_interval = int(self.long_break_interval_entry.get())
            self.auto_start_breaks = self.auto_start_breaks_var.get()
            self.auto_start_pomodoros = self.auto_start_pomodoros_var.get()
            # CTkMessagebox(title="Success", message="Pomodoro settings updated successfully!", icon="check")
            self.show_notification("Success", "Pomodoro settings updated successfully!")
        except ValueError:
            # CTkMessagebox(title="Error", message="Please enter valid numbers for all durations.", icon="cancel")
            self.show_notification("Error", "Please enter valid numbers for all durations.")


    def toggle_pomodoro(self):
        if not hasattr(self, "break_active"):
            self.break_active = False
        if not self.pomodoro_active and not self.break_active:
            self.start_pomodoro()
        elif self.paused:
            self.resume_session()
        else:
            self.pause_session()

    #in here work
    def start_pomodoro(self):
        self.pomodoro_active = True
        self.break_active = False
        self.paused = False
        self.current_time = self.pomodoro_time
        x = self.monitor.focus_mode_alert()
        print(x)
        self.sidebar.winfo_children()[2].configure(text="Pause Pomodoro")
        self.start_pause_button.configure(image=self.get_icon("pause"), text="", fg_color="transparent" , hover_color= Hover_color_dark)
        self.run_timer()

    def start_break(self):
        self.pomodoro_active = False
        self.break_active = True
        self.paused = False
        self.current_time = self.long_break_time if self.pomodoro_counter % self.long_break_interval == 0 else self.break_time
        self.start_pause_button.configure(image=self.get_icon("pause"), text="", fg_color="transparent")
        self.run_timer()

    def pause_session(self):
        self.paused = True
        self.start_pause_button.configure(image=self.get_icon("play"), text="", fg_color="transparent")
        self.sidebar.winfo_children()[2].configure(text="Resume Pomodoro")

    def resume_session(self):
        self.paused = False
        self.start_pause_button.configure(image=self.get_icon("pause"), text="", fg_color="transparent")
        self.sidebar.winfo_children()[2].configure(text="Pause Pomodoro")

    def reset_pomodoro(self):
        self.pomodoro_active = False
        self.break_active = False
        self.paused = False
        self.current_time = self.pomodoro_time
        self.pomodoro_counter = 0
        self.break_counter = 0
        self.start_pause_button.configure(image=self.get_icon("play"), text="", fg_color="transparent")
        self.reset_button.configure(image=self.get_icon("reset"), text="", fg_color="transparent")
        self.pomodoro_label.configure(text="Pomodoro: Not started")
        self.pomodoro_progress.set(0)
        self.update_statistics()

    def skip_session(self):
        self.skip_button.configure(image=self.get_icon("skip"), text="", )
        if self.break_active:
            self.complete_break()
        else:
            # Don't allow skipping Pomodoro sessions
            self.show_notification("Cannot Skip", "You can't skip a Pomodoro session. Stay focused!")
    def run_timer(self):
        def update_timer():
            if (self.pomodoro_active or self.break_active) and not self.paused:
                if self.current_time > 0:
                    minutes, seconds = divmod(self.current_time, 60)
                    session_type = "Pomodoro" if self.pomodoro_active else "Break"
                    self.pomodoro_label.configure(text=f"{session_type}: {minutes:02d}:{seconds:02d}")
                    total_time = self.pomodoro_time if self.pomodoro_active else (self.long_break_time if self.pomodoro_counter % self.long_break_interval == 0 else self.break_time)
                    progress = 1 - (self.current_time / total_time)
                    self.pomodoro_progress.set(progress)
                    self.current_time -= 1
                    self.after(1000, update_timer)
                else:
                    if self.pomodoro_active:
                        self.complete_pomodoro()
                    else:
                        self.complete_break()
            elif  self.paused:
                self.after(1000, update_timer)

        update_timer()

    def complete_pomodoro(self):
        self.pomodoro_active = False
        self.pomodoro_counter += 1
        self.update_statistics()
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
        # CTkMessagebox(title="Pomodoro Completed", message="Time for a break!", icon="info")
        self.show_notification("Pomodoro Completed", "Time for a break!")
        if self.auto_start_breaks:
            self.start_break()
        else:
            self.start_pause_button.configure(image=self.get_icon("play"), text="",)
            self.pomodoro_label.configure(text="Break: Not started")

    def complete_break(self):

        self.break_active = False
        self.break_counter += 1
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
        # CTkMessagebox(title="Break Completed", message="Time to focus!", icon="info")
        self.show_notification("Break Completed", "Time to focus!")
        if self.auto_start_pomodoros:
            self.start_pomodoro()
        else:
            self.start_pause_button.configure(image=self.get_icon("play"), text="", )

            self.pomodoro_label.configure(text="Pomodoro: Not started")

    def update_statistics(self):
        self.pomodoro_count_label.configure(text=f"Pomodoros Completed: {self.pomodoro_counter}")
        total_focus_time = self.pomodoro_counter * (self.pomodoro_time // 60)
        self.total_focus_time_label.configure(text=f"Total Focus Time: {total_focus_time} minutes")

    def update_break_label(self):
        minutes, seconds = divmod(self.break_time, 60)
        self.pomodoro_label.configure(text=f"Break: {minutes:02d}:{seconds:02d} remaining")

    # Function to interpolate color from green to red
    def get_progress_color(self, progress, start_color, end_color):
        """
        Get the color that represents the progress as a transition between two colors.

        :param progress: A float between 0 and 1 indicating the progress (0 = start color, 1 = end color).
        :param start_color: A tuple (R, G, B) for the start color.
        :param end_color: A tuple (R, G, B) for the end color.

        :return: Hex string representing the color at the given progress.
        """
        start_red, start_green, start_blue = start_color
        end_red, end_green, end_blue = end_color

        # Calculate the intermediate color based on progress
        red = int(start_red + (end_red - start_red) * progress)
        green = int(start_green + (end_green - start_green) * progress)
        blue = int(start_blue + (end_blue - start_blue) * progress)

        # Convert to hex format
        return f'#{red:02x}{green:02x}{blue:02x}'


    # Function to update progress and color
    def update_progress(self , value  , progress_bar , red , green ):
        # Set the progress bar value
        progress_bar.set(value)

        # Update the color dynamically based on progress
        color = self.get_progress_color(value , red , green )
        progress_bar.configure(progress_color=color)
    def update_ui(self):
        current_time = time.time()
        if current_time - self.last_ui_update >= self.update_interval:
            self.update_dashboard_tab()
            self.update_log_tab()
            self.update_Legos_tab()
            self.last_ui_update = current_time
        self.after(1000, self.update_ui)  # Schedule the next update

    def create_dashboard_tab(self):
        # Add a tab to the notebook
        self.notebook.add("Dashboard")

        # Get the created Dashboard tab and place elements in it
        dashboard_tab = self.notebook.tab("Dashboard")
        self.goal_label = ctk.CTkLabel(dashboard_tab, text="Daily Goal: 0 minutes", font=ctk.CTkFont(size=16))
        self.goal_label.pack(pady=10)

        self.progress_bar_frame = ctk.CTkFrame(dashboard_tab)
        self.progress_bar_frame.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.progress_bar_frame, width=400, corner_radius=0)  # 400px
        self.progress_bar.grid(row=0, column=0, padx=0)

        # Initializing progress bars with progress set to 0
        self.progress_bar.set(0)

        self.current_app_label = ctk.CTkLabel(dashboard_tab, text="Current App: None", font=ctk.CTkFont(size=16))
        self.current_app_label.pack(pady=10)

        # Pomodoro section
        pomodoro_frame = ctk.CTkFrame(dashboard_tab)
        pomodoro_frame.pack(pady=20, padx=20, fill="x")

        self.pomodoro_label = ctk.CTkLabel(pomodoro_frame, text="Pomodoro: Not started", font=ctk.CTkFont(size=16))
        self.pomodoro_label.pack(pady=10)

        self.pomodoro_progress = ctk.CTkProgressBar(pomodoro_frame, width=300)
        self.pomodoro_progress.pack(pady=10)
        self.pomodoro_progress.set(0)

        button_frame = ctk.CTkFrame(pomodoro_frame)
        button_frame.pack(pady=10)


        self.start_pause_button = ctk.CTkButton(button_frame, text="", image=self.get_icon("play"), fg_color="transparent",width=35, command=self.toggle_pomodoro  )
        self.start_pause_button.pack(side="left", padx=5)

        self.skip_button = ctk.CTkButton(button_frame, text="", image=self.get_icon("skip"),fg_color="transparent" ,width=35, command=self.skip_session)
        self.skip_button.pack(side="left", padx=5)

        self.reset_button = ctk.CTkButton(button_frame, text="", image=self.get_icon("reset"),fg_color="transparent" ,width=35, command=self.reset_pomodoro)
        self.reset_button.pack(side="left", padx=5)

        # Create the productivity chart
        self.productivity_chart = ctk.CTkFrame(dashboard_tab, width=400, height=200)
        self.productivity_chart.pack(pady=20)
        # Here you would integrate a charting library to show productivity over time


        self.goal_label2 = ctk.CTkLabel(dashboard_tab, text="", font=ctk.CTkFont(size=16))

    def create_log_tab(self):
        # Add a tab to the notebook
        self.notebook.add("Activity Log")

        # Get the created Dashboard tab and place elements in it
        log_tab = self.notebook.tab("Activity Log")
        columns = ( "window_title", "duration", "classification")
        self.tree = ttk.Treeview(log_tab, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill='both', expand=True)
    def create_Legos_tab(self):
        self.notebook.add("LegoRelations")

        # Get the created Dashboard tab and place elements in it
        Legos_tab = self.notebook.tab("LegoRelations")
        self.lego_label = ctk.CTkLabel(Legos_tab, text="")
        self.lego_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Rules list using grid
        self.rules_frame = ctk.CTkScrollableFrame(self.lego_label)
        self.rules_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Search bar using grid
        search_frame = ctk.CTkFrame(self.lego_label)
        search_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Entry and Button in the search frame
        ctk.CTkEntry(search_frame, placeholder_text="Search rules...").grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(search_frame, text="Search", width=100).grid(row=0, column=1, padx=5)

        # Configure grid weights for proper expansion
        Legos_tab.grid_rowconfigure(1, weight=1)  # Allow rules_frame to expand
        Legos_tab.grid_columnconfigure(0, weight=1)  # Allow horizontal expansion
        search_frame.grid_columnconfigure(0, weight=1)  # Expand search entry
    
    def show_add_rule_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Rule")
        dialog.geometry("600x700")
        dialog.transient(self.root)

        # App name
        ctk.CTkLabel(dialog, text="Application Name:").pack(pady=5)
        app_name = ctk.CTkEntry(dialog)
        app_name.pack(pady=5)

        # Conditions frame
        conditions_frame = ctk.CTkFrame(dialog)
        conditions_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(conditions_frame, text="Conditions").pack()

        # Condition types
        condition_types = ["time_exceeds", "time_between", "day_of_week", "app_running",
                         "cpu_usage", "memory_usage", "keyboard_pressed"]

        condition_var = ctk.StringVar(value=condition_types[0])
        condition_dropdown = ctk.CTkOptionMenu(conditions_frame, values=condition_types,
                                             variable=condition_var)
        condition_dropdown.pack(pady=5)

        # Condition value
        ctk.CTkLabel(conditions_frame, text="Condition Value:").pack()
        condition_value = ctk.CTkEntry(conditions_frame)
        condition_value.pack(pady=5)

        # Actions frame
        actions_frame = ctk.CTkFrame(dialog)
        actions_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(actions_frame, text="Actions").pack()

        # Action types
        action_types = ["close_app", "minimize_app", "start_app", "send_notification",
                       "play_sound", "take_screenshot", "keyboard_shortcut"]

        action_var = ctk.StringVar(value=action_types[0])
        action_dropdown = ctk.CTkOptionMenu(actions_frame, values=action_types,
                                          variable=action_var)
        action_dropdown.pack(pady=5)

        # Action parameters
        ctk.CTkLabel(actions_frame, text="Action Parameters:").pack()
        action_params = ctk.CTkEntry(actions_frame)
        action_params.pack(pady=5)

        def add_rule():
            try:
                new_event = AppEvent(
                    app_name=app_name.get(),
                    event_type="custom",
                    conditions=[{
                        "type": condition_var.get(),
                        "value": condition_value.get()
                    }],
                    actions=[{
                        "type": action_var.get(),
                        "params": {"value": action_params.get()}
                    }]
                )
                self.automation.add_event(new_event)
                self.update_rules_display()
                dialog.destroy()
                # CTkMessagebox(title="Success", message="Rule added successfully!")
                self.show_notification("Success", "Rule added successfully!")
            except Exception as e:
                # CTkMessagebox(title="Error", message=f"Error adding rule: {str(e)}", icon="cancel")
                self.show_notification("Error", f"Error adding rule: {str(e)}", icon="cancel")
        # Add button
        ctk.CTkButton(dialog, text="Add Rule", command=add_rule).pack(pady=20)
    def update_rules_display(self):
        # Clear current rules display
        for widget in self.rules_frame.winfo_children():
            widget.destroy()

        # Add each rule to the display
        for event in self.automation.events:
            rule_frame = ctk.CTkFrame(self.rules_frame)
            rule_frame.pack(fill="x", padx=5, pady=5)

            # Rule header
            header_frame = ctk.CTkFrame(rule_frame)
            header_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(header_frame, text=f"App: {event.app_name}").pack(side="left")

            # Control buttons
            ctk.CTkButton(header_frame, text="Edit", width=60,
                         command=lambda e=event: self.edit_rule(e)).pack(side="right", padx=5)
            ctk.CTkButton(header_frame, text="Delete", width=60,
                         command=lambda e=event: self.delete_rule(e)).pack(side="right", padx=5)

            # Conditions and actions
            details_frame = ctk.CTkFrame(rule_frame)
            details_frame.pack(fill="x", padx=5, pady=5)

            conditions_text = "\n".join([f"Condition: {c['type']} = {c['value']}"
                                       for c in event.conditions])
            actions_text = "\n".join([f"Action: {a['type']}" for a in event.actions])

            ctk.CTkLabel(details_frame, text=conditions_text).pack(pady=2)
            ctk.CTkLabel(details_frame, text=actions_text).pack(pady=2)
    def load_rules(self):
        # Load saved rules from file if exists
        rules_file = Path('automation_rules.json')
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                    for rule_data in rules_data:
                        event = AppEvent(**rule_data)
                        self.automation.add_event(event)
                self.update_rules_display()
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Error loading rules: {str(e)}", icon="cancel")

    def save_rules(self):
        # Save current rules to file
        rules_data = [vars(event) for event in self.automation.events]
        with open('automation_rules.json', 'w') as f:
            json.dump(rules_data, f)

    def edit_rule(self, event):
        # Similar to add_rule_dialog but populate with existing values
        pass

    def delete_rule(self, event):
        if CTkMessagebox(title="Confirm Delete",
                        message="Are you sure you want to delete this rule?",
                        icon="question", option_1="Yes", option_2="No").get() == "Yes":
            self.automation.events.remove(event)
            self.update_rules_display()
            self.save_rules()
    def create_settings_tab(self):
        self.notebook.add("Settings")

        # Get the created Dashboard tab and place elements in it
        settings_tab = self.notebook.tab("Settings")

        #Pomodoro settings
        settings_frame = ctk.CTkFrame(settings_tab)
        settings_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(settings_frame, text="Pomodoro Duration (minutes):").grid(row=0, column=0, padx=10, pady=5)
        self.pomodoro_duration = ctk.CTkEntry(settings_frame)
        self.pomodoro_duration.grid(row=0, column=1, padx=10, pady=5)
        self.pomodoro_duration.insert(0, "25")

        ctk.CTkLabel(settings_frame, text="Short Break Duration (minutes):").grid(row=1, column=0, padx=10, pady=5)
        self.short_break_duration = ctk.CTkEntry(settings_frame)
        self.short_break_duration.grid(row=1, column=1, padx=10, pady=5)
        self.short_break_duration.insert(0, "5")

        ctk.CTkLabel(settings_frame, text="Long Break Duration (minutes):").grid(row=2, column=0, padx=10, pady=5)
        self.long_break_duration = ctk.CTkEntry(settings_frame)
        self.long_break_duration.grid(row=2, column=1, padx=10, pady=5)
        self.long_break_duration.insert(0, "15")

        ctk.CTkLabel(settings_frame, text="Long Break Interval:").grid(row=3, column=0, padx=10, pady=5)
        self.long_break_interval_entry = ctk.CTkEntry(settings_frame)
        self.long_break_interval_entry.grid(row=3, column=1, padx=10, pady=5)
        self.long_break_interval_entry.insert(0, "4")

        self.auto_start_breaks_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(settings_frame, text="Auto-start breaks", variable=self.auto_start_breaks_var).grid(row=4, column=0, padx=10, pady=5)

        self.auto_start_pomodoros_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(settings_frame, text="Auto-start pomodoros", variable=self.auto_start_pomodoros_var).grid(row=4, column=1, padx=10, pady=5)

        apply_button = ctk.CTkButton(settings_frame, text="Apply Settings", command=self.apply_pomodoro_settings)
        apply_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # Daily goal setting
        goal_frame = ctk.CTkFrame(settings_tab)
        goal_frame.pack(pady=20, padx=20, fill="x")

        goal_label = ctk.CTkLabel(goal_frame, text="Set Daily Productive Time Goal (minutes):")
        goal_label.pack(side="left", padx=10)

        self.goal_entry = ctk.CTkEntry(goal_frame)
        self.goal_entry.pack(side="left", padx=10)
        self.goal_entry.insert(0, "60")  # Default 4 hours

        set_goal_button = ctk.CTkButton(goal_frame, text="",image=self.get_icon("check"),fg_color="transparent", command=self.set_daily_goal , hover_color=Hover_color_dark ,width=35)
        set_goal_button.pack(side="left", padx=10)

        #sync
        theme_frame = ctk.CTkFrame(settings_tab)
        theme_frame.pack(pady=20, padx=20, fill="x")

        theme_label = ctk.CTkLabel(theme_frame, text="Select Theme:")
        theme_label.pack(side="left", padx=10)

        self.theme_var = ctk.StringVar(value="dark")
        theme_option = ctk.CTkOptionMenu(theme_frame, values=["light", "dark" ], command=self.change_theme, variable=self.theme_var)
        theme_option.pack(side="left", padx=10)
        set_sync_button = ctk.CTkButton(theme_frame, text="",image=self.get_icon("refresh"), command=self.refresher , hover_color=Hover_color_dark ,width=35 , fg_color="transparent")
        set_sync_button.pack(side="right", padx=10)
        sync_label = ctk.CTkLabel(theme_frame, text="Refreshing:")
        sync_label.pack(side="right", padx=10)

        #Im/Export settings
        port_frame = ctk.CTkFrame(settings_tab)
        port_frame.pack(pady=20, padx=20, fill="x")

        port_label = ctk.CTkLabel(port_frame, text="Import/Export datasets (csv format):")
        port_label.pack(side="left", padx=10)
        port_button = ctk.CTkButton(port_frame, text="",image=self.get_icon("box-delete"), command=self.export_csv , hover_color=Hover_color_dark ,width=35 , fg_color="transparent")
        port_button.pack(side="right", padx=10)
        port_button = ctk.CTkButton(port_frame, text="",image=self.get_icon("box-add"), command=self.import_csv , hover_color=Hover_color_dark ,width=35 , fg_color="transparent")
        port_button.pack(side="right", padx=10)


    def export_csv(self):
        x, y = self.classifier.export_training_data()
        if x:
            self.show_notification("Training Data Exported", "Training data exported to the specified file.")
        else:
            self.show_notification("Error", f"Error: {y}")

        # self.show_notification("Success","Exported training data to CSV file")
    def import_csv(self):
        import tkinter as tk  # Import tkinter for the Toplevel
        from tkinter import filedialog
        from tkinterdnd2 import TkinterDnD, DND_FILES
        import customtkinter as ctk
        # Create a new top-level window (modal window)
        root_import = tk.Toplevel(self)  # Use Toplevel from tkinter
        root_import.title("Import CSV file")

        # Apply the same theme as the main window
        ctk.set_appearance_mode(self.theme)

        # Center the window
        window_width = 400
        window_height = 100
        screen_width = root_import.winfo_screenwidth()
        screen_height = root_import.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        root_import.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        # Make the secondary window modal (disable interaction with the main window)
        root_import.grab_set()

        # CustomTkinter Label and Button
        label = ctk.CTkLabel(root_import, text="Drag and drop the CSV file or select from folders")
        label.pack(pady=10)

        def select_file():
            file = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
            if file:
                self.classifier.import_training_data(file)
                root_import.destroy()

        button = ctk.CTkButton(root_import, text="Browse", command=select_file)
        button.pack(pady=10)

        def drag_drop(event):
            file = event.data.splitlines()[0]
            if file:
                self.classifier.import_training_data(file)
                root_import.destroy()

        # Enable TkinterDnD2 drag-and-drop for the new window
        TkinterDnD(root_import)  # Enable DnD on the Toplevel
        root_import.drop_target_register(DND_FILES)
        root_import.dnd_bind('<<Drop>>', drag_drop)

        # Wait for the window to close before continuing in the main window
        root_import.wait_window()

    def update_dashboard_tab(self):
        current_app = self.monitor.get_active_window()
        if self.classifier.preprocess_window_title(current_app) != default_app:
            self.previous_app = self.classifier.preprocess_window_title(current_app)

        self.current_app_label.configure(text=f"Current App: {self.previous_app}")

        productive_time = self.monitor.get_productive_time()
        daily_goal = int(self.goal_entry.get()) if self.goal_entry.get() else self.previous_daily_goal
        self.previous_daily_goal = daily_goal

        progress = min(productive_time / (daily_goal * 60), 1)

        if  0.3333333333333333 == progress  and progress not in self.sent_notifications:
            self.send_random_notification(notifications_1_3)
            self.sent_notifications.add(progress)

        if   0.6666666666666666 == progress  and progress not in self.sent_notifications:
            self.send_random_notification(notifications_2_3)
            self.sent_notifications.add(progress)

        if  progress == 1   and progress not in self.sent_notifications:
            self.send_random_notification(notifications_3_3)
            self.sent_notifications.add(progress)

        if ((productive_time // 60) % (daily_goal)) % 1 and progress == 1 :
            self.send_random_notification(notifications_over)
            self.sent_notifications.add(productive_time % (daily_goal * 60))






        self.update_progress(progress, self.progress_bar, RED, GREEN)

        self.goal_label.configure(text=f"Daily Goal: {int(productive_time // 60)}/{daily_goal} minutes")
        if int(productive_time // 60) >= daily_goal:
            self.goal_label2.configure(text=f"Over-Daily Goal: + {int(productive_time // 60) - daily_goal} minutes, Please take a break!")
            self.goal_label2.pack(pady=10)
        else:
            self.goal_label2.pack_forget()

        #chart

    def update_log_tab(self, *args):
            current_time = time.time()
            if self.cached_log_data is None or current_time - self.last_log_update > 60:  # Update cache every minute
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

                conn = sqlite3.connect('helpers/sources/activity_log.db')
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT window_title, SUM(duration) as total_duration, classification
                    FROM activity_log
                    WHERE datetime(timestamp) >= ?
                    GROUP BY window_title, classification
                    ORDER BY total_duration DESC
                    LIMIT 100
                ''', (today,))
                self.cached_log_data = cursor.fetchall()
                conn.close()
                self.last_log_update = current_time

            self.tree.delete(*self.tree.get_children())

            for window_title, total_duration, classification in self.cached_log_data:
                formatted_duration = self.format_time(total_duration)
                self.tree.insert("", "end", values=(window_title, formatted_duration, classification))

    @staticmethod
    def format_time(seconds):
               hours, remainder = divmod(seconds, 3600)
               minutes, seconds = divmod(remainder, 60)
               return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"



    def update_Legos_tab(self):
        if self.screenshots:
            current_screenshot = self.screenshots[self.current_screenshot_index]
            if current_screenshot not in self.cached_screenshots:
                img = Image.open(current_screenshot)
                img = img.resize((400, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.cached_screenshots[current_screenshot] = photo
            else:
                photo = self.cached_screenshots[current_screenshot]

            self. lego_label.configure(image=photo)
            self. lego_label.image = photo

    def show_previous_screenshot(self):
        if self.current_screenshot_index > 0:
            self.current_screenshot_index -= 1
            self.update_Legos_tab()

    def show_next_screenshot(self):
        if self.current_screenshot_index < len(self.screenshots) - 1:
            self.current_screenshot_index += 1
            self.update_Legos_tab()

    def set_daily_goal(self):
        try:
            goal = int(self.goal_entry.get())
            if goal > 0:
                self.show_notification("Success" , f"Daily goal set to {goal} minutes" )
                # messagebox.showinfo("Success", f"Daily goal set to {goal} minutes")
            else:
                raise ValueError
        except ValueError:
            self.show_notification("Error" , "Please enter a valid positive number for the daily goal" )
            # messagebox.showerror("Error", "Please enter a valid positive number for the daily goal")
    def set_time_pomodorro(self):
        try:
            goal = int(self.pom_entry.get())
            if goal > 0:
                # messagebox.showinfo("Success", f"Pomodorro session set to {goal} minutes")
                self.show_notification("Success" , f"Pomodorro session set to {goal} minutes")

            else:
                raise ValueError
        except ValueError:
            self.show_notification("Error" , "Please enter a valid positive number for the Pomodorro session" )
            # messagebox.showerror("Error", "Please enter a valid positive number for the Pomodorro session")
    def set_time_Break(self):
        try:
            goal = int(self.break_entry.get())
            if goal > 0:
                messagebox.showinfo("Success", f"Break Time set to {goal} minutes")
            else:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for the Break Time")


    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)
        self.theme = new_theme
        self.update_icons()

    def update_icons(self):
        # Update sidebar toggle button
        self.toggle_button.configure(image=self.get_icon("sm-arrow-left" if self.sidebar_open else "sm-arrow-right", size=0.03))

        # Update sidebar buttons
        for btn, (_, icon_name, _) in zip(self.sidebar_buttons, self.buttons_info):
            btn.configure(image=self.get_icon(icon_name))

        # Update other buttons in the application
        icon_updates = {
            self.skip_button: "skip",
            self.start_pause_button: "pause" if not self.paused else "play",
            self.reset_button: "reset"
        }
        for button, icon_name in icon_updates.items():
            button.configure(image=self.get_icon(icon_name))

    def animate_sidebar(self, new_width):
        def _animate(current_width):
            if (new_width > current_width and current_width < new_width) or \
               (new_width < current_width and current_width > new_width):
                current_width += 10 if new_width > current_width else -10
                self.sidebar.configure(width=current_width)
                self.after(10, lambda: _animate(current_width))
            else:
                self.sidebar.configure(width=new_width)

        _animate(self.sidebar.winfo_width())

    def show_notification(self , title, message , icon = "helpers/sources/assets/icons/bell.ico" ):
        notification.notify(
            title=title,
            ticker= "Activity Tracker",
            message=message,
            app_name = "Activity Tracker",
            timeout=2,  # Duration the notification will stay on screen
            app_icon= icon , # Optional: Add an icon if available
            toast= False
        )

    def send_random_notification(self , notifications):
        title = "Progress Update"
        message = rd.choice(notifications)
        self.show_notification(title, message)
