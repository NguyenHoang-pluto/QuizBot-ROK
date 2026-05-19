import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_autumn():
    url = 'https://www.google.com/search?q=mùa+thu+ở+việt+nam+rơi+vào+tháng+mấy+answer'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8'
    }
    res = requests.get(url, headers=headers, timeout=5, verify=False)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    print("Mobile divs found:", len(soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')))
    for i, d in enumerate(soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')[:2]):
        print(f"Mobile {i+1}:", d.text[:120])
        
    print("\nDesktop divs found:", len(soup.select('div[class*="VwiC3b"]')))
    for i, d in enumerate(soup.select('div[class*="VwiC3b"]')[:2]):
        print(f"Desktop {i+1}:", d.get_text()[:120])

if __name__ == "__main__":
    test_autumn()
