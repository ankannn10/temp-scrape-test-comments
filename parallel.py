# parallel_scraper.py
import concurrent.futures
import test  # Assuming your code is encapsulated for importing
import json

video_urls = [
    # List of YouTube URLs to scrape
    "https://youtu.be/5bevi_0v6wU?si=MTxFF2cLfBob8GBB",
    "https://youtu.be/jac53THxO0I?si=CgDkWDVJhcaScJog",
    "https://youtu.be/1s9Vg2uF34Y?si=l0A0Es0l6WeUbkro",
    # add more URLs as needed
]

def scrape_video(url):
    # Initialize the scraper object or directly call functions from youtube_scraper
    data = test.run_scraper(url)  # assuming scrape_video_data is main function in youtube_scraper
    filename = f"{url.split('=')[1]}_data.json"  # save each file uniquely
    with open(filename, 'w') as file:
        json.dump(data, file)
    return filename

if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(scrape_video, video_urls))
    print(f"Scraped data saved in files: {results}")
