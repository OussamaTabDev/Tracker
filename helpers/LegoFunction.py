import time
import psutil
import pygetwindow as gw
from datetime import datetime, time as dt_time
import json
import os
from pathlib import Path
import keyboard
import schedule
from collections import defaultdict
import subprocess
import re
import logging

class AppEvent:
    def __init__(self, app_name, event_type, conditions=None, actions=None):
        self.app_name = app_name
        self.event_type = event_type
        self.conditions = conditions or {}
        self.actions = actions or []
        self.last_trigger_time = 0
        self.counter = 0

class AppAutomation:
    def __init__(self):
        self.active_apps = set()
        self.app_start_times = {}
        self.usage_history = defaultdict(lambda: defaultdict(float))
        self.events = []
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename='app_automation.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def add_event(self, event):
        """Add a new event to monitor"""
        self.events.append(event)
        logging.info(f"Added new event for {event.app_name}: {event.event_type}")

    def check_condition(self, condition, app_name):
        """Check if a condition is met"""
        condition_type = condition.get('type')
        value = condition.get('value')

        if condition_type == 'time_exceeds':
            return self.get_app_runtime(app_name) >= value
        elif condition_type == 'time_between':
            current_time = datetime.now().time()
            start_time = dt_time(*map(int, value[0].split(':')))
            end_time = dt_time(*map(int, value[1].split(':')))
            return start_time <= current_time <= end_time
        elif condition_type == 'day_of_week':
            return datetime.now().strftime('%A').lower() in value
        elif condition_type == 'app_running':
            return value in self.get_running_apps()
        elif condition_type == 'cpu_usage':
            return psutil.cpu_percent() >= value
        elif condition_type == 'memory_usage':
            return psutil.virtual_memory().percent >= value
        elif condition_type == 'keyboard_pressed':
            return keyboard.is_pressed(value)
        return False

    def execute_action(self, action, app_name):
        """Execute the specified action"""
        action_type = action.get('type')
        params = action.get('params', {})

        if action_type == 'close_app':
            self.close_app(app_name)
        elif action_type == 'minimize_app':
            self.minimize_app(app_name)
        elif action_type == 'start_app':
            self.start_app(params.get('path', ''))
        elif action_type == 'send_notification':
            self.send_notification(params.get('message', ''))
        elif action_type == 'play_sound':
            self.play_sound(params.get('sound_file', ''))
        elif action_type == 'take_screenshot':
            self.take_screenshot()
        elif action_type == 'write_log':
            logging.info(params.get('message', ''))
        elif action_type == 'keyboard_shortcut':
            keyboard.press_and_release(params.get('keys', ''))

    def get_running_apps(self):
        """Get list of currently running applications"""
        return {window.title for window in gw.getAllWindows() if window.title}

    def get_app_runtime(self, app_name):
        """Get how long an app has been running in minutes"""
        if app_name in self.app_start_times:
            return (time.time() - self.app_start_times[app_name]) / 60
        return 0

    def close_app(self, app_name):
        """Close specified application"""
        try:
            windows = gw.getWindowsWithTitle(app_name)
            for window in windows:
                window.close()
            logging.info(f"Closed application: {app_name}")
        except Exception as e:
            logging.error(f"Error closing {app_name}: {str(e)}")

    def minimize_app(self, app_name):
        """Minimize specified application"""
        try:
            windows = gw.getWindowsWithTitle(app_name)
            for window in windows:
                window.minimize()
        except Exception as e:
            logging.error(f"Error minimizing {app_name}: {str(e)}")

    def start_app(self, path):
        """Start an application"""
        try:
            subprocess.Popen(path)
            logging.info(f"Started application: {path}")
        except Exception as e:
            logging.error(f"Error starting application: {str(e)}")

    def take_screenshot(self):
        """Take a screenshot"""
        try:
            import pyautogui
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screenshot_{timestamp}.png'
            pyautogui.screenshot(filename)
            logging.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logging.error(f"Error taking screenshot: {str(e)}")

    def send_notification(self, message):
        """Send system notification"""
        try:
            # Platform-specific notification code here
            logging.info(f"Notification sent: {message}")
        except Exception as e:
            logging.error(f"Error sending notification: {str(e)}")

    def play_sound(self, sound_file):
        """Play a sound file"""
        try:
            if os.path.exists(sound_file):
                # Platform-specific sound playing code here
                logging.info(f"Played sound: {sound_file}")
        except Exception as e:
            logging.error(f"Error playing sound: {str(e)}")

    def monitor(self):
        """Main monitoring loop"""
        while True:
            try:
                current_apps = self.get_running_apps()

                # Check for new apps
                for app in current_apps - self.active_apps:
                    self.app_start_times[app] = time.time()
                    self.handle_app_opened(app)

                # Check for closed apps
                for app in self.active_apps - current_apps:
                    self.handle_app_closed(app)

                self.active_apps = current_apps

                # Check all events
                for event in self.events:
                    all_conditions_met = all(
                        self.check_condition(condition, event.app_name)
                        for condition in event.conditions
                    )

                    if all_conditions_met:
                        for action in event.actions:
                            self.execute_action(action, event.app_name)

                time.sleep(1)  # Check every second

            except Exception as e:
                logging.error(f"Error in monitor loop: {str(e)}")
                time.sleep(1)

