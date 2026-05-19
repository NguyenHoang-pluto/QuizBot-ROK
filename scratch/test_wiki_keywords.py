import requests
import re

def clean_question_for_search(q):
    # Convert to lowercase
    q = q.lower().strip()
    
    # Remove punctuation
    q = re.sub(r'[\?\.\,\!\-\_\(\)]', ' ', q)
    
    # List of common question words / stop words to remove
    stop_words = [
        "thành phố", "nào", "sau đây", "nằm ở", "ở", "vào", "rơi", "tháng mấy", "là gì", "là ai", 
        "bao nhiêu", "như thế nào", "tại sao", "cái gì", "ai là", "quốc gia", "nước nào", "đơn vị", 
        "chỉ huy", "tướng", "vị", "năm nào", "nhóm", "loại", "vật phẩm", "được", "mệnh danh", "gọi là",
        "có", "thể", "trong", "trên", "dưới", "của", "và", "hoặc", "thì", "mà", "là", "một", "những", "các"
    ]
    
    # Replace stop words
    for word in stop_words:
        # Match word boundaries or spaces around
        q = re.sub(r'\b' + re.escape(word) + r'\b', ' ', q)
        
    # Clean extra spaces
    q = re.sub(r'\s+', ' ', q).strip()
    return q

def test_wiki_search(raw_q):
    cleaned_q = clean_question_for_search(raw_q)
    print(f"Raw: '{raw_q}'")
    print(f"Cleaned for search: '{cleaned_q}'")
    
    search_url = "https://vi.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'RoKQuizBot/1.0'}
    
    for q_term in [raw_q, cleaned_q]:
        print(f"\n--- Searching Wikipedia for: '{q_term}' ---")
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': q_term,
            'utf8': 1,
            'format': 'json',
            'srlimit': 3
        }
        res = requests.get(search_url, params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            results = res.json().get('query', {}).get('search', [])
            for i, r in enumerate(results):
                print(f"  Result {i+1}: Title='{r['title']}', Snippet='{re.sub(r'<[^>]*>', '', r['snippet'])[:150]}...'")

if __name__ == "__main__":
    test_wiki_search("mùa thu ở việt nam rơi vào tháng mấy")
