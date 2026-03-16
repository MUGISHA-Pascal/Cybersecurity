from urllib.robotparser import RobotFileParser

def analyze_robots_txt(url, user_agent="*"):
  """
  Analyzes a robots.txt file and prints information for the specified user agent.

  Args:
      url (str): The URL of the website containing the robots.txt file.
      user_agent (str, optional): The user agent string (defaults to "*").
  """

  # Create a RobotFileParser object
  parser = RobotFileParser()

  # Set the URL of the robots.txt file
  parser.set_url(f"{url}/robots.txt")

  # Read the robots.txt file
  try:
    parser.read()
  except Exception as e:
    print(f"An error occurred while reading robots.txt: {e}")
    return

  # Check if the user agent is allowed to access the root path
  can_fetch = parser.can_fetch(user_agent, "/")

  # Print analysis results
  print(f"URL: {url}")
  print(f"User-Agent: {user_agent}")
  print(f"Can access root path: {can_fetch}")

  # Optionally, explore other functionalities of the RobotFileParser object
  # You can check if specific URLs are allowed/disallowed for the user agent

if __name__ == "__main__":
  # Example usage
  website_url = "https://www.example.com"
  analyze_robots_txt(website_url)

  # Analyze for a specific user agent (e.g., Googlebot)
  analyze_robots_txt(website_url, user_agent="Googlebot")
