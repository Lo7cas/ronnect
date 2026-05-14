import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("DISCORD_TOKEN")
PUBLIC_KEY = os.getenv("PUBLIC_DISCORD_KEY")
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
    if data.get("key") != ROBLOX_ACCESS_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    action = data.get("action")
    player_name = data.get("player_name")
    server_id = data.get("server_id").lower()

    user_id = get_discord_user_by_nickname(player_name)
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}
    channels = requests.get(f"https://discord.com/api/v10/guilds/{GUILD_ID}/channels", headers=headers).json()
    target_channel = next((c for c in channels if c['name'] == server_id), None)

    if action == "player_added":
        if not target_channel:
            payload = {
                "name": server_id,
                "type": 0,
                "permission_overwrites": [
                    {"id": GUILD_ID, "deny": "1024"},
                    {"id": user_id, "allow": "1024"}
                ]
            }
            requests.post(f"https://discord.com/api/v10/guilds/{GUILD_ID}/channels", headers=headers, json=payload)
        else:
            requests.put(
                f"https://discord.com/api/v10/channels/{target_channel['id']}/permissions/{user_id}",
                headers=headers,
                json={"allow": "1024", "type": 1}
            )

    elif action == "player_removing":
        if target_channel:
            requests.delete(f"https://discord.com/api/v10/channels/{target_channel['id']}/permissions/{user_id}", headers=headers)
            
            updated_channel = requests.get(f"https://discord.com/api/v10/channels/{target_channel['id']}", headers=headers).json()
            overwrites = updated_channel.get("permission_overwrites", [])
            
            user_overwrites = [o for o in overwrites if o['id'] != GUILD_ID and o['type'] == 1]
            
            if len(user_overwrites) == 0:
                requests.delete(f"https://discord.com/api/v10/channels/{target_channel['id']}", headers=headers)

    return jsonify({"status": "ok"})
