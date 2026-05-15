import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("DISCORD_TOKEN")
ROBLOX_ACCESS_KEY = os.getenv("ROBLOX_ACCESS_KEY")
GUILD_ID = os.getenv("GUILD_ID")

def get_discord_user_by_nickname(name):
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    response = requests.get(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/search?query={name}",
        headers=headers
    )
    if response.status_code == 200:
        members = response.json()
        for member in members:
            if member.get('nick') == name or member['user']['username'] == name:
                return member['user']['id']
    return None

@app.route('/roblox', methods=['POST'])
def handle_roblox():
    data = request.json
    if not data or data.get("key") != ROBLOX_ACCESS_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    action = data.get("action")
    player_name = data.get("player_name")
    server_id = data.get("server_id").lower()
    headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}

    channels_res = requests.get(f"https://discord.com/api/v10/guilds/{GUILD_ID}/channels", headers=headers)
    if channels_res.status_code != 200:
        return jsonify({"error": "Could not fetch Discord channels"}), 500
        
    channels = channels_res.json()
    target_channel = next((c for c in channels if c['name'] == server_id), None)

    if action == "server_close":
        if target_channel:
            requests.delete(f"https://discord.com/api/v10/channels/{target_channel['id']}", headers=headers)
        return jsonify({"status": "ok"}), 200

    user_id = get_discord_user_by_nickname(player_name)
    if not user_id:
        return jsonify({"error": f"User {player_name} not found"}), 404

    if action == "player_added":
        target_id = None
        if not target_channel:
            payload = {
                "name": server_id,
                "type": 0,
                "permission_overwrites": [
                    {"id": GUILD_ID, "deny": "1024"},
                    {"id": user_id, "allow": "1024"}
                ]
            }
            res = requests.post(f"https://discord.com/api/v10/guilds/{GUILD_ID}/channels", headers=headers, json=payload)
            if res.status_code == 201:
                target_id = res.json().get("id")
        else:
            target_id = target_channel['id']
            requests.put(
                f"https://discord.com/api/v10/channels/{target_id}/permissions/{user_id}",
                headers=headers,
                json={"allow": "1024", "type": 1}
            )

        if target_id:
            msg_payload = {"content": f"<@{user_id}> joined the chat"}
            requests.post(f"https://discord.com/api/v10/channels/{target_id}/messages", headers=headers, json=msg_payload)

    elif action == "player_removing":
        if target_channel:
            requests.delete(f"https://discord.com/api/v10/channels/{target_channel['id']}/permissions/{user_id}", headers=headers)

    return jsonify({"status": "ok"}), 200
