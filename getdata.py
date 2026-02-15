import requests

req = requests.get("https://gamma-api.polymarket.com/status")
print(req.status_code)