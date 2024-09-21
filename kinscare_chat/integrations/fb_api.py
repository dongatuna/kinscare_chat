import os
import requests
from fastapi import HTTPException

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_REDIRECT_URI = os.getenv("FB_REDIRECT_URI")
FB_AUTH_URL = "https://www.facebook.com/v17.0/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/v17.0/oauth/access_token"
FB_POST_URL = "https://graph.facebook.com/v17.0/me/feed"

class FacebookAPI:
    def __init__(self):
        self.app_id = FB_APP_ID
        self.app_secret = FB_APP_SECRET
        self.redirect_uri = FB_REDIRECT_URI
        self.auth_url = FB_AUTH_URL
        self.token_url = FB_TOKEN_URL
        self.post_url = FB_POST_URL
        self.access_token = None

    def get_auth_url(self):
        return (
            f"{self.auth_url}?client_id={self.app_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=public_profile,pages_manage_posts"
            f"&response_type=code"
        )

    def exchange_code_for_access_token(self, code: str):
        response = requests.get(
            self.token_url,
            params={
                "client_id": self.app_id,
                "redirect_uri": self.redirect_uri,
                "client_secret": self.app_secret,
                "code": code,
            },
        )
        response_data = response.json()
        if "access_token" in response_data:
            self.access_token = response_data["access_token"]
            return self.access_token
        else:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")

    def make_post(self, message: str):
        if not self.access_token:
            raise HTTPException(status_code=401, detail="Access token is missing")

        response = requests.post(
            self.post_url,
            params={
                "access_token": self.access_token,
                "message": message
            }
        )
        response_data = response.json()
        if "id" in response_data:
            return response_data
        else:
            raise HTTPException(status_code=400, detail="Failed to make post")
