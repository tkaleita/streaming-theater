import requests
import urllib

scope = "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.force-ssl"
auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://oauth2.googleapis.com/token"
redirect_uri = "https://localhost"

YT_CLIENT_ID = ""
YT_CLIENT_SECRET = ""

params = {
    "client_id": YT_CLIENT_ID,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": scope,
    "access_type": "offline",
    "prompt": "consent",
}

full_auth_url = auth_url + "?" + urllib.parse.urlencode(params)

print("\nOpen this URL in your browser:\n")
print(full_auth_url)
print("\nAfter approving, you will be redirected to your redirect URI.")
print("Copy the `code` parameter from the URL and paste it here.\n")

auth_code = input("Authorization code: ").strip()

data = {
    "client_id": YT_CLIENT_ID,
    "client_secret": YT_CLIENT_SECRET,
    "code": auth_code,
    "grant_type": "authorization_code",
    "redirect_uri": redirect_uri,
}

response = requests.post(token_url, data=data, timeout=10)
response.raise_for_status()

tokens = response.json()

if "refresh_token" not in tokens:
    raise RuntimeError(
        "No refresh token returned. "
        "You probably already authorized this client without prompt=consent."
    )

print(tokens)