# 🎬 Advanced Video Queue Processing Bot

A Telegram bot with queue system, automatic delivery, and user authentication for video processing with real-time progress updates.

## ✨ Features

### Core Features:
- **Queue-Based Processing**: Jobs processed in order
- **Automatic Delivery**: Videos delivered when processing completes
- **User Authentication**: Required access control
- **Multi-resolution Compression**: 1080p, 720p, 480p, 360p
- **Large Video Support**: Process videos up to 2GB

### Progress Tracking:
- **Real-time Updates**: 0% → 100% progress tracking
- **Visual Progress Bars**: [████░░░░] style indicators
- **Live Monitoring**: Continuous progress updates
- **Progress Command**: Check current job status

### Queue Management:
- **Fair Processing**: Jobs in order received
- **User Limits**: Configurable queue limits per user
- **Position Tracking**: See your place in queue
- **Job History**: View past processing jobs

### Security Features:
- **User Authorization**: Required access for all users
- **Admin Controls**: Manage authorized users
- **Database Storage**: Persistent job tracking
- **Rate Limiting**: Prevent abuse

## 🚀 Setup

### Prerequisites:
- Python 3.8+
- FFmpeg installed on system
- Telegram API credentials
- Bot token from @BotFather
- Private channel for video storage

### Installation:

1. **Install FFmpeg:**
```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # macOS
   brew install ffmpeg
      # Windows: Download from https://ffmpeg.org/download.html
```

2. **Setup Telegram Channels:**
   - Create a private channel
   - Add your bot as admin
   - Get the channel ID (@userinfobot can help)

3. **Clone and setup:**
```bash
   git clone <your-repo-url>
   cd telegram-video-processor
   pip install -r requirements.txt
```

4. **Get API Credentials:**
   - Go to https://my.telegram.org
   - Create an application to get API_ID and API_HASH

5. **Create Bot Token:**
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Get your bot token

6. **Set Environment Variables:**
```bash
   # Create .env file with:
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   UPLOAD_CHANNEL_ID=your_private_channel_id
   AUTHORIZED_USERS=123456789,987654321  # User IDs comma-separated
   ADMIN_USERS=123456789  # Admin user IDs
   REQUIRE_AUTHENTICATION=true
```

## 📋 Commands

- `/start` - Show welcome message and features
- `/help` - Get detailed help information
- `/info` - Get video information (reply to video)
- `/queue` - Check your position in processing queue
- `/jobs` - View your recent processing jobs
- `/progress` - Check current job progress

## 🛠️ Configuration

Edit `config.py` to customize:
- Maximum file sizes
- Queue limits per user- Concurrent processing limits
- Supported resolutions
- Authentication settings

## 🚀 Deployment

### Local Run:
```bash
python app.py
```

### Render.com:
1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Add environment variables

### Koyeb:
1. Create new Application
2. Select Git source
3. Set runtime to Python
4. Configure environment variables
5. Deploy

## 🔧 Admin Commands

Admin users can manage the bot:
- Add/remove authorized users
- Monitor queue status
- View all jobs across users

## 📊 Performance

- **Memory Usage**: Optimized for minimal RAM usage
- **Processing Speed**: Concurrent processing with limits
- **Scalability**: Queue system prevents overload
- **Free Hosting**: Designed for free tier usage

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License

MIT License - See LICENSE file for details.
## 🆘 Support

For issues and support, create an issue on GitHub.
