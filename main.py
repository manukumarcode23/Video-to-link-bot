import os
import json
import hashlib
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
import aiohttp_jinja2
import jinja2
from datetime import datetime

# Environment variables
API_ID = 7475468
API_HASH = "58gyr7e85h77"
BOT_TOKEN = "8385442:8387ht73465"
LOG_CHANNEL = -10072855235
BASE_URL = os.getenv("BASE_URL", "https://yourdomain.com")
PORT = int(os.getenv("PORT", 8080))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client
app = Client("video_stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# JSON file for user storage
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_user(user_id, first_name):
    users = load_users()
    if not any(user["id"] == user_id for user in users):
        users.append({"id": user_id, "name": first_name})
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return True
    return False

def get_hash(message_id, filename):
    return hashlib.md5(f"{message_id}{filename}{BOT_TOKEN}".encode()).hexdigest()

async def send_to_log_channel(client, message, user_id, first_name=None):
    if first_name:
        # Log new user
        await client.send_message(
            LOG_CHANNEL,
            f"New user: {first_name} (ID: {user_id}) joined at {datetime.now()}"
        )
    else:
        # Forward video to log channel
        return await message.forward(LOG_CHANNEL)

# /start command handler
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    if save_user(user_id, first_name):
        await send_to_log_channel(client, message, user_id, first_name)
    await message.reply(
        f"Hello {first_name}! 👋 Send me a video, and I'll give you a streaming link."
    )

# Video/Document handler
@app.on_message(filters.video | filters.document & filters.private)
async def handle_video(client, message):
    user_id = message.from_user.id
    file_name = message.video.file_name if message.video else message.document.file_name
    if not file_name:
        file_name = f"video_{message.id}.mp4"

    # Forward to log channel
    forwarded = await send_to_log_channel(client, message, user_id)
    message_id = forwarded.id
    hash_value = get_hash(message_id, file_name)
    stream_url = f"{BASE_URL}/watch/{message_id}/{file_name}?hash={hash_value}"

    # Reply with streaming link
    await message.reply(
        f"🎥 **{file_name}**\n\nStream your video:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🖥️ Watch Online", url=stream_url)]
        ])
    )

# ByteStreamer class for streaming
class ByteStreamer:
    def __init__(self, client: Client):
        self.client = client

    async def get_file_properties(self, message_id):
        message = await self.client.get_messages(LOG_CHANNEL, message_id)
        if message.video:
            return message.video.file_id, message.video.file_size
        elif message.document:
            return message.document.file_id, message.document.file_size
        return None, None

    async def stream(self, message_id: int, _: str):
        file_id, file_size = await self.get_file_properties(message_id)
        if not file_id:
            return Response(status=404, text="File not found")

        headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
        }
        return Response(
            body=await self.client.stream_media(file_id),
            status=200,
            headers=headers
        )

# Web server routes
async def watch_handler(request: Request):
    message_id = request.match_info["msg_id"]
    filename = request.match_info["filename"]
    hash_value = request.query.get("hash")
    expected_hash = get_hash(message_id, filename)
    if hash_value != expected_hash:
        return web.Response(status=403, text="Invalid hash")
    context = {"stream_url": f"/{message_id}/{filename}"}
    return aiohttp_jinja2.render_template("dl.html", request, context)

async def stream_handler(request: Request):
    message_id = request.match_info["msg_id"]
    filename = request.match_info["filename"]
    streamer = ByteStreamer(app)
    return await streamer.stream(int(message_id), filename)

# Run bot and web server
if __name__ == "__main__":
    import asyncio
    async def main():
        await app.start()
        runner = web.AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"Web server running on port {PORT}")
        try:
            await asyncio.Event().wait()
        finally:
            await runner.cleanup()
            await app.stop()

    asyncio.run(main())
