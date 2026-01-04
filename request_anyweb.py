import requests

url = "https://example.com" 

for i in range(1000000):
    try:
        response = requests.get(url, timeout=5)
        print(f"الطلب {i+1}: الحالة = {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"الطلب {i+1}: فشل - {e}")
