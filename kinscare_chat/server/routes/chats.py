import os
import threading
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from kinscare_chat.ai.openai_api import OpenAIAssistant
from kinscare_chat.database.handlers.credentials import CredentialsDbCore
from kinscare_chat.database.handlers.users import UsersDbCore
from kinscare_chat.integrations.fb_api import FacebookAPI
from kinscare_chat.integrations.sendgrid_api import SendGridApi
from kinscare_chat.server.models.chats import ChatRequest, InactiveChatRequest
from kinscare_chat.server.utils import verify_secret_key


assistant = OpenAIAssistant(os.getenv("OPENAI_ASSISTANT_ID"))
router = APIRouter()

INACTIVITY_TIMEOUT = 1800

TEST_USER_ID = 1

class JobEntry(BaseModel):
    name: str
    supervisor: str
    position: str
    email: EmailStr
    phone: str

class JobInfoRequest(BaseModel):
    entries: List[JobEntry]

class WebInactivity:
    users = {}
    inactives = []
    check_interval = 1  # time in seconds between checks

    @classmethod
    def update_thread(cls, thread_id):
        cls.users[thread_id] = time.time()

    @classmethod
    def reset_timer(cls, thread_id):
        del cls.users[thread_id]
        cls.inactives.remove(thread_id)

    @classmethod
    def trigger_inactive(cls, thread_id):
        if thread_id not in cls.inactives:
            cls.inactives.append(thread_id)
            return True
        else:
            return False

    @classmethod
    def check_inactivity(cls, thread_id):
        last_interaction_time = cls.users[thread_id]
        dist = time.time() - last_interaction_time
        if dist > INACTIVITY_TIMEOUT:
            pass #  TODO: do something on timeout
            cls.reset_timer(thread_id)

    @classmethod
    def start_background_task(cls):
        def task():
            while True:
                for thread_id in list(cls.users.keys()):
                    cls.check_inactivity(thread_id)
                time.sleep(cls.check_interval)

        thread = threading.Thread(target=task)
        thread.daemon = True  # Ensures that the thread will end when main program does
        thread.start()

# Start background task
WebInactivity.start_background_task()


@router.get('/chats/start', tags=["Chats"])
def start_conversation(_: str = Depends(verify_secret_key)):
    print("Starting a new conversation...")
    thread = assistant.new_thread()
    print(f"New thread created with ID: {thread.id}")
    return {"thread_id": thread.id}

@router.post('/chats/chat', tags=["Chats"])
def chat(new_chat: ChatRequest, _: str = Depends(verify_secret_key)):
    thread_id = new_chat.thread_id
    user_input = new_chat.message

    if not thread_id or not user_input:
        print("Error: Missing thread_id or user_input")
        raise HTTPException(status_code=400, detail="Missing thread_id or user_input")

    print(f"Received message: {user_input} for thread ID: {thread_id}")

    run_tools = assistant.new_message(thread_id, user_input)

    if run_tools:
        if run_tools[0] == 'capture_work_experience':
            return {"response": "SYS:FORM_JOB_EXPERIENCE"}
        elif run_tools[0] == 'share_plan_to_email':
            print('EMAIL share')
            content = run_tools[1].get('plan_content')
            settings = UsersDbCore.get_settings(TEST_USER_ID)
            emails = settings['share_emails']
            print(emails)
            if len(emails) == 0:
                return {"response": "No emails in your Share Emails list."}
            SendGridApi.send_plan_share_email(emails, content, "Inno Mwatsi")
            return {"response": "Email sent successfully."}
        elif run_tools[0] == 'yes_no':
            print("YES NO func")
            quest = run_tools[1].get('yes_no_question')
            return {"response": f"{quest} SYS:YES_NO"}
        else:
            print(run_tools[0])
    else:
        response = assistant.get_last_message(thread_id)

    if response is None:
        print("Error: No response from assistant")
        raise HTTPException(status_code=500, detail="No response from assistant")
        
    elif 'SYS:SHARE_FACEBOOK' in response['msg']:
        print('FB share')
        creds = CredentialsDbCore.get_fb_creds(TEST_USER_ID)
        if not creds:
            facebook_api = FacebookAPI()
            url = facebook_api.get_auth_url()
            return {"response": f"Please authenticate with Facebook by following this link: {url}"}
    elif 'SYS:SHARE_INSTAGRAM' in response['msg']:
        print('IG share')
        creds = CredentialsDbCore.get_fb_creds(TEST_USER_ID)
        if not creds:
            facebook_api = FacebookAPI()
            url = facebook_api.get_auth_url()
            return {"response": f"Please authenticate with Instagram by following this link: {url}"}
    elif 'SYS:SHOW_SETTINGS_SHARE_EMAILS' in response['msg']:
        settings = UsersDbCore.get_settings(1)
        emails = settings['share_emails']
        if len(emails) == 0:
            return {"response": "No emails in your Share Emails list."}
        else:
            emails_list = '\n'.join([f"- {email}" for email in emails])
            return {"response": f"The emails in your Share Emails list are:\n{emails_list}"}

    print(f"Assistant response: {response['msg']}")
    return {"response": response['msg']}


@router.post('/chats/inactive', tags=["Chats"])
def inactive(new_inactive: InactiveChatRequest, _: str = Depends(verify_secret_key)):
    thread_id = new_inactive.thread_id
    result = WebInactivity.trigger_inactive(thread_id)
    if result is True:
        return {"response": "Are you there?"}
    else:
        # This indicates a conflict, i.e., the operation cannot be performed.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inactive already triggered"
        )

@router.post('/job-info', tags=["Job Info"])
def collect_job_info(job_info: JobInfoRequest, _: str = Depends(verify_secret_key)):
    # Here you can handle the collected job information, such as saving it to the database
    print(f"Received job info: {job_info}")
    # Assuming you have a function to save this data, e.g., save_job_info_to_db(job_info)
    return {"message": "Job information received successfully."}