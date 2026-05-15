from flask import Flask
import ssl
import subprocess

app = Flask(__name__)

@app.route('/onboard', methods=['POST'])
def onboard():

    print("Trusted xApp verified")

    subprocess.run(
        "sudo CHART_REPO_URL=http://0.0.0.0:8090 dms_cli install sdl-xapp-secure 1.0.0 ricxapp",
        shell=True
    )

    return "xApp onboarding successful"

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = False

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
