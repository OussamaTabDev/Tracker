import pandas as pd
from datetime import datetime
from helpers.settings import SUMMARY_DIR
import os
# Load the CSV file
activity_log = pd.read_csv(f'{SUMMARY_DIR}\Activiy_log_all.csv')

# Convert 'timestamp' column to datetime format
activity_log['timestamp'] = pd.to_datetime(activity_log['timestamp'])

# Extract the date from the timestamp for grouping purposes
activity_log['date'] = activity_log['timestamp'].dt.date

# Define productive vs unproductive keywords
productive_keywords = ['code', 'python', 'studio', 'editor', 'jupyter', 'terminal']
unproductive_keywords = ['youtube', 'game', 'netflix']

# Function to classify activity based on window title
def classify_activity(title):
    title_lower = title.lower()
    if any(keyword in title_lower for keyword in productive_keywords):
        return 'Productive'
    elif any(keyword in title_lower for keyword in unproductive_keywords):
        return 'Unproductive'
    return 'Neutral'

# Apply classification to window titles
activity_log['classification'] = activity_log['window_title'].apply(classify_activity)

# Fill missing durations with 0 for now
activity_log['duration'].fillna(0, inplace=True)

# Group activities by day
daily_activities = activity_log.groupby('date')

# Function to generate daily summary
def generate_daily_summary(date, day_data):
    total_time = day_data['duration'].sum()
    productive_time = day_data.loc[day_data['classification'] == 'Productive', 'duration'].sum()
    unproductive_time = day_data.loc[day_data['classification'] == 'Unproductive', 'duration'].sum()
    neutral_time = day_data.loc[day_data['classification'] == 'Neutral', 'duration'].sum()

    summary = f"Summary for {date}:\n"
    summary += f"Total Time: {total_time/60:.2f} minutes\n"
    summary += f"Productive Time: {productive_time/60:.2f} minutes\n"
    summary += f"Unproductive Time: {unproductive_time/60:.2f} minutes\n"
    summary += f"Neutral Time: {neutral_time/60:.2f} minutes\n"


    # Suggestions
    suggestions = []
    if unproductive_time > productive_time:
        suggestions.append("Try to reduce unproductive activities and allocate more time to productive tasks.")
    if productive_time < 0.5 * total_time:
        suggestions.append("Increase focus time on productive tasks to improve efficiency.")
    if not suggestions:
        suggestions.append("Great job! You're maintaining a good balance between tasks.")

    summary += "\nSuggestions:\n" + "\n".join(suggestions) + "\n"

    return summary

# Function to generate summaries for all days
def generate_all_summaries(activity_log = activity_log):
    summaries = []
    for date, day_data in daily_activities:
        summaries.append(generate_daily_summary(date, day_data))
    return "\n".join(summaries) , summaries

# Get all daily summaries
all_summaries , sum_array = generate_all_summaries(activity_log)
# Ensure the directory exists
os.makedirs(SUMMARY_DIR, exist_ok=True)
# Optionally, save the summary to a text file
with open(f'{SUMMARY_DIR}\daily_summary.txt', 'w', encoding='utf-8') as f:
    f.write(all_summaries)
def automation_log():
    all_summaries , sum_array = generate_all_summaries(activity_log)
    # Ensure the directory exists
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    with open(f'{SUMMARY_DIR}\daily_summary.txt', 'w', encoding='utf-8') as f:
        f.write(all_summaries)
    return  sum_array

def summary_return():
# Print out the summaries to see the output
    sum_array= automation_log()
    return sum_array[len(sum_array) - 2]
