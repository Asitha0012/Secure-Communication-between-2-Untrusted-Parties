import requests

response = requests.post(
    "https://127.0.0.1:9443/onboard",
    cert=("xapp.crt", "xapp.key"),
    verify="ca.crt"
)

print(response.text)
