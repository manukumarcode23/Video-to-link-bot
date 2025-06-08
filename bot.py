import os
import hashlib
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
BASE_URL = os.getenv("BASE_URL", "https://your-koyeb-app.koyeb.app")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client.telegram_bot
users_collection = db.users

# Pyrogram client
app = Client("telegram_video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def generate_secure_hash(message_id: int, file_name: str) -> str:
    """Generate a secure hash for stream authentication"""
    secret_key = os.getenv("SECRET_KEY", "default_secret_key_change_this")
    data = f"{message_id}:{file_name}:{secret_key}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"user_id": user_id})
    
    if not existing_user:
        # Save new user to MongoDB
        user_data = {
            "user_id": user_id,
            "first_name": first_name
        }
        await users_collection.insert_one(user_data)
        
        # Log new user to LOG_CHANNEL
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"🆕 New User Joined!\n\n"
                f"👤 Name: {first_name}\n"
                f"🆔 ID: {user_id}"
            )
        except Exception as e:
            logger.error(f"Failed to log new user to channel: {e}")
    
    # Send greeting message
    await message.reply_text(
        f"👋 Hello {first_name}!\n\n"
        f"Welcome to the Video Streaming Bot! 🎬\n\n"
        f"📤 Send me a video file and I'll create a streaming link for you!"
    )

@app.on_message(filters.video | filters.document)
async def handle_video_upload(client: Client, message: Message):
    """Handle video/document uploads"""
    try:
        # Get file info
        if message.video:
            file_obj = message.video
            file_name = file_obj.file_name or f"video_{message.id}.mp4"
        elif message.document:
            file_obj = message.document
            file_name = file_obj.file_name or f"document_{message.id}"
        else:
            return
        
        # Forward to LOG_CHANNEL
        try:
            forwarded_msg = await message.forward(LOG_CHANNEL)
            message_id = forwarded_msg.id
        except Exception as e:
            logger.error(f"Failed to forward to log channel: {e}")
            await message.reply_text("❌ Failed to process the file. Please try again.")
            return
        
        # Generate secure stream link
        secure_hash = generate_secure_hash(message_id, file_name)
        stream_url = f"{BASE_URL}/watch/{message_id}/{file_name}?hash={secure_hash}"
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🖥️ Watch Online", url=stream_url)]
        ])
        
        # Reply with file info and stream link
        await message.reply_text(
            f"✅ File uploaded successfully!\n\n"
            f"📁 File: {file_name}\n"
            f"🔗 Stream link generated!",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error handling video upload: {e}")
        await message.reply_text("❌ An error occurred while processing your file.")

async def main():
    """Main function to start the bot"""
    logger.info("Starting Telegram bot...")
    await app.start()
    logger.info("Bot started successfully!")
    
    # Import and start the web server
    from streamer import start_web_server
    await start_web_server()

if __name__ == "__main__":
    asyncio.run(main())

