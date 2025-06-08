import os
import hashlib
import asyncio
from aiohttp import web, ClientSession
from aiohttp.web_response import StreamResponse
from pyrogram import Client
import logging
from dotenv import load_dotenv

# Load environment variables (for local testing, Koyeb uses its own env vars)
load_dotenv()

logger = logging.getLogger(__name__)

# Environment variables (HARDCODED FOR IMMEDIATE DEPLOYMENT - NOT RECOMMENDED FOR PRODUCTION)
# Please configure these as environment variables in Koyeb for better security.
API_ID = 24385604
API_HASH = "29acdafd1a365dddeffe8a53fb19db3f"
BOT_TOKEN = "8173450714:AAFwzph38DqMpkYUaUu-xkr3UF9bZawvxEY"
LOG_CHANNEL = -1002323311540
BASE_URL = "https://ammu-manu-app.koyeb.app"
SECRET_KEY = "ammumanu"

# Pyrogram client for file access
bot_client = None

def generate_secure_hash(message_id: int, file_name: str) -> str:
    """Generate a secure hash for stream authentication"""
    data = f"{message_id}:{file_name}:{SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def validate_hash(message_id: int, file_name: str, provided_hash: str) -> bool:
    """Validate the provided hash"""
    expected_hash = generate_secure_hash(message_id, file_name)
    return expected_hash == provided_hash

async def watch_handler(request):
    """Handle /watch/{msg_id}/{filename} - Render HTML video player"""
    try:
        msg_id = int(request.match_info["msg_id"])
        filename = request.match_info["filename"]
        provided_hash = request.query.get("hash", "")
        
        # Validate hash
        if not validate_hash(msg_id, filename, provided_hash):
            return web.Response(text="Invalid or missing hash", status=403)
        
        # Generate stream URL
        stream_url = f"{BASE_URL}/{msg_id}/{filename}?hash={provided_hash}"
        
        # Read HTML template
        template_path = os.path.join(os.path.dirname(__file__), "templates", "dl.html")
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError:
            # Fallback to dl.html in root directory
            template_path = os.path.join(os.path.dirname(__file__), "dl.html")
            with open(template_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        
        # Replace placeholders
        html_content = html_content.replace("{{VIDEO_URL}}", stream_url)
        html_content = html_content.replace("{{VIDEO_TITLE}}", filename)
        
        return web.Response(text=html_content, content_type="text/html")
        
    except Exception as e:
        logger.error(f"Error in watch_handler: {e}")
        return web.Response(text="Internal server error", status=500)

async def stream_handler(request):
    """Handle /{msg_id}/{filename} - Stream video file from Telegram"""
    try:
        msg_id = int(request.match_info["msg_id"])
        filename = request.match_info["filename"]
        provided_hash = request.query.get("hash", "")
        
        # Validate hash
        if not validate_hash(msg_id, filename, provided_hash):
            return web.Response(text="Invalid or missing hash", status=403)
        
        # Get the message from LOG_CHANNEL
        try:
            message = await bot_client.get_messages(LOG_CHANNEL, msg_id)
            if not message:
                return web.Response(text="File not found", status=404)
            
            # Get file info
            if message.video:
                file_obj = message.video
            elif message.document:
                file_obj = message.document
            else:
                return web.Response(text="No video file found", status=404)
            
        except Exception as e:
            logger.error(f"Error getting message: {e}")
            return web.Response(text="File not found", status=404)
        
        # Handle range requests for video streaming
        range_header = request.headers.get("Range")
        file_size = file_obj.file_size
        
        if range_header:
            # Parse range header
            range_match = range_header.replace("bytes=", "").split("-")
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1
            
            # Ensure valid range
            start = max(0, start)
            end = min(file_size - 1, end)
            content_length = end - start + 1
            
            # Create partial content response
            response = StreamResponse(
                status=206,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(content_length),
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Access-Control-Allow-Headers": "Range",
                }
            )
            
            await response.prepare(request)
            
            # Stream the file chunk
            async for chunk in bot_client.stream_media(message, offset=start, limit=content_length):
                await response.write(chunk)
            
            await response.write_eof()
            return response
            
        else:
            # Full file response
            response = StreamResponse(
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(file_size),
                    "Accept-Ranges": "bytes",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Access-Control-Allow-Headers": "Range",
                }
            )
            
            await response.prepare(request)
            
            # Stream the entire file
            async for chunk in bot_client.stream_media(message):
                await response.write(chunk)
            
            await response.write_eof()
            return response
            
    except Exception as e:
        logger.error(f"Error in stream_handler: {e}")
        return web.Response(text="Internal server error", status=500)

async def options_handler(request):
    """Handle OPTIONS requests for CORS"""
    return web.Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Range",
        }
    )

async def health_handler(request):
    """Health check endpoint for deployment monitoring"""
    return web.json_response({"status": "healthy", "service": "telegram_video_bot"})

async def start_web_server():
    """Start the aiohttp web server"""
    global bot_client
    
    # Initialize bot client for file access
    bot_client = Client("streamer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    await bot_client.start()
    
    # Create aiohttp application
    app = web.Application()
    
    # Add routes
    app.router.add_get("/health", health_handler)
    app.router.add_get("/watch/{msg_id}/{filename}", watch_handler)
    app.router.add_get("/{msg_id}/{filename}", stream_handler)
    app.router.add_options("/{msg_id}/{filename}", options_handler)
    
    # Start web server
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logger.info(f"Web server started on port {port}")
    
    # Keep the server running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
    except KeyboardInterrupt:
        logger.info("Shutting down web server...")
        await runner.cleanup()
        await bot_client.stop()

