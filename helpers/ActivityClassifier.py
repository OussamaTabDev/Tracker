import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
from helpers.settings import *
import csv
from collections import Counter
from typing import List, Tuple, Dict
import csv
from itertools import combinations
class ActivityClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB()
        self.data_file = "helpers/sources/activity_training_data.csv"
        # self.data_file = "helpers/sources/activity_training_data_website.csv"
        self.train_classifier()
        self.categories = None

    def get_classifications(self):
        if os.path.exists(self.data_file):
            try:
                data = pd.read_csv(self.data_file)
                if data.empty:
                    raise pd.errors.EmptyDataError
            except pd.errors.EmptyDataError:
                print("Training data file is empty. Creating a basic training set.")
                data = self.create_basic_training_data()
        else:
            print("Training data file not found. Creating a basic training set.")
            data = self.create_basic_training_data()

        # Ensure all classifications are treated as categories
        data['classification'] = data['classification'].astype('category')

        # Train the classifier
        X = self.vectorizer.fit_transform(data["window_title"])
        y = data["classification"]
        self.categories = data['classification'].unique()
        return self.categories
    def train_classifier(self):
        if os.path.exists(self.data_file):
            try:
                data = pd.read_csv(self.data_file)
                if data.empty:
                    raise pd.errors.EmptyDataError
            except pd.errors.EmptyDataError:
                print("Training data file is empty. Creating a basic training set.")
                data = self.create_basic_training_data()
        else:
            print("Training data file not found. Creating a basic training set.")
            data = self.create_basic_training_data()

        # Ensure all classifications are treated as categories
        data['classification'] = data['classification'].astype('category')

        # Train the classifier
        X = self.vectorizer.fit_transform(data["window_title"])
        y = data["classification"]
        self.categories = data['classification'].unique()

        # Use a classifier that can handle new classes
        from sklearn.multiclass import OneVsRestClassifier
        from sklearn.svm import LinearSVC
        self.classifier = OneVsRestClassifier(LinearSVC(random_state=0))

        self.classifier.fit(X, y)
        print(f"Classifier trained with {len(data)} records.")
        print(f"Classifications: {data['classification'].unique()}")
        print(self.categories)
        # Evaluate classifier accuracy
        self.evaluate_classifier(X, y)

    def create_basic_training_data(self):
        """Create a basic training dataset if no data is available."""
        data = pd.DataFrame({
            "window_title": [
                'Microsoft Word', 'Google Chrome','ppp5' ,'Visual Studio Code',
                'YouTube', 'Netflix', 'Slack',
                'Outlook', 'Excel', 'PowerPoint',
                'Steam', 'Epic Games', 'Spotify' ,'Microsoft Store',
            ],
            "classification": [
                "Productive", "Neutral", "poisoned",  "Productive",
                "Unproductive", "Unproductive", "Neutral",
                "Productive", "Productive", "Productive",
                "Unproductive", "Unproductive", "Neutral",
                "Unproductive",
            ]
        })
        data.to_csv(self.data_file, index=False)
        print(f"Basic training set created and saved to '{self.data_file}'.")
        return data

    #need some work on it for
    def is_relevant_activity(self, window_title, file="helpers/sources/activity_training_data.csv"):
        # Check if the window title is present in the exported titles
        for prefix in self.export_window_titles_to_array(file).keys():
            # print(prefix)
            if window_title in prefix:
                return True

        # If not relevant, add the window title to non-relevant apps
        self.add_non_relevant_app(window_title, non_relevant_apps)

        # Clean duplicate entries in the CSV
        self.clean_duplicates_in_csv(non_relevant_apps)

        return False

    def add_non_relevant_app(self, window_title, file_path):
        """Appends the window title to the non-relevant apps CSV."""
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([window_title])

    def clean_duplicates_in_csv(self, file_path):
        """Removes duplicates from the given CSV, keeping only the latest occurrence."""
        unique_entries = {}

        # Read the CSV file
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Assuming the first row is the header
            rows = list(reader)

        # Keep only the latest occurrence of each task
        for row in rows:
            task_name = row[0]  # Assuming task/window name is in the first column
            unique_entries[task_name] = row  # Keep the latest occurrence (overwrites older ones)

        # Write the cleaned data back to the CSV (preserving header)
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Write the header
            writer.writerows(unique_entries.values())

    def classify_activity(self, window_title , file = "helpers/sources/activity_training_data.csv"):
        if file == "helpers/sources/activity_training_data.csv":
            window_title = self.preprocess_window_title(window_title)

        X = self.vectorizer.transform([window_title])

        # Predict the classification
        prediction = self.classifier.predict(X)
        return prediction[0]

    def export_window_titles_to_array(self , csv_file):
        classification_map = {}
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                window_title, classification = row
                classification_map[window_title.strip('"')] = classification
        return classification_map

    def remove_custom_classification(self, window_title):
        print(self.custom_classifications)
        if window_title in self.custom_classifications:
            del self.custom_classifications[window_title]
            # If you're storing classifications in a file or database, update it here
            self.save_custom_classifications()

    def preprocess_window_title(self, window_title, default_classification="Unknown"):
        # Load the classification map from the file
        classification_map = self.export_window_titles_to_array(self.data_file)

        # Find common prefixes
        old_window_title = window_title
        # Split window title into parts using " - " as a separator if present
        if " - " in window_title:
            parts = [part.strip() for part in window_title.split(" - ")]
        else:
            parts = [window_title.strip()]

        app = None
        classifications = []

        # Iterate over each part to find classifications
        for part in parts:
            # Split part into individual words
            key_parts = part.split()

            all_combinations = []
            for i in range(1, len(key_parts) + 1):
                # Generate combinations of different lengths
                for combo in combinations(key_parts, i):
                    # Join the words to form a phrase and add to list
                    all_combinations.append(" ".join(combo))

            # Check all combinations in classification map
            matched_classification = default_classification
            for combo in all_combinations:
                if combo in classification_map:
                    matched_classification = classification_map[combo]
                    if app is None:
                        app = combo  # Set app based on the first matched combination
                    break  # Stop if we found a match

            classifications.append(matched_classification)
            # print(f"Part: {part}, Classification: {matched_classification}")
        # print(f"Preprocessed window title: {app}")
        # pr
        if app is None:
            app = default_app
            # If not relevant, add the window title to non-relevant apps
            self.add_non_relevant_app(old_window_title, non_relevant_apps)
            # Clean duplicate entries in the CSV
            self.clean_duplicates_in_csv(non_relevant_apps)
        return app



    def clean_duplicates_inplace(self):
        window_data = {}

        # Read the CSV file and keep only the latest classification
        with open(self.data_file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                window_title = row['window_title'].strip('"')  # Remove surrounding quotes if present
                classification = row['classification']
                window_data[window_title] = classification

        # Write the cleaned data back to the same file
        with open(self.data_file, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['window_title', 'classification']
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(fieldnames)  # Write the header row

            # Write the cleaned data
            for window_title, classification in window_data.items():
                formatted_entry = f'"{window_title}",{classification}'
                outfile.write(formatted_entry + '\n')

    def add_custom_classification(self, window_title, classification  , file = 'helpers/sources/activity_training_data.csv'):
        """Add a custom classification and retrain the classifier."""
        # print(window_title, classification ,file )
        try:
            data = pd.read_csv(file)
            new_data = pd.DataFrame({"window_title": [window_title], "classification": [classification]})
            data = pd.concat([data, new_data], ignore_index=True)

            # Format the new entry as '"window_title",classification'
            formatted_entry = f'"{window_title}",{classification}'

            # Append the formatted entry to the CSV file
            with open(file, 'a', newline='') as f:
                f.write(formatted_entry + '\n')

            print(f"Added custom classification: {formatted_entry}. Retraining classifier...")
            self.train_classifier()
        except Exception as e:
            print(f"Error adding custom classification: {e}")

    def evaluate_classifier(self, X, y):
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # Train the classifier on the training set
        self.classifier.fit(X_train, y_train)
        # Predict on the test set
        y_pred = self.classifier.predict(X_test)
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Classifier accuracy: {accuracy * 100:.2f}%")

    #untill now not working (setting import and export datasets to the same file)
    def export_training_data(self, export_file="exported_training_data.csv"):
        import shutil
        """Export the training data to a CSV file."""
        try:
            path_file = os.path.join(backup_dir, export_file)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            # Copy the data to a CSV file
            shutil.copyfile(self.data_file, path_file)
            return (True , "")
        except Exception as e:
            return (False , e)
    def import_training_data(self, import_file):
        """Import training data from a CSV file and retrain the classifier."""
        try:
            new_data = pd.read_csv(import_file)
            data = pd.read_csv(self.data_file)
            data = pd.concat([data, new_data], ignore_index=True)
            data.drop_duplicates(subset=['window_title'], inplace=True)
            data.to_csv(self.data_file, index=False)
            print(f"Imported training data from '{import_file}'. Retraining classifier...")
            self.train_classifier()
        except Exception as e:
            print(f"Error importing training data: {e}")
        # Replace the old file with the new one
        os.replace(import_file, self.data_file)

    def delete_windows(self , window_tile_selected , file= 'helpers/sources/activity_training_data.csv'):
        window_data = {}

        # Read the CSV file and keep only the latest classification
        with open(file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row['window_title'].strip('"') != window_tile_selected:
                    window_title = row['window_title'].strip('"')  # Remove surrounding quotes if present
                    classification = row['classification']
                    window_data[window_title] = classification

        # Write the cleaned data back to the same file
        with open(file, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['window_title', 'classification']
            writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(fieldnames)  # Write the header row

            # Write the cleaned data
            for window_title, classification in window_data.items():
                formatted_entry = f'"{window_title}",{classification}'
                outfile.write(formatted_entry + '\n')
