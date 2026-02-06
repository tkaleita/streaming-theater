import requests

# 1. THE TOKEN YOU JUST COPIED FROM THE URL BAR
TW_TOKEN = "" 
# 2. YOUR CLIENT ID FROM THE CONSOLE
TW_CLIENT_ID = ""

def check_reality():
    # Note: Validate uses "OAuth" prefix, NOT "Bearer"
    headers = {"Authorization": f"OAuth {TW_TOKEN}"}
    r = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)
    
    data = r.json()
    if r.status_code == 200:
        print("✅ FINALLY! THE TOKEN IS VALID.")
        print(f"USER ID: {data['user_id']}")
        print(f"CLIENT ID: {data['client_id']}")
        print(f"SCOPES: {data['scopes']}")
    else:
        print(f"❌ STILL DEAD. Error: {data}")

check_reality()