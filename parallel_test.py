# scrape_multiple_videos.py

import test  # Import the test.py module
import json
import re
import os

# List of YouTube URLs to scrape
video_urls = [
    "https://youtu.be/5bevi_0v6wU?si=MTxFF2cLfBob8GBB",
    "https://youtu.be/jac53THxO0I?si=CgDkWDVJhcaScJog",
    "https://youtu.be/1s9Vg2uF34Y?si=l0A0Es0l6WeUbkro",
]

def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    # Regular expression to match YouTube video IDs
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if match:
        return match.group(1)
    else:
        print(f"Could not extract video ID from URL: {url}")
        return None

def scrape_and_save_videos(urls):
    """
    Scrapes video data for each URL and saves it to a unique JSON file.
    """
    for url in urls:
        video_id = get_video_id(url)
        if video_id:
            try:
                # Run the scraper from test.py
                data = test.run_scraper(url)
                
                # Create a unique filename using the video ID
                filename = f"{video_id}_data.json"
                
                # Save the data to a JSON file
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                
                print(f"Data for video ID {video_id} saved to {filename}")
            except Exception as e:
                print(f"An error occurred while scraping {url}: {e}")
        else:
            print(f"Skipping URL due to invalid video ID: {url}")

if __name__ == "__main__":
    scrape_and_save_videos(video_urls)
