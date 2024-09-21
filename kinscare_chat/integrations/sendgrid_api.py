import os
from urllib.parse import quote

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From

PLAN_SHARE_TEMPLATE = "d-0b96653b788245ffa8ab5f33dbaccb0d"

class SendGridApi:

    @classmethod
    def send_plan_share_email(cls, to_emails: list, content, name):
        print(f"Content: {content}")
        # create Mail object and populate
        message = Mail(
            from_email=From("feedback@kinscare.org", name),
            to_emails=to_emails)
        # pass custom values for our HTML placeholders
        message.dynamic_template_data = {
            'content': content
        }
        message.template_id = PLAN_SHARE_TEMPLATE
        # create our sendgrid client object, pass it our key, then send and return our response objects
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            code, body, headers = response.status_code, response.body, response.headers
            print("Dynamic Messages Sent!")
        except Exception as e:
            print("Error: {0}".format(e))
        return str(response.status_code)
