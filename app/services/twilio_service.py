import os

from twilio.rest import Client

from dotenv import load_dotenv
load_dotenv()


from_whatsapp_number = 'whatsapp:' + os.environ.get('TWILIO_WHATSAPP_NUMBER')
to_whatsapp_number = 'whatsapp:' + os.environ.get('MY_WHATSAPP_NUMBER')

TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN

client = Client(account_sid, auth_token)