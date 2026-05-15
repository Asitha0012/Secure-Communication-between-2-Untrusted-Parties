import os
import requests

base = os.path.dirname(os.path.abspath(__file__))

response = requests.post(
    "https://127.0.0.1:8443/onboard",
    cert=(f"{base}/xapp.crt", f"{base}/xapp.key"),
    verify=f"{base}/ca.crt"
)

print(response.text)
