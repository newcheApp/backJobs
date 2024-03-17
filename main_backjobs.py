# import subprocess module
import subprocess
import sys
import os

def fetch_news_from_directory(directory_path):
    print("> Starting to Fetch News...\n")

    # Iterate over the files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".py"):  # Check if the file is a Python file
            file_path = os.path.join(directory_path, filename)
            print(f"\n{'-'*100}\n> Fetching News from {filename}...\n")
            
            # Run the Python script
            subprocess.run([sys.executable, file_path])

fetch_news_from_directory("webScraping")

# And new websites before this line ^
# Adding summaries
print("\n" + "-"*100)
print("\n> Adding summaries of news...\n")
subprocess.run([sys.executable, "contentProcessing/summurization.py"])
print("\n> Tagger started...")
subprocess.run([sys.executable, "contentProcessing/tagger/tagger_runner.py"])
print("\n> Mover started...")
subprocess.run([sys.executable, "contentProcessing/news_mover.py"])

print("\n> News Fetching end...")
print("\n> End of Back Processes...")