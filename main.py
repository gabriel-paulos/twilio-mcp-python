from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from twilio.rest import Client

from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

#import pydantic
#from icecream import ic


load_dotenv()

class Credentials(BaseSettings):

  account_sid: str | None = None
  auth_token: str | None = None
  phone_number: Annotated[
    str, 
    BeforeValidator(lambda v: v if v.startswith("+") else f"+{v}")
  ]

  
  model_config: SettingsConfigDict = SettingsConfigDict(
      env_prefix = "TWILIO_",
      env_file = ".env",
      env_file_encoding = "utf-8"
  )


try:  
  credentials = Credentials()
  client = Client(credentials.account_sid, credentials.auth_token)

  mcp = FastMCP(
      name="twilioServer", 
      dependencies=["twilio", "python-dotenv", "pydantic", "typing"],
      description="A server that sends a message using Twilio",
      version="0.0.1"
      )

except Exception as e: 
  print(f"Error: {e}")
  exit(1)


@mcp.tool(name='textme', description='Send a text message using Twilio')
def send_message(to: str=credentials.phone_number, message: str="Hello world"):
  """
  Sends a message to a phone number using Twilio
  """
  try:
    message = client.messages.create(
      messaging_service_sid='MG67808210bf00bd0d6bbfece0cf6075e6',
      body=message,
      to=to
    )
    
    return [
      f"Message sent to {to}",
      message.sid,
    ]
  except Exception as e:
    return[
      f'Error sending message: {e}'
    ]

@mcp.tool(name="msglogs", description="get the message logs for a number")
def get_message_logs(phone_number: str=credentials.phone_number, limit: int=10):
    """
    Retrieves message logs for a specific phone number.
    """
    messages = client.messages.list(to=phone_number, limit=limit)  # Last 10 messages
    
    if not messages:
        print(f"No messages found for {phone_number}")
        return
    
    for msg in messages:
        print(f"SID: {msg.sid} | Status: {msg.status} | Sent At: {msg.date_sent} | Body: {msg.body}")








