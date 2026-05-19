import requests
import re
import urllib3

urllib3.disable_warnings()

print("Đang tải trang...")
res = requests.get('https://rok-lac.vercel.app/en', verify=False)
html = res.text
print(f"Kích thước HTML: {len(html)}")

# Thử regex giải mã JSON lồng nhau
pattern = r'\\"question\\":\\"(.*?)\\",\\"answer\\":\\"(.*?)\\"'
matches = re.findall(pattern, html)

print(f"Tìm thấy: {len(matches)} câu hỏi!")
for i, (q, a) in enumerate(matches[:5]):
    print(f"{i+1}. Q: {q} -> A: {a}")
