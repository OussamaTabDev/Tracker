import threading
from helpers.AppMonitor import AppMonitor
from helpers.ModernGUI import ModernGUI
from helpers.ActivityClassifier import ActivityClassifier
import customtkinter as ctk
from helpers.orgonizer import  run_scheduler
# from helpers.login import LoginApp as login_app
# from helpers import *
# from login import LoginApp as login_app
def start_scheduler_in_thread():
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Allows the thread to close when the main program exits
    scheduler_thread.start()

if __name__ == "__main__":
    # if login_app.is_user_logged_in():
        start_scheduler_in_thread()  # Start the scheduler in a background thread
        monitor = AppMonitor()
        app = ModernGUI(monitor)
    # else:
    #     app = login_app()  # Show the login interface
        app.mainloop()
