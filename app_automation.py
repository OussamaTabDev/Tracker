# import time
# import psutil
# import pygetwindow as gw
# from datetime import datetime, time as dt_time
# import json
# import os
# from pathlib import Path
# import keyboard
# import schedule
# from collections import defaultdict
# import subprocess
# import re
# import logging

# class AppEvent:
#     def __init__(self, app_name, event_type, conditions=None, actions=None):
#         self.app_name = app_name
#         self.event_type = event_type
#         self.conditions = conditions or {}
#         self.actions = actions or []
#         self.last_trigger_time = 0
#         self.counter = 0

# class AppAutomation:
#     def __init__(self):
#         self.active_apps = set()
#         self.app_start_times = {}
#         self.usage_history = defaultdict(lambda: defaultdict(float))
#         self.events = []
#         self.setup_logging()
#         schedule.every().sunday.at("18:00").do(self.weekly_summary)

#     def setup_logging(self):
#         logging.basicConfig(
#             filename='app_automation.log',
#             level=logging.INFO,
#             format='%(asctime)s - %(levelname)s - %(message)s'
#         )

#     def add_event(self, event):
#         """Add a new event to monitor"""
#         self.events.append(event)
#         logging.info(f"Added new event for {event.app_name}: {event.event_type}")

#     def check_condition(self, condition, app_name):
#         """Check if a condition is met"""
#         condition_type = condition.get('type')
#         value = condition.get('value')

#         if condition_type == 'time_exceeds':
#             return self.get_app_runtime(app_name) >= value
#         elif condition_type == 'time_between':
#             current_time = datetime.now().time()
#             start_time = dt_time(*map(int, value[0].split(':')))
#             end_time = dt_time(*map(int, value[1].split(':')))
#             return start_time <= current_time <= end_time
#         elif condition_type == 'day_of_week':
#             return datetime.now().strftime('%A').lower() in value
#         elif condition_type == 'app_running':
#             return value in self.get_running_apps()
#         elif condition_type == 'cpu_usage':
#             return psutil.cpu_percent() >= value
#         elif condition_type == 'memory_usage':
#             return psutil.virtual_memory().percent >= value
#         elif condition_type == 'keyboard_pressed':
#             return keyboard.is_pressed(value)
#         return False

#     def execute_action(self, action, app_name):
#         """Execute the specified action"""
#         action_type = action.get('type')
#         params = action.get('params', {})

#         if action_type == 'close_app':
#             self.close_app(app_name)
#         elif action_type == 'minimize_app':
#             self.minimize_app(app_name)
#         elif action_type == 'start_app':
#             self.start_app(params.get('path', ''))
#         elif action_type == 'send_notification':
#             self.send_notification(params.get('message', ''))
#         elif action_type == 'play_sound':
#             self.play_sound(params.get('sound_file', ''))
#         elif action_type == 'take_screenshot':
#             self.take_screenshot()
#         elif action_type == 'write_log':
#             logging.info(params.get('message', ''))
#         elif action_type == 'keyboard_shortcut':
#             keyboard.press_and_release(params.get('keys', ''))

#     def get_running_apps(self):
#         """Get list of currently running applications"""
#         return {window.title for window in gw.getAllWindows() if window.title}

#     def get_app_runtime(self, app_name):
#         """Get how long an app has been running in minutes"""
#         if app_name in self.app_start_times:
#             return (time.time() - self.app_start_times[app_name]) / 60
#         return 0

#     def close_app(self, app_name):
#         """Close specified application"""
#         try:
#             windows = gw.getWindowsWithTitle(app_name)
#             for window in windows:
#                 window.close()
#             logging.info(f"Closed application: {app_name}")
#         except Exception as e:
#             logging.error(f"Error closing {app_name}: {str(e)}")

#     def minimize_app(self, app_name):
#         """Minimize specified application"""
#         try:
#             windows = gw.getWindowsWithTitle(app_name)
#             for window in windows:
#                 window.minimize()
#         except Exception as e:
#             logging.error(f"Error minimizing {app_name}: {str(e)}")

#     def start_app(self, path):
#         """Start an application"""
#         try:
#             subprocess.Popen(path)
#             logging.info(f"Started application: {path}")
#         except Exception as e:
#             logging.error(f"Error starting application: {str(e)}")

#     def take_screenshot(self):
#         """Take a screenshot"""
#         try:
#             import pyautogui
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#             filename = f'screenshot_{timestamp}.png'
#             pyautogui.screenshot(filename)
#             logging.info(f"Screenshot saved: {filename}")
#         except Exception as e:
#             logging.error(f"Error taking screenshot: {str(e)}")

#     def send_notification(self, message):
#         """Send system notification"""
#         try:
#             logging.info(f"Notification sent: {message}")
#         except Exception as e:
#             logging.error(f"Error sending notification: {str(e)}")

#     def play_sound(self, sound_file):
#         """Play a sound file"""
#         try:
#             if os.path.exists(sound_file):
#                 logging.info(f"Played sound: {sound_file}")
#         except Exception as e:
#             logging.error(f"Error playing sound: {str(e)}")

#     def monitor(self):
#         """Main monitoring loop"""
#         while True:
#             try:
#                 current_apps = self.get_running_apps()

#                 for app in current_apps - self.active_apps:
#                     self.app_start_times[app] = time.time()
#                     self.handle_app_opened(app)

#                 for app in self.active_apps - current_apps:
#                     self.handle_app_closed(app)

#                 self.active_apps = current_apps

#                 for event in self.events:
#                     all_conditions_met = all(
#                         self.check_condition(condition, event.app_name)
#                         for condition in event.conditions
#                     )

#                     if all_conditions_met:
#                         for action in event.actions:
#                             self.execute_action(action, event.app_name)

#                 schedule.run_pending()
#                 time.sleep(1)

#             except Exception as e:
#                 logging.error(f"Error in monitor loop: {str(e)}")
#                 time.sleep(1)

#     def weekly_summary(self):
#         """Log weekly summary of app usage"""
#         productive_apps = ["VSCode", "Excel", "Outlook"]
#         for app, times in self.usage_history.items():
#             total_time = sum(times.values())
#             productive_status = "Productive" if app in productive_apps else "Non-productive"
#             logging.info(f"{app}: {total_time} minutes ({productive_status})")


import time
import psutil
import pygetwindow as gw
from datetime import datetime, time as dt_time, timedelta
import json
import os
from pathlib import Path
import keyboard
import schedule
from collections import defaultdict
import subprocess
import re
import logging
import random
from plyer import notification
import webbrowser
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any

class AppCategories:
    PRODUCTIVE = "productive"
    ENTERTAINMENT = "entertainment"
    SOCIAL = "social"
    HEALTH = "health"
    LEARNING = "learning"

class AppEvent:
    def __init__(self, app_name: str, event_type: str, conditions: Dict = None,
                 actions: List[Dict] = None, category: str = None):
        self.app_name = app_name
        self.event_type = event_type
        self.conditions = conditions or {}
        self.actions = actions or []
        self.last_trigger_time = 0
        self.counter = 0
        self.category = category

class AppAutomation:
    def __init__(self):
        self.active_apps = set()
        self.app_start_times = {}
        self.usage_history = defaultdict(lambda: defaultdict(float))
        self.events = []
        self.pomodoro_active = False
        self.break_time = False
        self.daily_goals = {}
        self.achievements = set()
        self.setup_logging()
        self.load_config()
        self.setup_schedules()

    def setup_logging(self):
        logging_dir = Path("logs")
        logging_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=logging_dir / 'app_automation.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.app_categories = config.get('app_categories', {})
                self.daily_goals = config.get('daily_goals', {})
                self.motivation_quotes = config.get('motivation_quotes', [])
                self.break_activities = config.get('break_activities', [])
        except FileNotFoundError:
            self.create_default_config()

    def create_default_config(self):
        """Create default configuration"""
        default_config = {
            'app_categories': {
                'VSCode': AppCategories.PRODUCTIVE,
                'Excel': AppCategories.PRODUCTIVE,
                'Chrome': AppCategories.LEARNING,
                'Steam': AppCategories.ENTERTAINMENT,
                'Spotify': AppCategories.ENTERTAINMENT
            },
            'daily_goals': {
                'productive_time': 240,  # minutes
                'learning_time': 60,
                'exercise_time': 30
            },
            'motivation_quotes': [
                "Progress is better than perfection",
                "Small steps lead to big changes",
                "You've got this!"
            ],
            'break_activities': [
                "Quick stretch",
                "Deep breathing",
                "Walk around",
                "Drink water",
                "Eye exercises"
            ]
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        self.app_categories = default_config['app_categories']
        self.daily_goals = default_config['daily_goals']
        self.motivation_quotes = default_config['motivation_quotes']
        self.break_activities = default_config['break_activities']

    def setup_schedules(self):
        """Setup scheduled tasks"""
        schedule.every().day.at("09:00").do(self.daily_motivation)
        schedule.every().day.at("22:00").do(self.daily_summary)
        # schedule.every().sunday.at("18:00").do(self.weekly_summary)
        schedule.every(2).hours.do(self.suggest_break)
        # schedule.every().day.at("00:00").do(self.reset_daily_stats)

    def start_pomodoro(self, work_minutes=25, break_minutes=5):
        """Start a Pomodoro timer"""
        self.pomodoro_active = True
        self.send_notification("Pomodoro Started", "Time to focus!")

        # Schedule break
        schedule.every(work_minutes).minutes.do(self.take_break, break_minutes)
        logging.info(f"Started Pomodoro: {work_minutes} minutes work, {break_minutes} minutes break")

    def take_break(self, break_minutes):
        """Handle Pomodoro break"""
        if self.pomodoro_active:
            self.break_time = True
            activity = random.choice(self.break_activities)
            self.send_notification("Break Time!", f"Take a {break_minutes} minute break\nSuggestion: {activity}")

            # Schedule end of break
            schedule.every(break_minutes).minutes.do(self.end_break)

    def end_break(self):
        """End Pomodoro break"""
        self.break_time = False
        if self.pomodoro_active:
            self.send_notification("Break Over", "Back to work!")

    def daily_motivation(self):
        """Send daily motivation notification"""
        quote = random.choice(self.motivation_quotes)
        self.send_notification("Daily Motivation", quote)

    def suggest_break(self):
        """Suggest taking a break based on continuous work time"""
        for app, start_time in self.app_start_times.items():
            if (time.time() - start_time) > 7200:  # 2 hours
                self.send_notification("Take a Break",
                    f"You've been using {app} for 2 hours. Time for a break!")

    def track_achievement(self, achievement):
        """Track user achievements"""
        if achievement not in self.achievements:
            self.achievements.add(achievement)
            self.send_notification("Achievement Unlocked!", achievement)
            logging.info(f"Achievement unlocked: {achievement}")

    def generate_productivity_report(self):
        """Generate detailed productivity report"""
        report_data = defaultdict(float)

        for app, times in self.usage_history.items():
            category = self.app_categories.get(app, "Other")
            report_data[category] += sum(times.values())

        # Create pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(report_data.values(), labels=report_data.keys(), autopct='%1.1f%%')
        plt.title('Time Distribution by Category')
        plt.savefig('productivity_report.png')
        plt.close()

        return report_data

    def daily_summary(self):
        """Generate and send daily summary"""
        report_data = self.generate_productivity_report()

        summary = "Daily Summary:\n"
        for category, minutes in report_data.items():
            goal = self.daily_goals.get(f"{category}_time", 0)
            summary += f"{category}: {minutes:.0f} minutes"
            if goal > 0:
                progress = (minutes / goal) * 100
                summary += f" ({progress:.1f}% of daily goal)"
            summary += "\n"

        self.send_notification("Daily Summary", summary)
        logging.info(f"Daily summary generated: {summary}")

    def handle_app_opened(self, app_name):
        """Handle when an app is opened"""
        category = self.app_categories.get(app_name, "Other")
        self.send_notification("App Tracking", f"Now tracking: {app_name} ({category})")
        logging.info(f"App opened: {app_name} - Category: {category}")

    def suggest_alternatives(self, app_name):
        """Suggest productive alternatives when entertainment apps are used too long"""
        if self.app_categories.get(app_name) == AppCategories.ENTERTAINMENT:
            productive_apps = [app for app, cat in self.app_categories.items()
                             if cat == AppCategories.PRODUCTIVE]
            if productive_apps:
                suggestion = random.choice(productive_apps)
                self.send_notification("Productivity Suggestion",
                    f"Consider switching to {suggestion} for some productive work!")

    def send_notification(self, title, message):
        """Send system notification with improved error handling"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,
                timeout=10,
            )
            logging.info(f"Notification sent: {title} - {message}")
        except Exception as e:
            logging.error(f"Error sending notification: {str(e)}")

    def monitor(self):
        """Enhanced main monitoring loop"""
        try:
            while True:
                current_apps = self.get_running_apps()
                current_time = time.time()

                # Handle app changes
                for app in current_apps - self.active_apps:
                    self.app_start_times[app] = current_time
                    self.handle_app_opened(app)

                for app in self.active_apps - current_apps:
                    self.handle_app_closed(app)

                # Update active apps
                self.active_apps = current_apps

                # Process events
                for event in self.events:
                    self.process_event(event)

                # Check app usage durations
                for app in current_apps:
                    duration = (current_time - self.app_start_times.get(app, current_time)) / 60
                    if duration > 60:  # 1 hour
                        self.suggest_alternatives(app)

                # Run scheduled tasks
                schedule.run_pending()

                # Check achievement conditions
                self.check_achievements()

                time.sleep(1)

        except Exception as e:
            logging.error(f"Error in monitor loop: {str(e)}")
            self.send_notification("Error", "App monitoring encountered an error. Check logs.")
            raise

    def check_achievements(self):
        """Check and award achievements"""
        productive_time = sum(self.usage_history[app].get(datetime.now().date(), 0)
                            for app, category in self.app_categories.items()
                            if category == AppCategories.PRODUCTIVE)

        if productive_time > 240:  # 4 hours
            self.track_achievement("Productivity Master: 4 hours of productive work!")

        if len(self.active_apps) == 0 and time.time() - max(self.app_start_times.values(), default=0) > 3600:
            self.track_achievement("Digital Detox: 1 hour without active apps!")
