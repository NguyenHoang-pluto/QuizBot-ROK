import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_bing():
    url = "https://www.bing.com/search?q=Ai+la+nguoi+sang+lap+ra+Rome+answer"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8'
    }
    res = requests.get(url, headers=headers, timeout=5, verify=False)
    print("Response Length:", len(res.text))
    with open("scratch/bing_response.html", "w", encoding="utf-8") as f:
        f.write(res.text)

if __name__ == "__main__":
    save_bing()

# mùa thu ở việt nam rơi vào tháng mấy 