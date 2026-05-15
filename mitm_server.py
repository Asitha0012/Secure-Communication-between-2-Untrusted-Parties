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
