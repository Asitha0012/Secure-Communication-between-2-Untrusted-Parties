# Secure Onboarding of Third-Party xApps in Near-RT RIC of Open RAN

## Information Security Course Project

### Project Title
Secure Communication Design and Implementation for Third-Party xApp Onboarding in Open RAN Near-RT RIC

---

# 1. Project Overview

This project demonstrates a secure onboarding mechanism for third-party xApps into the Open RAN Near-Real-Time RAN Intelligent Controller (Near-RT RIC) using mutual TLS (mTLS).

The implementation uses:

- Existing OSC Near-RT RIC Kubernetes cluster
- Existing custom SDL xApp
- Lightweight Flask-based SMO server
- Certificate Authority (CA)
- Mutual TLS authentication
- Helm onboarding through ChartMuseum
- Fake xApp attack simulation
- MITM attack simulation

The system ensures:

- Confidentiality
- Integrity
- Authentication
- Secure onboarding
- Protection against unauthorized xApps
- Protection against MITM attacks

---

# 2. Architecture

```text
Trusted xApp Vendor
        |
        |  Mutual TLS Authentication
        v
Lightweight SMO Server (Flask HTTPS Server)
        |
        |  Verification of Trusted Certificates
        v
ChartMuseum + dms_cli
        |
        v
OSC Near-RT RIC Kubernetes Cluster
        |
        v
Secure xApp Deployment
```

---

# 3. Technologies Used

| Technology | Purpose |
|---|---|
| OSC Near-RT RIC | Open RAN platform |
| Kubernetes | Container orchestration |
| Docker | xApp containerization |
| Flask | Lightweight SMO server |
| OpenSSL | Certificate generation |
| Python Requests | Secure HTTPS communication |
| mTLS | Mutual authentication |
| ChartMuseum | Helm chart repository |
| Helm/dms_cli | xApp onboarding |

---

# 4. Prerequisites

Before starting:

- Ubuntu VM installed
- OSC Near-RT RIC cluster already running
- Existing custom SDL xApp already available
- Docker installed
- Kubernetes installed
- Helm installed
- Python3 installed
- Flask installed

Install required Python packages:

```bash
pip3 install flask requests
```

Explanation:
- Flask is used to create the lightweight SMO server.
- Requests library is used for HTTPS onboarding communication.

---

# 5. Existing Custom xApp

This project reuses the existing custom SDL xApp.

Original xApp description:

- Reads/writes data to Redis SDL database
- Uses SDL API
- Runs inside Near-RT RIC

The secure onboarding process deploys this xApp again as a new secure deployment.

---

# 6. Create Working Directory

```bash
mkdir ~/Desktop/security
cd ~/Desktop/security
```

Explanation:
- All security-related files are stored in this directory.

---

# 7. Create Root Certificate Authority (CA)

## Step 1 — Generate CA Private Key

```bash
openssl genrsa -out ca.key 2048
```

Explanation:
- Generates the private key of the trusted root CA.
- This CA signs trusted certificates.

---

## Step 2 — Create Root CA Certificate

```bash
openssl req -x509 -new -nodes \
-key ca.key \
-sha256 -days 365 \
-out ca.crt
```

Use:

```text
Common Name = OpenRAN-Root-CA
```

Explanation:
- Creates self-signed root CA certificate.
- This CA becomes the trust anchor.

Generated Files:

| File | Purpose |
|---|---|
| ca.key | Root CA private key |
| ca.crt | Root CA certificate |

---

# 8. Create Trusted xApp Certificate

## Step 1 — Generate xApp Private Key

```bash
openssl genrsa -out xapp.key 2048
```

Explanation:
- Creates private key for trusted xApp onboarding client.

---

## Step 2 — Create xApp CSR

```bash
openssl req -new -key xapp.key -out xapp.csr
```

Use:

```text
Common Name = trusted-xapp
```

Explanation:
- CSR = Certificate Signing Request.
- Requests certificate from trusted CA.

---

## Step 3 — Sign xApp Certificate Using CA

```bash
openssl x509 -req \
-in xapp.csr \
-CA ca.crt \
-CAkey ca.key \
-CAcreateserial \
-out xapp.crt \
-days 365 \
-sha256
```

Explanation:
- CA signs the xApp certificate.
- Makes xApp trusted by SMO.

Generated Files:

| File | Purpose |
|---|---|
| xapp.key | Trusted xApp private key |
| xapp.csr | xApp certificate request |
| xapp.crt | Trusted xApp certificate |
| ca.srl | CA serial file |

---

# 9. Create SMO Server Certificate

## Step 1 — Create SAN Configuration File

Create:

```bash
nano san.cnf
```

Paste:

```ini
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[dn]
CN = 127.0.0.1

[req_ext]
subjectAltName = @alt_names

[alt_names]
IP.1 = 127.0.0.1
```

Explanation:
- Adds Subject Alternative Name (SAN).
- Prevents hostname verification warnings.

---

## Step 2 — Generate SMO Key

```bash
openssl genrsa -out smo.key 2048
```

Explanation:
- Creates SMO server private key.

---

## Step 3 — Create SMO CSR

```bash
openssl req -new \
-key smo.key \
-out smo.csr \
-config san.cnf
```

Explanation:
- Creates certificate request for SMO.

---

## Step 4 — Sign SMO Certificate

```bash
openssl x509 -req \
-in smo.csr \
-CA ca.crt \
-CAkey ca.key \
-CAcreateserial \
-out smo.crt \
-days 365 \
-sha256 \
-extfile san.cnf \
-extensions req_ext
```

Explanation:
- CA signs the SMO server certificate.
- Makes SMO trusted by xApps.

Generated Files:

| File | Purpose |
|---|---|
| smo.key | SMO private key |
| smo.csr | SMO certificate request |
| smo.crt | Trusted SMO certificate |
| san.cnf | SAN configuration |

---

# 10. Start ChartMuseum

## Step 1 — Run ChartMuseum

```bash
docker run --rm -u 0 -it -d \
-p 8090:8080 \
-e STORAGE=local \
-e STORAGE_LOCAL_ROOTDIR=/charts \
chartmuseum/chartmuseum:latest
```

Explanation:
- Creates local Helm chart repository.
- Used by dms_cli during onboarding.

---

## Step 2 — Verify ChartMuseum

```bash
curl http://127.0.0.1:8090/api/charts
```

Expected Output:

```text
{}
```

Explanation:
- Empty response means ChartMuseum is running.

---

# 11. Create Secure Descriptor

Go to existing custom xApp folder.

Example:

```bash
cd ~/Desktop/custom-sdl-xapp
```

---

## Step 1 — Copy Existing Descriptor

```bash
cp -r descriptor descriptor-secure
```

Explanation:
- Creates separate onboarding descriptor.
- Prevents affecting original FYP deployment.

---

## Step 2 — Fix Permissions

```bash
sudo chown -R $USER:$USER descriptor-secure
```

Explanation:
- Removes root ownership.
- Allows editing files normally.

---

## Step 3 — Edit config-file.json

Open:

```bash
nano descriptor-secure/config-file.json
```

Replace content with:

```json
{
    "name": "sdl-xapp-secure",
    "version": "1.0.0",
    "containers": [
        {
            "name": "sdl-xapp-secure",
            "image": {
                "registry": "127.0.0.1:5000",
                "name": "sdl-xapp-secure",
                "tag": "1.0.0"
            }
        }
    ],
    "controls": {
        "logger": {
            "level": 3
        }
    },
    "messaging": {
        "ports": [
            {
                "name": "rmr-data",
                "container": "sdl-xapp-secure",
                "port": 4560,
                "description": "rmr data port"
            },
            {
                "name": "rmr-route",
                "container": "sdl-xapp-secure",
                "port": 4561,
                "description": "rmr route port"
            }
        ]
    },
    "rmr": {
        "protPort": "tcp:4560",
        "maxSize": 2072,
        "numWorkers": 1,
        "txMessages": ["RIC_SUB_REQ"],
        "rxMessages": ["RIC_SUB_RESP"]
    }
}
```

Explanation:
- Creates separate secure onboarding deployment.
- Prevents conflict with original FYP xApp.

---

# 12. Build Docker Image

Go to custom xApp source directory.

```bash
cd ~/Desktop/custom-sdl-xapp
```

---

## Step 1 — Build Docker Image

```bash
docker build -t 127.0.0.1:5000/sdl-xapp-secure:1.0.0 .
```

Explanation:
- Builds secure xApp Docker image.

---

## Step 2 — Push Docker Image

```bash
docker push 127.0.0.1:5000/sdl-xapp-secure:1.0.0
```

Explanation:
- Pushes image into local Docker registry.

---

# 13. Onboard Helm Chart

Go to:

```bash
cd descriptor-secure
```

---

## Step 1 — Upload Helm Chart

```bash
sudo CHART_REPO_URL=http://127.0.0.1:8090 \
dms_cli onboard \
--config_file_path=config-file.json \
--shcema_file_path=schema.json
```

Explanation:
- Uploads xApp Helm chart to ChartMuseum.
- Makes xApp available for deployment.

---

## Step 2 — Verify Chart Exists

```bash
curl http://127.0.0.1:8090/api/charts | python3 -m json.tool
```

Expected Output:

```text
sdl-xapp-secure
```

Explanation:
- Confirms successful onboarding.

---

# 14. Create Lightweight SMO Server

Create:

```bash
nano smo_server.py
```

Paste:

```python
from flask import Flask, request
import ssl
import subprocess

app = Flask(__name__)

@app.route('/onboard', methods=['POST'])
def onboard():

    print("Trusted xApp verified")

    subprocess.run(
        "sudo CHART_REPO_URL=http://127.0.0.1:8090 dms_cli install sdl-xapp-secure 1.0.0 ricxapp",
        shell=True
    )

    return "xApp onboarding successful"

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.verify_mode = ssl.CERT_REQUIRED

context.load_cert_chain(
    certfile='smo.crt',
    keyfile='smo.key'
)

context.load_verify_locations(cafile='ca.crt')

app.run(
    host='0.0.0.0',
    port=8443,
    ssl_context=context
)
```

Explanation:
- Implements lightweight SMO onboarding server.
- Uses HTTPS + mutual TLS.
- Verifies client certificates.
- Deploys xApp only after successful authentication.

---

# 15. Create Trusted Onboarding Client

Create:

```bash
nano onboard_client.py
```

Paste:

```python
import requests

response = requests.post(
    "https://127.0.0.1:8443/onboard",
    cert=("xapp.crt", "xapp.key"),
    verify="ca.crt"
)

print(response.text)
```

Explanation:
- Simulates trusted third-party xApp vendor.
- Uses valid trusted certificate.
- Establishes secure mTLS connection.

---

# 16. Start Secure SMO Server

```bash
python3 smo_server.py
```

Expected Output:

```text
Running on https://0.0.0.0:8443/
```

Explanation:
- Starts HTTPS onboarding server.

---

# 17. Trigger Secure Onboarding

Open another terminal:

```bash
python3 onboard_client.py
```

Expected Output:

```text
xApp onboarding successful
```

Explanation:
- Trusted xApp successfully authenticated.
- SMO deploys xApp into Near-RT RIC.

---

# 18. Verify xApp Deployment

```bash
sudo kubectl get pods -A
```

Expected Output:

```text
ricxapp-sdl-xapp-secure-xxxxx
```

Explanation:
- Confirms successful onboarding and deployment.

---

# 19. Fake xApp Attack Simulation

This attack demonstrates rejection of unauthorized onboarding attempts.

---

## Step 1 — Create Fake Key

```bash
openssl genrsa -out fake.key 2048
```

Explanation:
- Creates attacker private key.

---

## Step 2 — Create Fake Self-Signed Certificate

```bash
openssl req -x509 -new -nodes \
-key fake.key \
-sha256 -days 365 \
-out fake.crt
```

Use:

```text
Common Name = malicious-xapp
```

Explanation:
- Creates fake self-signed certificate.
- NOT signed by trusted CA.

Generated Files:

| File | Purpose |
|---|---|
| fake.key | Attacker private key |
| fake.crt | Untrusted fake certificate |

---

## Step 3 — Modify onboard_client.py

Temporarily replace:

```python
cert=("xapp.crt", "xapp.key")
```

with:

```python
cert=("fake.crt", "fake.key")
```

Explanation:
- Simulates malicious xApp attempting onboarding.

---

## Step 4 — Run Attack

```bash
python3 onboard_client.py
```

Expected Output:

```text
TLSV1_ALERT_UNKNOWN_CA
```

Explanation:
- SMO rejects fake xApp.
- Mutual TLS authentication prevents unauthorized onboarding.

---

# 20. MITM Attack Simulation

This demonstrates protection against Man-in-the-Middle attacks.

---

## Step 1 — Create MITM Key

```bash
openssl genrsa -out mitm.key 2048
```

Explanation:
- Creates attacker server private key.

---

## Step 2 — Create Fake MITM Certificate

```bash
openssl req -x509 -new -nodes \
-key mitm.key \
-sha256 -days 365 \
-out mitm.crt
```

Use:

```text
Common Name = 127.0.0.1
```

Explanation:
- Creates rogue self-signed server certificate.

Generated Files:

| File | Purpose |
|---|---|
| mitm.key | MITM private key |
| mitm.crt | Rogue MITM certificate |

---

## Step 3 — Create MITM Server

Create:

```bash
nano mitm_server.py
```

Paste:

```python
from flask import Flask
import ssl

app = Flask(__name__)

@app.route('/onboard', methods=['POST'])
def fake():
    return "Intercepted by attacker"

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(
    certfile='mitm.crt',
    keyfile='mitm.key'
)

app.run(
    host='0.0.0.0',
    port=9443,
    ssl_context=context
)
```

Explanation:
- Simulates malicious fake SMO server.

---

## Step 4 — Create MITM Test Client

Create:

```bash
nano mitm_test_client.py
```

Paste:

```python
import requests

response = requests.post(
    "https://127.0.0.1:9443/onboard",
    cert=("xapp.crt", "xapp.key"),
    verify="ca.crt"
)

print(response.text)
```

Explanation:
- Trusted client attempts to connect to fake SMO.
- Client validates server certificate.

---

## Step 5 — Start MITM Server

```bash
python3 mitm_server.py
```

Explanation:
- Starts rogue HTTPS server.

---

## Step 6 — Run MITM Test

```bash
python3 mitm_test_client.py
```

Expected Output:

```text
CERTIFICATE_VERIFY_FAILED
```

Explanation:
- Client rejects rogue MITM certificate.
- Prevents attacker impersonation.

---

# 21. Remove Secure xApp Deployment

```bash
sudo helm uninstall ricxapp-sdl-xapp-secure -n ricxapp
```

Explanation:
- Removes secure onboarding deployment.
- Original FYP xApp remains unaffected.

---

# 22. Final Security Properties Achieved

| Security Property | How It Was Achieved |
|---|---|
| Confidentiality | TLS encryption protects communication |
| Integrity | TLS prevents tampering during transmission |
| Authentication | Mutual TLS validates both client and server |
| Secure Onboarding | SMO deploys only trusted xApps |
| Unauthorized Access Prevention | Fake xApps rejected |
| MITM Protection | Certificate validation blocks impersonation |
| Availability | Kubernetes manages deployment reliability |

---

# 23. Threats and Mitigations

| Threat | Mitigation |
|---|---|
| Unauthorized xApp onboarding | mTLS certificate validation |
| Fake xApp impersonation | Trusted CA verification |
| MITM attacks | TLS certificate verification |
| Traffic interception | Encrypted HTTPS communication |
| Deployment abuse | SMO verification before onboarding |

---

# 24. Assignment Requirement Mapping

| Assignment Requirement | Achieved Implementation |
|---|---|
| Secure communication between untrusted parties | xApp ↔ SMO using mTLS |
| Encryption | HTTPS/TLS |
| Authentication | Mutual TLS certificates |
| Integrity | TLS handshake and certificate validation |
| Threat mitigation | Fake xApp + MITM protection |
| Real implementation | OSC Near-RT RIC deployment |
| Security justification | CA trust model + certificate validation |

---

# 25. Final Conclusion

This project successfully implemented a secure onboarding framework for third-party xApps in Open RAN Near-RT RIC using mutual TLS authentication.

The implementation demonstrated:

- Secure communication
- Trusted onboarding
- Protection against unauthorized xApps
- MITM attack prevention
- Real Kubernetes deployment into OSC Near-RT RIC

The project satisfies all major Information Security assignment requirements while remaining lightweight and practical for Open RAN environments.

