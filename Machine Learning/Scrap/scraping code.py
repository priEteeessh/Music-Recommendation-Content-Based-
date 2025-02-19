from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import random

def scrape_songs(url, start_index=0, limit=None):
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(2)

    # Pausing execution to manually complete CAPTCHA
    input("Please complete the CAPTCHA manually, then press Enter...")

    songs = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Locate the table rows after scrolling
        table = driver.find_element(By.TAG_NAME, "table")
        tbody = table.find_element(By.TAG_NAME, "tbody")

        # Retry logic to handle StaleElementReferenceException
        for attempt in range(3):
            try:
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                break
            except StaleElementReferenceException:
                print("Stale element reference. Retrying...")
                time.sleep(1)

        for row in rows[len(songs) + start_index:]:
            try:
                columns = row.find_elements(By.TAG_NAME, "td")
                if len(columns) > 5:
                    song_info = columns[2].text
                    # Splititng title and artist
                    title, artist = song_info.split('\n')
                    date_string = columns[4].text
                    year = date_string.split(',')[-1].strip() if ',' in date_string else date_string.strip()
                    popularity = random.randint(1, 10)

                    songs.append({
                        "Title": title,
                        "Artist": artist,
                        "Date": year,
                        "Popularity": popularity,
                        "Genre": "Hollywood"
                    })

                # Saving records after collecting 100 songs
                if len(songs) % 100 == 0:
                    add_songs_to_excel(songs, file_path="songs_data.xlsx")
                    print(f"Saved {len(songs)} songs so far.")

            except ValueError:
                print(f"Skipping row due to unexpected format: {song_info}")
            except Exception as e:
                print(f"Error processing row: {e}")

            # Stopping if the limit has been reached
            if limit and len(songs) + start_index >= limit:
                print(f"Collected {limit} songs. Stopping.")
                break

        # Checking if we've reached the bottom of the page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height or (limit and len(songs) + start_index >= limit):
            break
        last_height = new_height

    driver.close()

    # Saving any remaining songs at the end
    add_songs_to_excel(songs, file_path="songs_data.xlsx")
    print(f"Total songs scraped: {len(songs)}")
    return songs


def add_songs_to_excel(new_songs, file_path="songs_data.xlsx"):
    if not new_songs:
        return  # No new songs to add

    new_df = pd.DataFrame(new_songs)

    # Load existing data if the file exists
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    combined_df.drop_duplicates(subset=["Title", "Artist"], inplace=True)

    # Reset the index to start from 1
    combined_df.index = range(1, len(combined_df) + 1)

    # Save to Excel with a single index column
    combined_df.to_excel(file_path, index=False)


# Main scraping function that resumes from the last saved record
def main():
    file_path = "songs_data.xlsx"

    # Determine the starting index based on the existing file
    start_index = 0
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        start_index = len(existing_df)

    # Scraping songs from these URLs
    url_list = [
        "https://credits.muso.ai/profile/10c8ed6f-9cd6-4ffd-a53b-29d0dfa21c66/credits",
        "https://credits.muso.ai/profile/48f7ddd6-c3d2-4c6e-95d7-0db6009c0856/credits",
        "https://credits.muso.ai/profile/6517cbd0-5830-435a-948f-93a014f16e49/credits",
        "https://credits.muso.ai/profile/9dd94bb1-da0f-45ed-802b-0274ebd65c33/credits",
        "https://credits.muso.ai/profile/7a850ae7-33e9-497d-9a30-c2dae9b7a6a3/credits",
        "https://credits.muso.ai/profile/a82abe38-f746-42bc-a1b8-34cc88dff127/credits",
        "https://credits.muso.ai/profile/677ec442-f18d-4af2-87bb-74602c2590f5/credits",
        "https://credits.muso.ai/profile/5dffbdc1-800f-4f95-ab58-9cefe5800dd0/credits",
        "https://credits.muso.ai/profile/0f3596f4-388c-448f-9add-b4468a886824/credits",
        "https://credits.muso.ai/profile/0c85f456-fe85-4789-9724-c10d696bb583/credits",
        "https://credits.muso.ai/profile/7db4a291-d482-4536-be87-2d06958e5d53/credits",
        "https://credits.muso.ai/profile/d902b465-ac21-48b6-a01d-7322fe9ebf13/credits",
        "https://credits.muso.ai/profile/2563d334-3dc3-4dc0-b6fb-303ae7ec91ad/credits",
        "https://credits.muso.ai/profile/195447e8-2e5e-435b-b9ea-8b6b40ea9c7b/credits",
        "https://credits.muso.ai/profile/bd0b2f35-cd32-42dd-821d-e3bb4a8bb934/credits",
        "https://credits.muso.ai/profile/827f6c94-3d7f-454f-8090-6ea3b0062e76/credits",
        "https://credits.muso.ai/profile/cbb3b11b-33f9-43c1-935a-75d7fff69252/credits",
        "https://credits.muso.ai/profile/2a769466-b1f0-4f2b-8f45-1354c8597022/credits",
        "https://credits.muso.ai/profile/4014d088-f893-4708-9e99-54ef55178120/credits",
        "https://credits.muso.ai/profile/e7ec2434-faf6-4e83-a169-e974001985f6/credits",
        "https://credits.muso.ai/profile/0ba5e3fd-2958-4450-b473-c129c6b0b52c/credits",
        "https://credits.muso.ai/profile/8f1f25f9-17c1-4eeb-9cf9-278146d85357/credits",
        "https://credits.muso.ai/profile/4abd5f9c-afc0-eb8e-42c3-b17be1186b34/credits",
        "https://credits.muso.ai/profile/a1fbcde4-eb29-42c0-81b5-1fb14a7b40a7/credits",
    ]

    for url in url_list:
        new_songs = scrape_songs(url, start_index=start_index, limit=None)

# Main function
main()
