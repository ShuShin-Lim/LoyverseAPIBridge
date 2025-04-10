from flask import Flask, request, redirect
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the Loyverse Report Viewer!"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    
    # Exchange the code for an access token
    token_response = requests.post(
        "https://api.loyverse.com/oauth/token",
        data={
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://yourapp.onrender.com/callback"  # Update with your Render URL later
        }
    )

    tokens = token_response.json()
    access_token = tokens.get("access_token")

    # Redirect back to your Android app with the token
    return redirect(f"loyverseapp://callback?access_token={access_token}")

if __name__ == "__main__":
    app.run(debug=True)
