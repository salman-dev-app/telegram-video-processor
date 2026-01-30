# 🎬 **Telegram Video Processing Bot**
*A powerful video compression bot with queue system and progress tracking*

## ✨ **Features**

### **Core Features:**
- **Multi-resolution Compression**: 1080p, 720p, 480p, 360p
- **Large File Support**: Process videos up to 2GB
- **Queue System**: Multiple jobs processed in order
- **Real-time Progress**: Live 0% → 100% updates
- **Channel Integration**: Stores processed videos in private channel
- **Automatic Delivery**: Sends processed videos when complete

### **Advanced Features:**
- **User Authentication**: Control who can use the bot
- **Admin Controls**: Manage authorized users
- **Database Storage**: SQLite for persistent job tracking
- **Memory Efficient**: Optimized for VPS environments
- **Error Recovery**: Automatic retry and cleanup

## 🚀 **Prerequisites**

### **System Requirements:**
- **Operating System**: Windows 10/11, Windows Server 2019/2022
- **RAM**: Minimum 4GB (8GB recommended for 2GB files)
- **Storage**: 50GB free space (for temp files)
- **Internet**: Stable broadband connection
- **Python**: 3.8 or higher

### **Software Requirements:**
- **Python 3.8+** (with "Add to PATH" enabled)
- **Git for Windows** (for cloning repository)
- **FFmpeg** (for video processing)

## 📋 **Installation Guide**

### **Step 1: Install Required Software**
1. **Install Python 3.9+**
   - Download from [python.org](https://python.org)
   - Check "Add Python to PATH" during installation

2. **Install Git**
   - Download from [git-scm.com](https://git-scm.com)
   - Use default settings during installation

3. **Install FFmpeg**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract and add to system PATH

### **Step 2: Clone Repository**
```cmd
cd C:\Users\Administrator\Desktop
git clone https://github.com/salman-dev-app/telegram-video-processor.git
cd telegram-video-processor
```

### **Step 3: Install Dependencies**
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 4: Get Telegram Credentials**
1. **Get API ID and Hash**
   - Visit [my.telegram.org](https://my.telegram.org)
   - Login with your phone number
   - Click "API Development Tools"
   - Create new application and save credentials

2. **Create Bot Token**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Use `/newbot` command
   - Follow instructions to create bot
   - Save the bot token

3. **Create Private Channel**
   - Create a new private channel on Telegram
   - Add your bot as administrator
   - Get the channel ID (use @userinfobot to find it)

### **Step 5: Configure Environment**
Create `.env` file with your credentials:
```
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
UPLOAD_CHANNEL_ID=your_private_channel_id_here
AUTHORIZED_USERS=comma,separated,user,ids
ADMIN_USERS=your_user_id
REQUIRE_AUTHENTICATION=true
MAX_FILE_SIZE=2147483648
MAX_CONCURRENT_PROCESSES=2
QUEUE_LIMIT_PER_USER=5
```

## ⚙️ **Configuration Options**

### **Environment Variables:**
| Variable | Description | Default |
|----------|-------------|---------|
| `API_ID` | Your Telegram API ID | Required |
| `API_HASH` | Your Telegram API Hash | Required |
| `BOT_TOKEN` | Your Bot Token from @BotFather | Required |
| `UPLOAD_CHANNEL_ID` | Private channel ID for storage | Required |
| `AUTHORIZED_USERS` | Comma-separated user IDs | Empty (open access) |
| `ADMIN_USERS` | Admin user IDs | Empty |
| `REQUIRE_AUTHENTICATION` | Require user authorization | false |
| `MAX_FILE_SIZE` | Maximum file size in bytes | 2147483648 (2GB) |
| `MAX_CONCURRENT_PROCESSES` | Number of simultaneous processes | 2 |
| `QUEUE_LIMIT_PER_USER` | Max jobs per user | 5 |

### **Resolution Settings:**
- **1080p**: 1920x1080, 8M bitrate (highest quality)
- **720p**: 1280x720, 5M bitrate (good balance)
- **480p**: 854x480, 3M bitrate (smaller file)
- **360p**: 640x360, 1.5M bitrate (smallest file)

## 🚀 **Running the Bot**

### **Method 1: Direct Run**
```cmd
python app.py
```

### **Method 2: Using Batch File**
Double-click `start_bot.bat`

### **Method 3: As Windows Service** (Advanced)
```cmd
# Install as service (requires additional setup)
python install_service.py
```

## 🤖 **Bot Commands**

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message and features |
| `/help` | Display help information |
| `/info` | Get video information (reply to video) |
| `/queue` | Check your position in queue |
| `/jobs` | View your recent jobs |
| `/progress` | Check current job progress |

## 📊 **Usage Statistics**

### **Performance Metrics:**
- **Processing Speed**: 2-5x faster than real-time
- **Memory Usage**: 200-800MB depending on file size
- **CPU Usage**: 20-80% during processing
- **Storage**: Temp files cleared automatically

### **Supported Formats:**
- MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP

## 🔧 **Troubleshooting**

### **Common Issues:**

**Q: ModuleNotFoundError: No module named 'pyrogram'**
A: Run `pip install -r requirements.txt`

**Q: FFmpeg not found**
A: Install FFmpeg and add to system PATH

**Q: Bot not responding**
A: Check internet connection and API credentials

**Q: Large files failing**
A: Verify available disk space and MAX_FILE_SIZE setting

**Q: Processing stuck**
A: Restart the bot and check temp directory

### **Log Files:**
- Check `bot.log` for detailed error information
- Review recent entries for troubleshooting

## 🔒 **Security Features**

### **User Management:**
- Optional authentication system
- Authorized user lists
- Admin controls
- Queue limits per user

### **Data Protection:**
- Temporary files auto-deleted
- No sensitive data stored
- Secure API credential handling

## 🛠️ **Maintenance**

### **Regular Tasks:**
- Monitor disk space (clean temp directory)
- Check bot logs for errors
- Update dependencies regularly
- Backup database if needed

### **Backup Strategy:**
- Database: `database.db` file
- Configuration: `.env` file
- Logs: Regular cleanup recommended

## 🆘 **Support**

### **Getting Help:**
- Check logs for error details
- Verify all configuration settings
- Ensure all dependencies are installed
- Contact via GitHub issues

### **Contributing:**
- Fork the repository
- Create feature branch
- Submit pull request
- Follow coding standards

## 📄 **License**

MIT License - See LICENSE file for details.

---

**Made with ❤️ for the Telegram community**

*Last updated: January 2026*
