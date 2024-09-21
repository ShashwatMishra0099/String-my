from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import time

API_ID = 28165213  # Your API ID
API_HASH = "74983137f88bb852802637dadf3d44a3"  # Your API Hash
BOT_TOKEN = "7397084299:AAGzcPONLSvrdlHNYiQBsJXEV3TwGdPu_aY"  # Your Bot Token
PHONE_NUMBER = None  # This will be set when the user provides their phone number

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_client = Client("user_session", api_id=API_ID, api_hash=API_HASH)  # User session for OTP handling

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply("Welcome! Please send your phone number in the format: +91XXXXXXXXXX")

@app.on_message(filters.text)
def get_otp(client, message):
    global PHONE_NUMBER
    if message.text.startswith("+91") and len(message.text) == 13:  # +91 followed by 10 digits
        PHONE_NUMBER = message.text
        user_client.start()  # Start the user client to send OTP
        user_client.send_code_request(PHONE_NUMBER)  # Request the OTP
        message.reply("OTP sent! Please enter the OTP you received.")
    else:
        message.reply("Please send your phone number in the format: +91XXXXXXXXXX")

@app.on_message(filters.text & filters.user(PHONE_NUMBER))
def verify_otp(client, message):
    try:
        user_client.sign_in(PHONE_NUMBER, message.text)  # Verify the OTP
        string_session = user_client.export_session_string()  # Generate string session
        message.reply(f"Your String Session is:\n{string_session}")  # Send the session string back
    except FloodWait as e:
        time.sleep(e.x)  # Handle rate limits
        message.reply("You're being rate limited. Please try again later.")
    except Exception as e:
        message.reply(f"An error occurred: {str(e)}")
    finally:
        user_client.stop()  # Stop the user client after the session is generated

app.run()
