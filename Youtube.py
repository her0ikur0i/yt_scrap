import asyncio
import os
import csv
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pyppeteer import launch

async def scrape_youtube():
    try:
        # Define file path
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'youtube_data.csv')
        
        # Launch browser
        browser = await launch(headless=False, executablePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

        # Create new page
        page = await browser.newPage()

        # Navigate to YouTube
        await page.goto('https://www.youtube.com/user/jacksfilms/videos')

        # Scroll to load more videos
        for _ in range(2):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")

            # Wait for 5 seconds after each scroll
            await asyncio.sleep(5)

        # Get HTML content
        html = await page.content()

        # Close the browser
        await browser.close()

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all video elements
        videos = soup.find_all('a', {'id': 'video-title-link'})

        # Extract data from each video element
        master_list = []
        for video in videos:
            data_dict = {}
            data_dict['title'] = video.text.strip()
            data_dict['video_url'] = 'https://youtube.com' + video['href']
            meta = video.find_parent().find_next_sibling().find_all('span')
            data_dict['views'] = meta[0].text.strip()
            data_dict['video_age'] = meta[1].text.strip()
            master_list.append(data_dict)

        # Create DataFrame from the list of dictionaries
        youtube_df = pd.DataFrame(master_list)

        # Function to convert views to numeric format
        def convert_views(df):
            if 'K' in df['views']:
                views = float(df['views'].split('K')[0]) * 1000
                return views
            elif 'M' in df['views']:
                views = float(df['views'].split('M')[0]) * 1000000
                return views

        # Apply the convert_views function to the 'views' column
        youtube_df['Clean_Views'] = youtube_df.apply(convert_views, axis=1)

        # Convert 'Clean_Views' column to integer type
        youtube_df['Clean_Views'] = youtube_df['Clean_Views'].astype(int)

        # Save DataFrame to CSV file
        youtube_df.to_csv(file_path, index=False)

        print("Data has been saved to", file_path)

    except Exception as e:
        print("Error:", e)

# Run the scraping function
asyncio.get_event_loop().run_until_complete(scrape_youtube())
