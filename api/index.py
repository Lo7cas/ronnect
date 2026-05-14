from flask import Flask, jsonify, request
from discord_interactions import verify_key
import os

app = Flask(__name__)
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

@app.route('/', methods=['POST'])
def interactions():
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    
    # Wir nehmen die komplett unverarbeiteten Daten (raw)
    raw_body = request.get_data()

    if signature is None or timestamp is None or not verify_key(raw_body, signature, timestamp, PUBLIC_KEY):
        return 'Bad request signature', 401

    interaction = request.json
    if interaction.get('type') == 1:
        return jsonify({'type': 1})

    return jsonify({
        'type': 4,
        'data': {'content': 'Bot läuft!'}
    })

index = app
