# import customtkinter as ctk
# import json
# from pathlib import Path
# import threading
# from CTkMessagebox import CTkMessagebox
# from automation_system import AppAutomation, AppEvent  # Importing from your automation script

# class AutomationGUI:
#     def __init__(self):
#         self.automation = AppAutomation()
#         self.running = False
#         self.setup_gui()
#         self.load_rules()

#     def setup_gui(self):
#         ctk.set_appearance_mode("dark")
#         ctk.set_default_color_theme("blue")

#         self.root = ctk.CTk()
#         self.root.title("Automation Control Panel")
#         self.root.geometry("1200x800")

#         # Save rules on close
#         self.root.protocol("WM_DELETE_WINDOW", self.on_close)

#         self.create_sidebar()
#         self.create_main_content()
#         self.create_status_bar()

#     def create_sidebar(self):
#         sidebar = ctk.CTkFrame(self.root, width=200)
#         sidebar.pack(side="left", fill="y", padx=10, pady=10)

#         ctk.CTkLabel(sidebar, text="LogoFunctions", font=("Arial", 20, "bold")).pack(pady=20)
#         self.start_button = ctk.CTkButton(sidebar, text="Start Monitoring", command=self.toggle_monitoring)
#         self.start_button.pack(pady=10)
#         ctk.CTkButton(sidebar, text="Add New Rule", command=self.show_add_rule_dialog).pack(pady=10)
#         # ctk.CTkButton(sidebar, text="View Statistics", command=self.show_statistics).pack(pady=10)
#         # ctk.CTkButton(sidebar, text="Settings", command=self.show_settings).pack(pady=10)

#     def create_main_content(self):
#         main_content = ctk.CTkFrame(self.root)
#         main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
#         self.rules_frame = ctk.CTkScrollableFrame(main_content)
#         self.rules_frame.pack(fill="both", expand=True, padx=10, pady=10)

#         search_frame = ctk.CTkFrame(main_content)
#         search_frame.pack(fill="x", padx=10, pady=(0, 10))
#         ctk.CTkEntry(search_frame, placeholder_text="Search rules...").pack(side="left", fill="x", expand=True)
#         ctk.CTkButton(search_frame, text="Search", width=100).pack(side="right", padx=5)

#     def create_status_bar(self):
#         self.status_bar = ctk.CTkLabel(self.root, text="Status: Ready")
#         self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

#     def show_add_rule_dialog(self):
#         dialog = ctk.CTkToplevel(self.root)
#         dialog.title("Add New Rule")
#         dialog.geometry("600x700")
#         dialog.transient(self.root)

#         ctk.CTkLabel(dialog, text="Application Name:").pack(pady=5)
#         app_name = ctk.CTkEntry(dialog)
#         app_name.pack(pady=5)

#         conditions_frame = ctk.CTkFrame(dialog)
#         conditions_frame.pack(fill="x", padx=10, pady=10)
#         ctk.CTkLabel(conditions_frame, text="Conditions").pack()
#         condition_var = ctk.StringVar(value="time_exceeds")
#         ctk.CTkOptionMenu(conditions_frame, values=["time_exceeds", "time_between", "day_of_week"], variable=condition_var).pack(pady=5)
#         condition_value = ctk.CTkEntry(conditions_frame)
#         condition_value.pack(pady=5)

#         actions_frame = ctk.CTkFrame(dialog)
#         actions_frame.pack(fill="x", padx=10, pady=10)
#         ctk.CTkLabel(actions_frame, text="Actions").pack()
#         action_var = ctk.StringVar(value="send_notification")
#         ctk.CTkOptionMenu(actions_frame, values=["close_app", "send_notification"], variable=action_var).pack(pady=5)
#         action_params = ctk.CTkEntry(actions_frame)
#         action_params.pack(pady=5)

#         def add_rule():
#             try:
#                 new_event = AppEvent(
#                     app_name=app_name.get(),
#                     event_type="custom",
#                     conditions=[{"type": condition_var.get(), "value": condition_value.get()}],
#                     actions=[{"type": action_var.get(), "params": {"value": action_params.get()}}]
#                 )
#                 self.automation.add_event(new_event)
#                 self.update_rules_display()
#                 dialog.destroy()
#                 CTkMessagebox(title="Success", message="Rule added successfully!")
#             except Exception as e:
#                 CTkMessagebox(title="Error", message=f"Error adding rule: {str(e)}", icon="cancel")

#         ctk.CTkButton(dialog, text="Add Rule", command=add_rule).pack(pady=20)

#     def update_rules_display(self):
#         for widget in self.rules_frame.winfo_children():
#             widget.destroy()
#         for event in self.automation.events:
#             rule_frame = ctk.CTkFrame(self.rules_frame)
#             rule_frame.pack(fill="x", padx=5, pady=5)

#             header_frame = ctk.CTkFrame(rule_frame)
#             header_frame.pack(fill="x", padx=5, pady=5)
#             ctk.CTkLabel(header_frame, text=f"App: {event.app_name}").pack(side="left")
#             ctk.CTkButton(header_frame, text="Edit", width=60, command=lambda e=event: self.edit_rule(e)).pack(side="right", padx=5)
#             ctk.CTkButton(header_frame, text="Delete", width=60, command=lambda e=event: self.delete_rule(e)).pack(side="right", padx=5)

#             details_frame = ctk.CTkFrame(rule_frame)
#             details_frame.pack(fill="x", padx=5, pady=5)
#             conditions_text = "\n".join([f"Condition: {c['type']} = {c['value']}" for c in event.conditions])
#             actions_text = "\n".join([f"Action: {a['type']}" for a in event.actions])
#             ctk.CTkLabel(details_frame, text=conditions_text).pack(pady=2)
#             ctk.CTkLabel(details_frame, text=actions_text).pack(pady=2)

#     def toggle_monitoring(self):
#         if not self.running:
#             self.running = True
#             self.start_button.configure(text="Stop Monitoring")
#             self.status_bar.configure(text="Status: Monitoring active")
#             self.monitor_thread = threading.Thread(target=self.automation.monitor)
#             self.monitor_thread.daemon = True
#             self.monitor_thread.start()
#         else:
#             self.running = False
#             self.start_button.configure(text="Start Monitoring")
#             self.status_bar.configure(text="Status: Monitoring stopped")

#     def load_rules(self):
#         rules_file = Path('automation_rules.json')
#         if rules_file.exists():
#             try:
#                 with open(rules_file, 'r') as f:
#                     rules_data = json.load(f)
#                     for rule_data in rules_data:
#                         event = AppEvent(**rule_data)
#                         self.automation.add_event(event)
#                 self.update_rules_display()
#             except Exception as e:
#                 CTkMessagebox(title="Error", message=f"Error loading rules: {str(e)}", icon="cancel")

#     def save_rules(self):
#         rules_data = [vars(event) for event in self.automation.events]
#         with open('automation_rules.json', 'w') as f:
#             json.dump(rules_data, f)

#     def edit_rule(self, event):
#         dialog = ctk.CTkToplevel(self.root)
#         dialog.title("Edit Rule")
#         dialog.geometry("600x700")
#         dialog.transient(self.root)

#         ctk.CTkLabel(dialog, text="Application Name:").pack(pady=5)
#         app_name = ctk.CTkEntry(dialog)
#         app_name.insert(0, event.app_name)
#         app_name.pack(pady=5)

#         conditions_frame = ctk.CTkFrame(dialog)
#         conditions_frame.pack(fill="x", padx=10, pady=10)
#         ctk.CTkLabel(conditions_frame, text="Conditions").pack()
#         condition_var = ctk.StringVar(value=event.conditions[0]["type"])
#         ctk.CTkOptionMenu(conditions_frame, values=["time_exceeds", "time_between"], variable=condition_var).pack(pady=5)
#         condition_value = ctk.CTkEntry(conditions_frame)
#         condition_value.insert(0, event.conditions[0]["value"])
#         condition_value.pack(pady=5)

#         actions_frame = ctk.CTkFrame(dialog)
#         actions_frame.pack(fill="x", padx=10, pady=10)
#         ctk.CTkLabel(actions_frame, text="Actions").pack()
#         action_var = ctk.StringVar(value=event.actions[0]["type"])
#         ctk.CTkOptionMenu(actions_frame, values=["close_app", "send_notification"], variable=action_var).pack(pady=5)
#         action_params = ctk.CTkEntry(actions_frame)
#         action_params.insert(0, event.actions[0]["params"].get("value", ""))
#         action_params.pack(pady=5)

#         def save_edit():
#             try:
#                 event.app_name = app_name.get()
#                 event.conditions = [{"type": condition_var.get(), "value": condition_value.get()}]
#                 event.actions = [{"type": action_var.get(), "params": {"value": action_params.get()}}]
#                 self.update_rules_display()
#                 dialog.destroy()
#                 CTkMessagebox(title="Success", message="Rule updated successfully!")
#             except Exception as e:
#                 CTkMessagebox(title="Error", message=f"Error saving changes: {str(e)}", icon="cancel")

#         ctk.CTkButton(dialog, text="Save Changes", command=save_edit).pack(pady=20)

#     def delete_rule(self, event):
#         if CTkMessagebox(title="Confirm Delete", message="Are you sure you want to delete this rule?", icon="question", option_1="Yes", option_2="No").get() == "Yes":
#             self.automation.events.remove(event)
#             self.update_rules_display()
#             self.save_rules()

#     def on_close(self):
#         self.save_rules()
#         self.root.destroy()

#     def run(self):
#         self.root.mainloop()

# if __name__ == "__main__":
#     app = AutomationGUI()
#     app.run()
# #

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QTabWidget, QPushButton, QLabel,
                           QListWidget, QProgressBar, QComboBox, QSpinBox,
                           QSystemTrayIcon, QMenu, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import json

class AutomationWorker(QThread):
    status_updated = pyqtSignal(dict)

    def __init__(self, automation):
        super().__init__()
        self.automation = automation
        self.running = True

    def run(self):
        while self.running:
            current_stats = {
                'active_apps': list(self.automation.active_apps),
                'usage_history': dict(self.automation.usage_history),
                'achievements': list(self.automation.achievements),
                'pomodoro_active': self.automation.pomodoro_active,
                'break_time': self.automation.break_time
            }
            self.status_updated.emit(current_stats)
            self.msleep(1000)  # Update every second

    def stop(self):
        self.running = False

class PomodoroWidget(QWidget):
    def __init__(self, automation):
        super().__init__()
        self.automation = automation
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Timer settings
        settings_group = QGroupBox("Pomodoro Settings")
        settings_layout = QHBoxLayout()

        self.work_time = QSpinBox()
        self.work_time.setRange(1, 60)
        self.work_time.setValue(25)
        self.break_time = QSpinBox()
        self.break_time.setRange(1, 30)
        self.break_time.setValue(5)

        settings_layout.addWidget(QLabel("Work (min):"))
        settings_layout.addWidget(self.work_time)
        settings_layout.addWidget(QLabel("Break (min):"))
        settings_layout.addWidget(self.break_time)
        settings_group.setLayout(settings_layout)

        # Control buttons
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Pomodoro")
        self.stop_button = QPushButton("Stop Pomodoro")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_pomodoro)
        self.stop_button.clicked.connect(self.stop_pomodoro)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)

        # Status
        self.status_label = QLabel("Not active")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(settings_group)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def start_pomodoro(self):
        work_minutes = self.work_time.value()
        break_minutes = self.break_time.value()
        self.automation.start_pomodoro(work_minutes, break_minutes)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Pomodoro active")

    def stop_pomodoro(self):
        self.automation.pomodoro_active = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Not active")

class ProductivityChart(QWidget):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_chart(self, data):
        self.ax.clear()
        if data:
            categories = list(data.keys())
            times = list(data.values())
            self.ax.pie(times, labels=categories, autopct='%1.1f%%')
            self.ax.set_title('Time Distribution by Category')
        self.canvas.draw()

class AchievementsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        layout.addWidget(QLabel("Achievements"))
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def update_achievements(self, achievements):
        self.list_widget.clear()
        self.list_widget.addItems(achievements)

class MainWindow(QMainWindow):
    def __init__(self, automation):
        super().__init__()
        self.automation = automation
        self.setWindowTitle("App Automation Dashboard")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.setup_system_tray()
        self.start_monitoring()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()

        # Dashboard tab
        dashboard = QWidget()
        dashboard_layout = QVBoxLayout()

        # Active apps
        self.active_apps_list = QListWidget()
        dashboard_layout.addWidget(QLabel("Active Applications"))
        dashboard_layout.addWidget(self.active_apps_list)

        # Daily goals progress
        goals_group = QGroupBox("Daily Goals Progress")
        goals_layout = QVBoxLayout()

        self.productive_progress = QProgressBar()
        self.learning_progress = QProgressBar()
        self.exercise_progress = QProgressBar()

        goals_layout.addWidget(QLabel("Productive Time"))
        goals_layout.addWidget(self.productive_progress)
        goals_layout.addWidget(QLabel("Learning Time"))
        goals_layout.addWidget(self.learning_progress)
        goals_layout.addWidget(QLabel("Exercise Time"))
        goals_layout.addWidget(self.exercise_progress)

        goals_group.setLayout(goals_layout)
        dashboard_layout.addWidget(goals_group)

        dashboard.setLayout(dashboard_layout)
        tabs.addTab(dashboard, "Dashboard")

        # Pomodoro tab
        self.pomodoro_widget = PomodoroWidget(self.automation)
        tabs.addTab(self.pomodoro_widget, "Pomodoro")

        # Statistics tab
        statistics = QWidget()
        statistics_layout = QVBoxLayout()
        self.productivity_chart = ProductivityChart()
        statistics_layout.addWidget(self.productivity_chart)
        statistics.setLayout(statistics_layout)
        tabs.addTab(statistics, "Statistics")

        # Achievements tab
        self.achievements_widget = AchievementsWidget()
        tabs.addTab(self.achievements_widget, "Achievements")

        # Settings tab
        settings = QWidget()
        settings_layout = QVBoxLayout()

        # Category settings
        category_group = QGroupBox("App Categories")
        category_layout = QVBoxLayout()

        self.app_category_combo = QComboBox()
        self.app_category_combo.addItems([
            "Productive", "Entertainment", "Social", "Health", "Learning"
        ])

        category_layout.addWidget(QLabel("Select app category:"))
        category_layout.addWidget(self.app_category_combo)

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        category_layout.addWidget(save_button)

        category_group.setLayout(category_layout)
        settings_layout.addWidget(category_group)
        settings.setLayout(settings_layout)

        tabs.addTab(settings, "Settings")

        layout.addWidget(tabs)

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))  # Add your icon file

        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def start_monitoring(self):
        self.worker = AutomationWorker(self.automation)
        self.worker.status_updated.connect(self.update_ui)
        self.worker.start()

    def update_ui(self, stats):
        # Update active apps
        self.active_apps_list.clear()
        self.active_apps_list.addItems(stats['active_apps'])

        # Update progress bars
        # if 'usage_history' in stats:
        #     productive_time = sum(time for app, times in stats['usage_history'].items()
        #                         if self.automation.app_categories.get(app) == "productive")
        #     self.productive_progress.setValue(min(100, (productive_time / self.automation.daily_goals['productive_time']) * 100))

        # Update achievements
        self.achievements_widget.update_achievements(stats['achievements'])

        # Update chart if needed
        if 'usage_history' in stats:
            category_times = {}
            for app, times in stats['usage_history'].items():
                category = self.automation.app_categories.get(app, "Other")
                category_times[category] = category_times.get(category, 0) + sum(times.values())
            self.productivity_chart.update_chart(category_times)

    def save_settings(self):
        # Save current settings to config file
        settings = {
            'app_categories': dict(self.automation.app_categories),
            'daily_goals': dict(self.automation.daily_goals)
        }
        with open('config.json', 'w') as f:
            json.dump(settings, f, indent=4)
        QMessageBox.information(self, "Settings", "Settings saved successfully!")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "App Automation",
            "Application minimized to system tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def quit_application(self):
        self.worker.stop()
        self.worker.wait()
        QApplication.quit()

def main():
    app = QApplication(sys.argv)

    # Create and start automation
    from app_automation import AppAutomation  # Import from your main file
    automation = AppAutomation()

    # Create and show GUI
    window = MainWindow(automation)
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
