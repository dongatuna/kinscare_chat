from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from kinscare_chat.database.handlers.credentials import CredentialsDbCore
from kinscare_chat.integrations.fb_api import FacebookAPI
from kinscare_chat.server.models.auth import FbAuthCode

load_dotenv()
router = APIRouter()

@router.get("/auth-url")
def auth_url():
    facebook_api = FacebookAPI()
    url = facebook_api.get_auth_url()
    return {"auth_url": url}

@router.post("/authenticate")
def authenticate(code: str = Form(...)):
    facebook_api = FacebookAPI()
    try:
        token = facebook_api.exchange_code_for_access_token(code)
        user_id = "some_user_id"  # Replace with logic to fetch or generate user_id
        CredentialsDbCore.add_fb_creds(user_id, token)
        return {"access_token": token}
    except HTTPException as e:
        return {"error": str(e.detail)}

class PostMessage(BaseModel):
    message: str

@router.post("/post-message")
def post_message(post: PostMessage, facebook_api: FacebookAPI = Depends(FacebookAPI)):
    result = facebook_api.make_post(post.message)
    return result
