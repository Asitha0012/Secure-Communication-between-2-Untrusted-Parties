import requests

response = requests.post(
    "https://127.0.0.1:8443/onboard",
    cert=("fake.crt", "fake.key"),
    verify="ca.crt"
)

print(response.text)
