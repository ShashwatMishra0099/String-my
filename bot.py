import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Fetching environment variables from Heroku
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Create the bot client
bot = Client("string_session_bot", bot_token=BOT_TOKEN)

# Dictionary to track user states
user_states = {}

# Command to start the session generation
@bot.on_message(filters.command("start_session"))
async def start_session(client, message: Message):
    user_states[message.from_user.id] = "awaiting_phone"
    await message.reply("Please enter your phone number to start generating the session string:")

@bot.on_message(filters.private)
async def handle_input(client, message: Message):
    user_id = message.from_user.id

    if user_id in user_states and user_states[user_id] == "awaiting_phone":
        phone_number = message.text.strip()
        user_states[user_id] = "awaiting_code"  # Change state to awaiting code

        # Initiate the client for generating the string session
        async with Client(":memory:", api_id=API_ID, api_hash=API_HASH) as user_client:
            try:
                # Start the login process with the provided phone number
                await user_client.send_code(phone_number)
                await message.reply("Please enter the code sent to your phone number:")

                # Store the user's phone number for later use
                user_states[user_id] = {"state": "awaiting_code", "phone": phone_number, "client": user_client}

            except Exception as e:
                await message.reply(f"Error: {str(e)}")

    elif user_id in user_states and user_states[user_id]["state"] == "awaiting_code":
        code = message.text.strip()
        user_client = user_states[user_id]["client"]
        phone_number = user_states[user_id]["phone"]

        try:
            # Complete the login with the OTP
            await user_client.sign_in(phone_number, code)
            string_session = await user_client.export_session_string()

            # Send the generated string session to the user's Saved Messages
            session_message = (
                f"Here is your session string:\n`{string_session}`\n\n\n\n"
                "BOT DEVELOP BY SMX\n"
                "@ShashwatSMX"
            )
            await user_client.send_message("me", session_message)

            # Notify the user in the current chat that the session string has been sent to their Saved Messages
            await message.reply("Your session string has been sent to your Saved Messages!", quote=True)

            # Clear the user's state
            del user_states[user_id]

        except Exception as e:
            await message.reply(f"Error: {str(e)}")

    else:
        await message.reply("I didn't understand that. Please use /start_session to begin.")

# Start the bot
bot.run()
