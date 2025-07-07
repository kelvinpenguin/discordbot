# Discord AI Voice Bot

A Discord bot with AI text and voice capabilities using OpenAI and ElevenLabs.

## Features

- `/ai` - Chat with AI using OpenAI's GPT models
- `/connect` - Connect to voice channels for AI voice conversations
- `/disconnect` - Disconnect from voice channels
- Automatic voice session management
- Text-to-speech using ElevenLabs
- Supports multiple servers simultaneously

## Setup

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- Discord Application/Bot Token
- OpenAI API Key
- ElevenLabs API Key

### Installation

1. **Clone and setup the project:**
   ```bash
   git clone <your-repo>
   cd discord-ai-bot
   pip install -r requirements.txt
   ```

2. **Install FFmpeg:**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   Download from https://ffmpeg.org/download.html

3. **Create Discord Application:**
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the bot token
   - Under "Privileged Gateway Intents", enable:
     - Message Content Intent
     - Server Members Intent

4. **Get API Keys:**
   - **OpenAI:** Get your API key from https://platform.openai.com/api-keys
   - **ElevenLabs:** Get your API key from https://elevenlabs.io/
   - **ElevenLabs Voice ID:** Find voice IDs at https://elevenlabs.io/voice-library

5. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and tokens
   ```

6. **Invite Bot to Server:**
   - Go to OAuth2 > URL Generator in Discord Developer Portal
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: 
     - Send Messages
     - Use Slash Commands
     - Connect
     - Speak
     - Use Voice Activity
   - Use the generated URL to invite the bot

### Running the Bot

```bash
python bot.py
```

## Usage

### Text AI Chat
Use `/ai <your message>` to chat with the AI in text form.

**Example:**
```
/ai What's the weather like in space?
```

### Voice AI Chat
1. Join a voice channel
2. Use `/connect` to have the bot join your channel
3. Type messages in the text channel - the bot will respond with voice
4. Type "disconnect", "stop", or "quit" to end the voice session
5. Or use `/disconnect` to manually disconnect

**Features:**
- Automatic timeout after 5 minutes of inactivity
- Bot automatically leaves if alone in voice channel
- Supports multiple servers simultaneously

## Configuration

### Environment Variables

- `DISCORD_TOKEN` - Your Discord bot token
- `OPENAI_API_KEY` - Your OpenAI API key
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key
- `ELEVENLABS_VOICE_ID` - Voice ID from ElevenLabs (optional, defaults to Bella)

### Customization

You can modify the following in `bot.py`:

- **AI Model:** Change `gpt-3.5-turbo` to `gpt-4` or other models
- **Voice Settings:** Modify ElevenLabs voice parameters
- **Response Length:** Adjust `max_tokens` parameter
- **Timeout Duration:** Change the 300-second timeout in voice sessions

## Troubleshooting

### Common Issues

1. **"FFmpeg not found"**
   - Install FFmpeg using the instructions above
   - Ensure FFmpeg is in your system PATH

2. **"Bot not responding to slash commands"**
   - Wait a few minutes after inviting the bot (commands need to sync)
   - Check bot permissions in your Discord server

3. **"Voice connection fails"**
   - Ensure bot has Connect and Speak permissions
   - Check if voice channel has user limits

4. **"API errors"**
   - Verify your API keys are correct and have sufficient credits
   - Check API rate limits

### Logs

The bot logs important events and errors. Check the console output for debugging information.

## Development

### Project Structure

```
discord-ai-bot/
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .env              # Your actual environment variables (not in git)
└── README.md         # This file
```

### Adding Features

The bot is built with discord.py and uses async/await patterns. Key components:

- **Slash Commands:** Use `@bot.tree.command()` decorator
- **Voice Handling:** Discord voice clients and FFmpeg for audio
- **AI Integration:** OpenAI async client for chat completions
- **TTS Integration:** ElevenLabs client for text-to-speech

## License

MIT License - feel free to modify and distribute!