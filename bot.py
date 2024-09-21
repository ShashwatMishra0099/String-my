import os
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message

# Fetching environment variables from Heroku
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Create the bot client
bot = Client("string_session_bot", bot_token=BOT_TOKEN)

# Command to start the session generation
@bot.on_message(filters.command("start_session"))
async def start_session(client, message: Message):
    await message.reply("Please enter your phone number to start generating the session string:")

    # Wait for phone number input from the user
    response = await bot.listen(message.chat.id, timeout=120)
    phone_number = response.text.strip()

    # Initiate the client for generating the string session
    async with Client(":memory:", api_id=API_ID, api_hash=API_HASH) as user_client:
        try:
            # Start the login process with the provided phone number
            await user_client.send_code(phone_number)
            await message.reply("Please enter the code sent to your phone number:")

            # Wait for the OTP code input
            response = await bot.listen(message.chat.id, timeout=120)
            code = response.text.strip()

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

        except Exception as e:
            await message.reply(f"Error: {str(e)}")

# Start the bot
bot.run()
