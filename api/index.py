import os
from flask import Flask, request, jsonify
import requests
from discord_interactions import verify_key

app = Flask(__name__)

PUBLIC_KEY = os.getenv("PUBLIC_DISCORD_KEY")
BOT_TOKEN = os.getenv("DISCORD_TOKEN")
ROBLOX_ACCESS_KEY = os.getenv("ROBLOX_ACCESS_KEY")

@app.route('/', methods=['POST'])
def interactions():
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    if not verify_key(body, signature, timestamp, PUBLIC_KEY):
        return 'invalid request signature', 401

    data = request.json
    if data.get('type') == 1:
        return jsonify({'type': 1})
    
    return jsonify({
        'type': 4,
        'data': {'content': 'Ronnect ist online!'}
    })

@app.route('/roblox', methods=['POST'])
def from_roblox():
    data = request.json
    
    incoming_key = data.get("key")
    if incoming_key != ROBLOX_ACCESS_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    channel_id = data.get("channel_id")
    message = data.get("message")
    
    if not channel_id or not message:
        return jsonify({"error": "Missing data"}), 400

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": message}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Discord API error", "details": response.text}), 500

if __name__ == '__main__':
    app.run(debug = True)
