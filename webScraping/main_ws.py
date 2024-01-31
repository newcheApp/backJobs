# import subprocess module
import subprocess
import sys

print("Starting to Fetch News.\n")

print("Fetching News in Science Alert.\n")
subprocess.run([sys.executable, "webScraping\sciencealert_ws.py"])

print("\n" + "-"*100)
print("Fetching News in Space News.\n")
subprocess.run([sys.executable, "webScraping\spacenews_ws.py"])

print("\nNews Fetching end.\n")