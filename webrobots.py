import requests

# Define the URL of the webpage to scrape
url = "https://www.example.com/"

# Send a GET request to the URL
try:
  response = requests.get(url)
  response.raise_for_status()  # Raise an exception for unsuccessful requests
except requests.exceptions.RequestException as e:
  print(f"An error occurred: {e}")
  exit()

# Extract the webpage content
content = response.text

# Parse the HTML content to extract the title (basic approach)
# Note: This is a simplified approach and may not work for all websites due to HTML structure variations

title_start = content.find("<title>")  # Find the opening title tag
if title_start != -1:
  title_end = content.find("</title>")  # Find the closing title tag
  if title_end != -1:
    title = content[title_start + 7:title_end]  # Extract the title text (excluding tags)
    print(f"Title of the webpage: {title}")
else:
  print("Title not found using this basic approach.")

