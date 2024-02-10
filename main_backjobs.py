# import subprocess module
import subprocess
import sys

print("Starting to Fetch News...\n")

print("Fetching News in Science Alert...\n")
subprocess.run([sys.executable, "webScraping\sciencealert_ws.py"])

print("\n" + "-"*100)
print("Fetching News in Space News...\n")
subprocess.run([sys.executable, "webScraping\spacenews_ws.py"])

print("\n" + "-"*100)
print("Fetching News in Motorsports...\n")
subprocess.run([sys.executable, "webScraping\motorsport_ws.py"])


# And new websites before this line ^
# Adding summaries
print("\n" + "-"*100)
print("Adding summaries of news...\n")
subprocess.run([sys.executable, "contentProcessing\summurization.py"])

print("\nNews Fetching end.\n")