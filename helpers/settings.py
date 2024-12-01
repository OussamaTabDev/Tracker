import customtkinter as ctk
from PIL import Image
from tksvg import SvgImage
import os
app_name = "PM Orgonizer"

# Get the path to the user's Documents folder
documents_dir = os.path.join(os.environ['USERPROFILE'], 'Documents')
backup_dir = os.path.join(documents_dir, app_name, "Backup")

# Define the screenshot directory
default_app = "System"
SCREENSHOT_DIR = os.path.join(documents_dir, app_name)
SUMMARY_DIR = os.path.join(documents_dir, app_name, "Summary")
non_relevant_apps = os.path.join(documents_dir, app_name, "non_relevant_apps.csv")
# Create the directory if it doesn't exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

#set the database file
DATABASE_FILE = "helpers/sources/activity_log.db"

# Red , Green , Blue , pr color , sc color
RED = (255, 0, 0)
GREEN = (0 , 255 , 0)
BLUE = (0, 0, 255)
CUSTOM_COLOR_PR_Dark = (0, 255, 255)
CUSTOM_COLOR_SC_Dark = (100, 255, 10 )
CUSTOM_COLOR_PR_Light = (0, 255, 255)
CUSTOM_COLOR_SC_light = (100, 255, 10 )
Hover_color_dark = "#1f1f1f"
Hover_color_light = "#303030"
# Define the SVG paths with keys for each icon
#width and hight of svg = 400 px , with scale of 0.05 , w , h = 20 px
img_paths = {
    "arrow-lt-dark": "helpers/sources/assets/svg_icons/arrow_left_dark.svg",
    "arrow-lt-light": "helpers/sources/assets/svg_icons/arrow_left_light.svg",
    "arrow-rt-dark": "helpers/sources/assets/svg_icons/arrow_right_dark.svg",
    "arrow-rt-light": "helpers/sources/assets/svg_icons/arrow_right_light.svg",
    "check-circle-dark": "helpers/sources/assets/svg_icons/check_circle_dark.svg",
    "check-circle-light": "helpers/sources/assets/svg_icons/check_circle_light.svg",
    "check-dark": "helpers/sources/assets/svg_icons/check_dark.svg",
    "check-light": "helpers/sources/assets/svg_icons/check_light.svg",
    "pause-dark": "helpers/sources/assets/svg_icons/pause_dark.svg",
    "pause-light": "helpers/sources/assets/svg_icons/pause_light.svg",
    "play-dark": "helpers/sources/assets/svg_icons/play_dark.svg",
    "play-light": "helpers/sources/assets/svg_icons/play_light.svg",
    "rewind-lt-dark": "helpers/sources/assets/svg_icons/rewind_left_dark.svg",
    "rewind-lt-light": "helpers/sources/assets/svg_icons/rewind_left_light.svg",
    "rewind-rt-dark": "helpers/sources/assets/svg_icons/rewind_right_dark.svg",
    "rewind-rt-light": "helpers/sources/assets/svg_icons/rewind_right_light.svg",
    "skip-dark": "helpers/sources/assets/svg_icons/skip_dark.svg",
    "skip-light": "helpers/sources/assets/svg_icons/skip_light.svg",
    "reset-dark": "helpers/sources/assets/svg_icons/reset_dark.svg",
    "reset-light": "helpers/sources/assets/svg_icons/reset_light.svg",
    "add-dark": "helpers/sources/assets/svg_icons/add_dark.svg",
    "add-light": "helpers/sources/assets/svg_icons/add_light.svg",
    "edit-dark": "helpers/sources/assets/svg_icons/edit_dark.svg",
    "edit-light": "helpers/sources/assets/svg_icons/edit_light.svg",
    "delete-dark": "helpers/sources/assets/svg_icons/delete_dark.svg",
    "delete-light": "helpers/sources/assets/svg_icons/delete_light.svg",
    "archive-dark": "helpers/sources/assets/svg_icons/archive_dark.svg",
    "archive-light": "helpers/sources/assets/svg_icons/archive_light.svg",
    "offline-light": "helpers/sources/assets/svg_icons/offline_light.svg",
    "offline-dark": "helpers/sources/assets/svg_icons/offline_dark.svg",
    "online-dark": "helpers/sources/assets/svg_icons/online_dark.svg",
    "online-light": "helpers/sources/assets/svg_icons/online_light.svg",
    "save-dark": "helpers/sources/assets/svg_icons/save_dark.svg",
    "save-light": "helpers/sources/assets/svg_icons/save_light.svg",
    "box-ok-light": "helpers/sources/assets/svg_icons/box_ok_light.svg",
    "box-ok-dark": "helpers/sources/assets/svg_icons/box_ok_dark.svg",
    "box-search-dark": "helpers/sources/assets/svg_icons/box_search_dark.svg",
    "box-search-light": "helpers/sources/assets/svg_icons/box_search_light.svg",
    "box-delete-dark": "helpers/sources/assets/svg_icons/box_delete_dark.svg",
    "box-delete-light": "helpers/sources/assets/svg_icons/box_delete_light.svg",
    "box-add-dark": "helpers/sources/assets/svg_icons/box_add_dark.svg",
    "box-add-light": "helpers/sources/assets/svg_icons/box_add_light.svg",
    "sm-arrow-left-light": "helpers/sources/assets/svg_icons/sm_arrow_left_light.svg",
    "sm-arrow-right-dark": "helpers/sources/assets/svg_icons/sm_arrow_right_dark.svg",
    "sm-arrow-right-light": "helpers/sources/assets/svg_icons/sm_arrow_right_light.svg",
    "happy-light": "helpers/sources/assets/svg_icons/happy_light.svg",
    "normal-dark": "helpers/sources/assets/svg_icons/normal_dark.svg",
    "normal-light": "helpers/sources/assets/svg_icons/normal_light.svg",
    "sad-dark": "helpers/sources/assets/svg_icons/sad_dark.svg",
    "sad-light": "helpers/sources/assets/svg_icons/sad_light.svg",
    "sm-arrow-left-dark": "helpers/sources/assets/svg_icons/sm_arrow_left_dark.svg",
    "happy-dark": "helpers/sources/assets/svg_icons/happy_dark.svg",
    "chart-dark": "helpers/sources/assets/svg_icons/chart_dark.svg",
    "chart-light": "helpers/sources/assets/svg_icons/chart_light.svg",
    "chart2-dark": "helpers/sources/assets/svg_icons/chart2_dark.svg",
    "chart2-light": "helpers/sources/assets/svg_icons/chart2_light.svg",
    "refresh-light": "helpers/sources/assets/svg_icons/refresh-light.svg",
    "refresh-dark": "helpers/sources/assets/svg_icons/refresh-dark.svg",

}
# def create_svg_images(img_paths ):
# # Loop through img_paths and create SvgImage objects, storing them in the dictionary
#     svgs = {}

#     for key, path in img_paths.items():
#         svgs[key] = SvgImage(file=path, scale=0.05)  # Adjust scale as needed
#     # Adjust scale to resize the SVG

#     return svgs


notifications_1_3 = [
    "You've completed 1/3 of your task. Great job! Take a moment to refocus.",
    "Well done! You're 1/3 of the way through. Keep up the momentum!",
    "Good progress—1/3 of the way done. Stay on track for continued success.",
    "Excellent start! You're 1/3 through. Continue pushing forward!",
    "You're 1/3 through! Keep that energy up and power through the rest!",
    "Nice work! You're already 1/3 done. Stay focused and keep going!",
    "Great progress! You've hit the 1/3 mark—keep moving forward!",
    "1/3 complete! Take a quick breath and push on to the finish line!",
    "Awesome! You're 1/3 of the way there. Stay sharp and keep working!",
    "You're 1/3 in! Keep that steady pace to finish strong!",
    "Well done! You've crossed the 1/3 point. Stay determined!",
    "Great going—1/3 of the task is done! Keep up the good work!",
    "1/3 complete! You're making excellent progress. Stay focused!",
    "You’re doing great! 1/3 of the way done. Keep the momentum going!",
    "Fantastic job! You're 1/3 through your task. Stay on course!",
    "You're on a roll! 1/3 finished—keep pushing toward success!",
    "Impressive! You've knocked out 1/3 of the task. Keep at it!",
    "Nice going! You've reached the 1/3 mark. Keep the progress steady!",
    "You're cruising—1/3 completed! Stay motivated and finish strong!",
    "1/3 down! You're making solid progress—keep the momentum alive!",
    "Great job so far—1/3 complete. Focus on that final push!",
    "You've completed 1/3—awesome! Keep up the focus and determination!",
    "You've reached 1/3 completion. Keep pushing and stay on track!",
    "You're 1/3 of the way done! Take pride in your progress and keep going!",
]
notifications_2_3 = [
    "You've completed 2/3 of your task. Great progress! Stay focused!",
    "You're 2/3 of the way there. Keep pushing forward!",
    "2/3 of the way there, You’re there, stay determined!",
    "Fantastic work—2/3 complete. Keep up the good work!",
    "Almost there! You're 2/3 done. Finish strong!",
    "Almost there! You're 2/3 done. Just a little more effort!",
    "You're 2/3 done, You’re doing great, just one more push!",
    "Great job! 2/3 done—just one final push to the finish!",
    "You're almost at the finish line! 2/3 completed, keep going!",
    "You've reached 2/3! Stay focused and finish strong!",
    "2/3 complete! You're so close—keep up the hard work!",
    "You're doing amazing—2/3 of the task is complete! Almost there!",
    "Just a little more to go! 2/3 finished, keep the energy high!",
    "2/3 of the task is done! Stay motivated for the final stretch!",
    "You’re nearly there—2/3 complete. Keep pushing to the end!",
    "You're 2/3 of the way through! Keep that momentum going!",
    "Fantastic progress! You've completed 2/3—stay focused on the goal!",
    "You're almost done! Just 1/3 to go—stay sharp!",
    "You’ve made it 2/3 of the way! Keep pushing toward success!",
    "Just a little more! 2/3 completed—finish strong!",
    "2/3 done—amazing work! Don’t stop now!",
    "Great effort so far—2/3 complete. Keep your focus for the final part!",
    "You’re close to the finish line! 2/3 is complete—keep going!",
    "You've got this! 2/3 of your task is done—finish it off!",
    "Stay determined! You're 2/3 of the way there—keep going!",
    "Incredible progress—2/3 done! Keep pushing for the finish!",
    "2/3 complete! The end is in sight—keep up the pace!",
]
notifications_3_3 = [
    "Congratulations! You've completed all tasks.",
    "Excellent job—task completed successfully!",
    "You’ve reached the finish line. Well done!",
    "All tasks are done. Great work!",
    "Excellent! You’ve finished your task successfully!",
    "Awesome work, task completed!",
    "Well done! You’ve reached your goal.",
    "Fantastic job! You’ve made it, time to celebrate!",
    "Amazing! You've completed all your tasks—fantastic work!",
    "All done! You've successfully finished your tasks. Great job!",
    "Task complete! Well done on seeing it through to the end!",
    "You’ve achieved your goal—excellent work!",
    "Great effort! You've finished all tasks—time to celebrate!",
    "Fantastic! Every task is done—take pride in your accomplishment!",
    "Well done! You've completed all your tasks with flying colors!",
    "Awesome! All tasks are finished—enjoy the satisfaction of a job well done!",
    "Congratulations on completing all tasks—brilliant work!",
    "You’ve successfully finished! Time to relax and enjoy your achievement!",
]
notifications_over = [
    "You’ve been working hard! A quick break will help you recharge.",
    " It’s time to give your mind and body a break—step away for a few minutes.",
    "You’ve been on the PC for a while. A short break will boost your focus!",
    "You’ve done a lot. Step away and come back refreshed.",
    "Continuous work can drain you. A little rest will make you more productive!",
    "You’ve been using the PC for quite a while. Step away, refresh, and come back stronger.",
    "You’ve been at it for too long. Take a break before continuing!",
    "Your mind deserves a rest! Come back with a fresh perspective after a short break.",
    "You've been working hard—take a short break to recharge your energy!",
    "Time to step away for a bit—your mind will thank you for the break!",
    "A well-earned break will boost your productivity—step away for a few minutes!",
    "Great work so far! Give yourself a quick break to stay at your best.",
    "Take a breather! A little rest will help you stay focused and sharp.",
    "You've been at it for a while—refresh your mind with a quick break!",
    "Time to pause! A short break will leave you feeling more energized.",
    "Step away for a moment—rest now, and you'll come back even stronger!",
    "You deserve a break—relax for a bit and return refreshed.",
    "A quick break will do wonders for your focus—step away and recharge!",
]
