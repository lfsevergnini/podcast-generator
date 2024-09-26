import random
import requests
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self, urls):
        self.urls = urls

    def fetch_content(self):
        content = []
        for url in self.urls:
            try:
                response = requests.get(url, timeout=3, verify=False, headers={'User-Agent': self.get_random_user_agent()})
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Attempt to extract main content
                main_content = self.extract_main_content(soup)
                content.append(main_content)
            except requests.RequestException as e:
                print(f"Failed to fetch {url}: {e}")
        return content

    def extract_main_content(self, soup):
        # Try to find the main content using common tags
        main_content = soup.find('article')
        if not main_content:
            main_content = soup.find('div', {'id': 'main-content'})
        if not main_content:
            main_content = soup.find('div', {'class': 'content'})
        if not main_content:
            main_content = soup.find('body')

        # Get text and remove extra whitespace
        text = main_content.get_text(separator=' ', strip=True)
        return text

    def get_random_user_agent(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/18.18362'
        ]

        return random.choice(user_agents)