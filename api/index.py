from flask import Flask, jsonify, request
from discord_interactions import verify_key_decorator
import os

app = Flask(__name__)

PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

@app.route('/', methods=['POST'])
def interactions():
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    
    content = request.json

    if content.get("type") == 1:
        return jsonify({"type": 1})

    if content.get("type") == 2:
        return jsonify({
            "type": 4,
            "data": {"content": "Vercel Bot is online"}
        })

    return jsonify({"type": 1})

@app.route('/roblox', methods=['POST'])
def roblox_handler():
    data = request.json
    print(f"Data from Roblox: {data}")
    return jsonify({"status": "received"}), 200