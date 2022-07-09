import requests
from bs4 import BeautifulSoup
import json

url_to_site = f"https://genius.com/api/search/multi?per_page=5&q={'%20'.join(['гимн', 'дахака'])}"
page_site = requests.get(url_to_site)
content = page_site.text

url_to_mus = json.loads(content)["response"]["sections"][0]["hits"][0]["result"]["url"]
print(url_to_mus)


