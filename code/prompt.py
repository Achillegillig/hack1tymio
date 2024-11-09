import requests

url = "http://localhost:5000/api/generate"
payload = {
    "messages": [{"role": "user", 
                  "content": "Hey Llama, do you feel ready to be the pilot of a Tymio bot?"}]
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())