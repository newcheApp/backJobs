import subprocess
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for development and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def fetch_news_from_directory(directory_path):
    directory_path = resource_path(directory_path)
    print("> Starting to Fetch News...\n")

    # Iterate over the files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".py"):  # Check if the file is a Python file
            file_path = os.path.join(directory_path, filename)
            print(f"\n{'-'*100}\n> Fetching News from {filename}...\n")
            
            # Run the Python script
            subprocess.run([sys.executable, file_path])

# Main execution starts here
if __name__ == "__main__":
    fetch_news_from_directory("webScraping")

    # Adding summaries
    print("\n" + "-"*100)
    print("\n> Adding summaries of news...\n")
    subprocess.run([sys.executable, resource_path("contentProcessing/summurization.py")])

    print("\n> Tagger started...")
    subprocess.run([sys.executable, resource_path("contentProcessing/tagger/tagger_runner.py")])

    print("\n> Mover started...")
    subprocess.run([sys.executable, resource_path("contentProcessing/news_mover.py")])

    print("\n> News Fetching end...")
    print("\n> End of Back Processes...")
