import re
import json
import time
import logging
from itertools import islice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--mute-audio")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_title(driver):
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, '#title yt-formatted-string')
        title = title_element.text
        return title
    except Exception as e:
        print("Error scraping title:", e)
        return None

def scrape_comment_count(driver):
    try:
        # Perform a small scroll to reveal the comments section
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(2)  # Wait briefly for comments section to load

        # Attempt to locate the comment count element
        comment_count_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//yt-formatted-string[contains(@class, "count-text")]'))
        )

        # Extract and process the comment count text
        comment_count_text = comment_count_element.text
        comment_count = int(re.sub('[^0-9]', '', comment_count_text))  # Remove non-numeric characters

        return comment_count
    except Exception as e:
        print("Error scraping comment count:", e)
        return None

def expand_description_box(driver):
    try:
        show_more = driver.find_element(By.CSS_SELECTOR, 'tp-yt-paper-button#expand')
        driver.execute_script("arguments[0].click();", show_more)
        time.sleep(2)  # Wait for content to load
    except Exception:
        print("No 'Show more' button found or already expanded.")

def scrape_views_date_tags(driver):
    try:
        # Locate the info section containing views, upload date, and tags
        info_element = driver.find_element(By.CSS_SELECTOR, 'yt-formatted-string#info')

        # Extract views count using regex
        views_match = re.search(r'([\d,\.]+)\sviews', info_element.text)
        if views_match:
            views_str = views_match.group(1).replace(',', '').replace('.', '')
            views_count = int(views_str)
        else:
            views_count = None

        # Extract upload date
        date_match = re.search(r'(\d{1,2}\s\w+\s\d{4}|\w+\s\d{1,2},\s\d{4})', info_element.text)
        upload_date = date_match.group(1) if date_match else None

        # Extract tags (hashtags) within the info section and remove '#'
        tag_elements = info_element.find_elements(By.CSS_SELECTOR, 'a.yt-simple-endpoint')
        tags = [tag.text.lstrip('#') for tag in tag_elements]

        return views_count, upload_date, tags
    except Exception as e:
        print("Error scraping views, upload date, or tags:", e)
        return None, None, []

def scrape_likes(driver):
    try:
        like_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="like this video"]')
        likes_text = like_button.get_attribute("aria-label")
        likes_match = re.search(r'([\d,\.]+)', likes_text)

        if likes_match:
            likes_str = likes_match.group(1).replace(',', '').replace('.', '')
            likes_count = int(likes_str)
        else:
            likes_count = None

        dislikes_count = None  # Dislikes are not publicly available
        return likes_count, dislikes_count
    except Exception as e:
        print("Error scraping likes or dislikes:", e)
        return None, None

def scrape_channel_info(driver):
    try:
        channel_name_element = driver.find_element(By.CSS_SELECTOR, '#channel-name #text')
        channel_name = channel_name_element.text.strip()

        subscriber_count_element = driver.find_element(By.CSS_SELECTOR, '#owner-sub-count')
        subscriber_count_text = subscriber_count_element.text.strip().replace("subscribers", "").strip()

        if 'K' in subscriber_count_text:
            subscriber_count = int(float(subscriber_count_text.replace('K', '').replace(',', '')) * 1000)
        elif 'M' in subscriber_count_text:
            subscriber_count = int(float(subscriber_count_text.replace('M', '').replace(',', '')) * 1_000_000)
        else:
            subscriber_count = int(subscriber_count_text.replace(',', ''))

        return channel_name, subscriber_count
    except Exception as e:
        print("Error scraping channel name or subscriber count:", e)
        return None, None

def scrape_transcript(driver):
    try:
        transcript_button = driver.find_element(By.XPATH, '//*[@id="primary-button"]/ytd-button-renderer/yt-button-shape/button')
        transcript_button.click()
        time.sleep(2)

        transcript = ""
        index = 1
        while True:
            try:
                segment_xpath = f'//*[@id="segments-container"]/ytd-transcript-segment-renderer[{index}]/div/yt-formatted-string'
                text_element = driver.find_element(By.XPATH, segment_xpath)
                transcript += text_element.text + "\n"
                index += 1
            except:
                break

        return transcript
    except Exception as e:
        print("Error scraping transcript:", e)
        return None

class ScraperComments:
    def __init__(self, url, sort_by=SORT_BY_POPULAR, comment_limit=21):
        self.url = url
        self.sort_by = sort_by
        self.comment_limit = comment_limit
        self.comments = []

    def get_comments(self):
        try:
            downloader = YoutubeCommentDownloader()
            comments = downloader.get_comments_from_url(self.url, sort_by=self.sort_by)
            comment_data = [comment['text'] for comment in islice(comments, self.comment_limit)]
            logging.info("Successfully downloaded comments")
            return comment_data
        except Exception as e:
            logging.error("Error in downloading comments", exc_info=True)
            return None

    def save_to_json(self, comments, file_name='comments2.json'):
        if not comments:
            logging.warning("No comments to save.")
            return
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(comments, file, ensure_ascii=False, indent=4)
            logging.info(f"Comments saved to {file_name}")
        except Exception as e:
            logging.error("Error in saving comments to JSON", exc_info=True)

    def scrape_and_save_comments(self):
        comments = self.get_comments()
        self.save_to_json(comments)

if __name__ == "__main__":
    driver = setup_driver()
    url = "https://youtu.be/zCp3j1KZCh4?si=Sg3jRiAPg24e4ph3"
    driver.get(url)
    time.sleep(5)

    # Step 1: Scrape the title
    title = scrape_title(driver)
    print("Title:", title)

    # Step 2: Scrape the comment count (minimal scroll)
    comment_count = scrape_comment_count(driver)
    print("Number of Comments:", comment_count)

    # Step 3: Expand the description box
    expand_description_box(driver)

    # Step 4: Continue with remaining scraping
    views_count, upload_date, tags = scrape_views_date_tags(driver)
    print("Views:", views_count)
    print("Upload Date:", upload_date)
    print("Tags:", tags)

    likes_count, _ = scrape_likes(driver)
    print("Likes:", likes_count)

    channel_name, subscriber_count = scrape_channel_info(driver)
    print("Channel Name:", channel_name)
    print("Subscriber Count:", subscriber_count)

    transcript_text = scrape_transcript(driver)
    if transcript_text:
        transcript_data = {"transcript": transcript_text}
        with open("transcript2.json", "w", encoding="utf-8") as json_file:
            json.dump(transcript_data, json_file, ensure_ascii=False, indent=4)
        print("Transcript saved to transcript.json")

    # Close the driver
    driver.quit()

    # Scrape comments and save to JSON
    scraper = ScraperComments(url, comment_limit=21)
    scraper.scrape_and_save_comments()
    print("Successfully saved comments to comments.json")