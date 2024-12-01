import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import calendar
import schedule
import time
# Define your paths
documents_path = Path(os.path.expanduser("Documents"))

# Function to get the list of folders based on YYYY-MM-DD format
def get_date_folders(documents_path, method="d"):
    if method == "d":
        # Get and sort folders by date (YYYY-MM-DD)
        folders = [f for f in documents_path.iterdir() if f.is_dir() and is_date_folder(f.name)]
        return sorted(folders, key=lambda x: datetime.strptime(x.name, "%Y-%m-%d"))

    elif method == "m":
        # Get and sort 10-day period folders by extracting the start date from the folder name
        folders = [f for f in documents_path.iterdir() if f.is_dir() and f.name.startswith("10_days_")]
        def extract_start_date(folder_name):
            try:
                # Extract start date from the folder name
                return datetime.strptime(folder_name.split("_")[2], "%Y-%m-%d")
            except (IndexError, ValueError):
                return datetime.min  # Fallback if the name format is unexpected
        return sorted(folders, key=lambda x: extract_start_date(x.name))

    elif method == "y":
        # Get and sort month folders by month (YYYY-MM)
        folders = [f for f in documents_path.iterdir() if f.is_dir() and f.name.startswith("month_")]
        return sorted(folders, key=lambda x: datetime.strptime(x.name, "month_%Y-%m"))



# Check if the folder name matches the YYYY-MM-DD format
def is_date_folder(folder_name):
    try:
        datetime.strptime(folder_name, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Function to generate a unique folder name if the folder already exists
def get_unique_folder_name(base_path):
    if not base_path.exists():
        return base_path
    counter = 1
    while True:
        new_path = base_path.with_name(f"{base_path.name}_{counter}")
        if not new_path.exists():
            return new_path
        counter += 1

# Function to group folders into periods of 10 days, considering incomplete periods
def group_folders_by_days(folders,  group_name_format):
    start_date = None
    current_group = []

    for folder in folders:
        folder_date = datetime.strptime(folder.name, "%Y-%m-%d")
        # print(folder_date)
        delta_days = get_part_of_month(folder_date.year , folder_date.month, folder_date.day)
        # print(delta_days)
        if start_date is None:
            start_date = folder_date
            current_group.append(folder)
        elif (folder_date - start_date).days < delta_days:
            current_group.append(folder)
        else:
            if (folder_date - start_date).days >= delta_days:
                # Group the current set of folders
                group_folder_name = documents_path / group_name_format.format(start_date.strftime("%Y-%m-%d"), current_group[-1].name)
                unique_folder_name = get_unique_folder_name(group_folder_name)
                os.makedirs(unique_folder_name, exist_ok=True)
                for f in current_group:
                    shutil.move(str(f), unique_folder_name)

            # Reset for the next group
            start_date = folder_date
            current_group = [folder]

    # Handle the last group
    if current_group:
        group_folder_name = documents_path / group_name_format.format(start_date.strftime("%Y-%m-%d"), current_group[-1].name)
        unique_folder_name = get_unique_folder_name(group_folder_name)
        os.makedirs(unique_folder_name, exist_ok=True)
        for f in current_group:
            shutil.move(str(f), unique_folder_name)


# Grouping every 10 days
def get_part_of_month(year, month, day):
    # Get the number of days in the month
    num_days = calendar.monthrange(year, month)[1]
    # print(num_days)
    # Calculate the size of each part
    part_size = num_days // 3


    # Determine the days for each part
    part1_end = part_size
    part2_end = part_size * 2
    part3_end = num_days - (part_size * 2)

    # Determine which part the day falls into
    if day <= part1_end:
        return part_size
    elif day <= part2_end:
        return part_size
    else:
        return part3_end

def extract_date_from_folder(folder_name):
    try:
        # Parse the folder name to extract the date
        date = datetime.strptime(folder_name, '%Y-%m-%d')
        return date.year, date.month, date.day
    except ValueError:
        raise ValueError("Folder name must be in the format YYYY-MM-DD")

def group_by_10_days(folders):
    # print(folders)
    group_folders_by_days(folders, "10_days_{}_to_{}")

# Grouping by months
def group_by_month(folders):
    grouped = {}
    all_months = set()

    for folder in folders:
        # Extract start date from the folder name
        try:
            start_date_str = folder.name.split("_")[2]  # "10_days_YYYY-MM-DD_to_YYYY-MM-DD"
            folder_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except (IndexError, ValueError):
            continue  # Skip folders with unexpected names

        month_start = folder_date.replace(day=1)
        month_str = month_start.strftime("%Y-%m")
        all_months.add(month_str)
        if month_str not in grouped:
            grouped[month_str] = []
        grouped[month_str].append(folder)

    # Ensure all months are handled
    for month in sorted(all_months):
        group_folder_name = documents_path / f"month_{month}"
        unique_folder_name = get_unique_folder_name(group_folder_name)
        os.makedirs(unique_folder_name, exist_ok=True)
        if month in grouped:
            for folder in grouped[month]:
                shutil.move(str(folder), unique_folder_name)
# Grouping by years
def group_by_year(folders):
    grouped = {}
    all_years = set()

    for folder in folders:
        try:
            # Extract year from the folder name
            year_str = folder.name.split("_")[1]  # "month_YYYY-MM"
            year = datetime.strptime(year_str, "%Y-%m").strftime("%Y")
        except (IndexError, ValueError):
            continue  # Skip folders with unexpected names

        all_years.add(year)
        if year not in grouped:
            grouped[year] = []
        grouped[year].append(folder)

    # Ensure all years are handled
    for year in sorted(all_years):
        group_folder_name = documents_path / f"year_{year}"
        unique_folder_name = get_unique_folder_name(group_folder_name)
        os.makedirs(unique_folder_name, exist_ok=True)
        if year in grouped:
            for folder in grouped[year]:
                shutil.move(str(folder), unique_folder_name)
# Automated task to run at the end of each period
def run_automation_monthly():
     if datetime.now().day == 1:
        folders = get_date_folders(documents_path, "d")
        group_by_10_days(folders)  # Group by 10 days first
        folders = get_date_folders(documents_path, "m")  # Refresh list of folders
        group_by_month(folders)  # Then group by month

def run_automation_yearly():
    if datetime.now().month == 1 and datetime.now().day == 1:
        folders = get_date_folders(documents_path, "y")  # Refresh list of folders
        group_by_year(folders)  # Finally, group by year


# Run the automation on the first day of the month at 00:01

# Schedule the monthly automation (runs daily, checks if it's the first day)
def schedule_monthly():
    schedule.every().day.at("00:01").do(run_automation_monthly)

# Schedule the yearly automation (runs daily, checks if it's the first day of the year)
def schedule_yearly():
    schedule.every().day.at("00:02").do(run_automation_yearly)

# Function to run the scheduled tasks

def run_scheduler():
    schedule_monthly()
    schedule_yearly()

    while True:
        schedule.run_pending()
        time.sleep(600)  # Check every 10 minutes

# Start scheduling in a separate thread

if __name__ == "__main__":
    run_scheduler()
