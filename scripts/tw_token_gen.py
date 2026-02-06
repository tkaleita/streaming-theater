import webbrowser
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# --- CONFIG ---
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'https://localhost'
SCOPES = 'user:read:chat user:write:chat'

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            code = params['code'][0]
            # Exchange the "Code" for the actual Tokens
            token_url = "https://id.twitch.tv/oauth2/token"
            data = {
                "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
                "code": code, "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI
            }
            res = requests.post(token_url, data=data).json()
            print("\n" + "="*40)
            print(f"ACCESS TOKEN:  {res.get('access_token')}")
            print(f"REFRESH TOKEN: {res.get('refresh_token')}")
            print("="*40 + "\n")
            self.wfile.write(b"Success! Tokens printed in terminal. You can close this.")
        else:
            self.wfile.write(b"Error: No code found.")

# Start the flow
auth_url = f"https://id.twitch.tv/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES.replace(' ', '%20')}"
print(f"Opening browser to: {auth_url}")
webbrowser.open(auth_url)
HTTPServer(('localhost', 17563), OAuthHandler).handle_request()