import requests
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self, urls):
        self.urls = urls

    def fetch_content(self):
        content = []
        for url in self.urls:
            try:
                response = requests.get(url)
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