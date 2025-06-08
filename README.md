# Telegram Video Bot for Koyeb

A powerful Telegram bot that allows users to upload videos and stream them through a web interface. Built with Pyrogram, aiohttp, and MongoDB Atlas, optimized for deployment on Koyeb.

## 🚀 Features

- **Video Upload**: Accept video files and documents via Telegram
- **Secure Streaming**: Generate secure streaming links with hash validation
- **Web Player**: Modern HTML5 video player with Plyr integration
- **Mobile Support**: Responsive design with touch controls
- **User Management**: MongoDB integration for user tracking
- **Logging**: Automatic logging of new users and uploads to a designated channel

## 📋 Prerequisites

1. **Telegram Bot**: Create a bot via [@BotFather](https://t.me/BotFather)
2. **Telegram API**: Get API credentials from [my.telegram.org](https://my.telegram.org)
3. **MongoDB Atlas**: Create a free cluster at [mongodb.com](https://www.mongodb.com/atlas)
4. **Koyeb Account**: Sign up at [koyeb.com](https://www.koyeb.com)
5. **Log Channel**: Create a Telegram channel for logging

## 🛠️ Setup Instructions

### 1. Clone/Download the Project

Download all project files to your local machine or clone from your repository.

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```env
# Telegram Bot Configuration
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Telegram Channel for logging (use channel ID with -100 prefix)
LOG_CHANNEL=-1001234567890

# Base URL for your Koyeb deployment
BASE_URL=https://your-koyeb-app.koyeb.app

# MongoDB Atlas Connection String
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database_name

# Secret key for hash generation (change this to a random string)
SECRET_KEY=your_super_secret_key_change_this

# Port (Koyeb will set this automatically)
PORT=8080
```

### 3. Get Required Credentials

#### Telegram API Credentials:
1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy `API_ID` and `API_HASH`

#### Bot Token:
1. Message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the bot token

#### Log Channel ID:
1. Create a new Telegram channel
2. Add your bot as an administrator
3. Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
4. Copy the channel ID (should start with -100)

#### MongoDB Atlas:
1. Create account at [mongodb.com](https://www.mongodb.com/atlas)
2. Create a new cluster (free tier available)
3. Create a database user
4. Get connection string from "Connect" → "Connect your application"

### 4. Deploy to Koyeb

#### Option A: GitHub Deployment (Recommended)

1. Push your code to a GitHub repository
2. Go to [Koyeb Dashboard](https://app.koyeb.com)
3. Click "Create App"
4. Select "GitHub" as source
5. Choose your repository
6. Configure build settings:
   - **Build command**: `pip install -r requirements.txt`
   - **Run command**: `python bot.py`
   - **Port**: `8080`
7. Add environment variables in the "Environment" section
8. Deploy!

#### Option B: Docker Deployment

1. Ensure Docker is installed locally
2. Build and push to a container registry:
   ```bash
   docker build -t your-username/telegram-video-bot .
   docker push your-username/telegram-video-bot
   ```
3. In Koyeb, select "Docker" as source
4. Enter your image name
5. Add environment variables
6. Deploy!

### 5. Update Base URL

After deployment, update the `BASE_URL` environment variable in Koyeb with your actual app URL:
```
BASE_URL=https://your-app-name.koyeb.app
```

## 📁 Project Structure

```
telegram_video_bot/
├── bot.py              # Main bot application
├── streamer.py         # Web server for video streaming
├── templates/
│   └── dl.html         # Video player template
├── dl.html             # Fallback template
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🎯 Usage

1. Start a chat with your bot
2. Send `/start` to register
3. Upload a video file
4. Click "🖥️ Watch Online" to stream the video
5. Share the link with others (they don't need Telegram)

## 🔧 Technical Details

### Tech Stack:
- **Bot Framework**: Pyrogram (async Telegram client)
- **Web Server**: aiohttp (async HTTP server)
- **Database**: MongoDB Atlas (cloud database)
- **Video Player**: Plyr (modern HTML5 player)
- **Deployment**: Koyeb (serverless platform)

### Security Features:
- Hash-based authentication for stream links
- No direct file access without valid hash
- User data stored securely in MongoDB
- CORS protection for web endpoints

### Performance Features:
- Byte-range streaming support
- Async/await throughout the codebase
- CDN-like streaming through Telegram
- Responsive design for all devices

## 🐛 Troubleshooting

### Common Issues:

1. **Bot not responding**: Check bot token and API credentials
2. **Videos not loading**: Verify LOG_CHANNEL ID and bot permissions
3. **Database errors**: Check MongoDB connection string
4. **Deployment fails**: Ensure all environment variables are set

### Logs:
Check Koyeb logs in the dashboard for detailed error messages.

### Health Check:
Visit `https://your-app.koyeb.app/health` to verify the service is running.

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Koyeb deployment logs
3. Verify all environment variables are correctly set
4. Ensure MongoDB Atlas allows connections from all IPs (0.0.0.0/0)

## 🔄 Updates

To update your deployment:
1. Push changes to your GitHub repository
2. Koyeb will automatically redeploy
3. Or rebuild and push your Docker image

---

**Happy streaming! 🎬**

