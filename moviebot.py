# movie_userbot.py
# Requirements: pip install pyrogram tgcrypto

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# ------------------ CONFIG ------------------
API_ID = 36057028 # your api id
API_HASH = "3ffb94f0e93da47f1a98123d0b77c3ff"
SESSION_STRING = "BQFNtIsANwzAN72uMDmR61FdXvuVy1XWjBoRuleua0Nb-BskYUxVF6prrTqizTNS_Dk341whK55bbfHiS3A12Y4BOp8die8SjZx7_iXR7xug6uGd0IyE8YjZ5YouC1HQZqZno1F4DQ7tCHZn0K7jbi9030lBiEptgAf9ZwhGOw5EApe-AXaPIvfKbqMTVHuiQ3g6KwisfvNOFh5TW-ivXiS9y8Lf_jFwkOhrBKa8gEV0DkSTN-AzsCDiujJFXGZjS3dwS9FsVnKl2unWY2nz3E1KJJlWTY5bXNYqy9ep8wkn1JwnsbnYpahHOLIzYBY4_yCYusNAHgKFBytoA8FoPcuDVvPP7wAAAAH5KUgGAA"
TARGET_BOT = "@iPapkornD2bot"  # bot username

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ APP INIT ------------------
app = Client(
    name="movie_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ------------------ HANDLERS ------------------

@app.on_message(filters.command("movie", prefixes="/") & filters.group)
async def movie_handler(client: Client, message: Message):
    try:
        # extract only movie name (without /movie)
        parts = message.text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            await message.reply_text("🎬 Please write a movie name after /movie (e.g. `/movie leo`)")
            return

        query = parts[1].strip()
        user_mention = message.from_user.mention if message.from_user else "Someone"

        logger.info(f"🎥 {user_mention} requested movie: {query}")

        # optional: let GC know it's processing
        status = await message.reply_text(f"🔎 Searching for **{query}** ...")

        # send only the movie name to bot (no /movie)
        sent = await client.send_message(TARGET_BOT, query)
        logger.info(f"✅ Sent '{query}' to {TARGET_BOT}")

        # wait for the bot's reply
        @app.on_message(filters.chat(TARGET_BOT))
        async def forward_reply(client, bot_reply: Message):
            try:
                if bot_reply.video or bot_reply.photo or bot_reply.document:
                    forwarded = await bot_reply.copy(
                        message.chat.id,
                        caption=f"{user_mention}'s request 🎬 — **{query}**"
                    )
                    await status.delete()
                    logger.info(f"✅ Forwarded result of {query} to GC")

                    # auto delete after 1 min
                    await asyncio.sleep(60)
                    await forwarded.delete()
                    logger.info("🗑️ Deleted video after 1 min")

                elif bot_reply.text:
                    await status.edit_text(f"{user_mention}, {bot_reply.text}")

            except Exception as e:
                logger.error(f"⚠️ Error forwarding reply: {e}")

    except Exception as e:
        logger.error(f"❌ Error in /movie handler: {e}")
        await message.reply_text("⚠️ Something went wrong, please try again.")

# ------------------ START ------------------
print("🚀 Userbot running... Waiting for /movie commands.")
app.run()