from flask import Flask, request, redirect, jsonify, session
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT SECRET HERE'
REDIRECT_URI = 'https://069e-113-211-212-168.ngrok-free.app/callback'
SCOPES = 'RECEIPTS_READ ITEMS_READ'


@app.route("/")
def home():
    return "Welcome to the Loyverse Report Viewer!"


# android app call to /login to get to loyverse login page
@app.route('/login')
def login():
    state = request.args.get('state') or secrets.token_urlsafe(16)

    # Store the state in the session for later verification
    session['state'] = state

    authorize_url = (f"https://api.loyverse.com/oauth/authorize?"
                     f"client_id={CLIENT_ID}"
                     f"&response_type=code"
                     f"&redirect_uri={REDIRECT_URI}"
                     f"&scope={SCOPES}"
                     f"&state={state}")

    return redirect(authorize_url)


@app.route("/callback")
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if not code:
        return "No authorization code received", 400

    # Verify that the state matches the one sent in the login request
    if state != session.get('state'):
        return "Invalid state parameter", 400  # CSRF attack detected

    # Token request to exchange the code for an access token
    token_url = 'https://api.loyverse.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    # Request the token from Loyverse API
    response = requests.post(token_url, data=data)
    token_info = response.json()

    if 'access_token' not in token_info:
        return "Error retrieving access token", 400

    access_token = token_info['access_token']
    print("Token Info:", token_info)

    # Construct the redirect URL to send the token back to the Android app
    redirect_url = f"loyversereportviewerapp://callback?access_token={access_token}&refresh_token={token_info.get('refresh_token')}&expires_in={token_info.get('expires_in')}&scope={token_info.get('scope')}"

    # Redirect the user back to the app using the custom URI scheme
    return redirect(redirect_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
