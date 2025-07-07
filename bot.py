import discord
from discord.ext import commands
import asyncio
import aiohttp
import tempfile
import os
import sys
from dotenv import load_dotenv
from openai import AsyncOpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

class AIBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        
        # Validate environment variables
        self.validate_environment()
        
        # Initialize API clients
        openai_key = os.getenv('OPENAI_API_KEY')
        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        
        if openai_key:
            self.openai_client = AsyncOpenAI(api_key=openai_key)
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not found. /ai command will be disabled.")
        
        if elevenlabs_key:
            self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_key)
        else:
            self.elevenlabs_client = None
            logger.warning("ElevenLabs API key not found. Voice functionality will be disabled.")
        
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Default to Bella
        
        # Voice connection storage
        self.voice_connections = {}
    
    def validate_environment(self):
        """Validate that required environment variables are set"""
        required_vars = ['DISCORD_TOKEN']
        optional_vars = ['OPENAI_API_KEY', 'ELEVENLABS_API_KEY', 'ELEVENLABS_VOICE_ID']
        
        missing_required = []
        missing_optional = []
        
        for var in required_vars:
            if not os.getenv(var) or os.getenv(var) == f'your_{var.lower()}_here':
                missing_required.append(var)
        
        for var in optional_vars:
            if not os.getenv(var) or 'your_' in os.getenv(var, ''):
                missing_optional.append(var)
        
        if missing_required:
            logger.error(f"Missing required environment variables: {missing_required}")
            logger.error("Please check your .env file!")
            sys.exit(1)
        
        if missing_optional:
            logger.warning(f"Missing optional environment variables: {missing_optional}")
            logger.warning("Some bot features may be disabled.")
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')

bot = AIBot()

@bot.tree.command(name="ai", description="Chat with AI using OpenAI")
async def ai_command(interaction: discord.Interaction, prompt: str):
    """Handle the /ai slash command"""
    await interaction.response.defer()
    
    # Check if OpenAI client is available
    if not bot.openai_client:
        await interaction.followup.send(
            "❌ OpenAI API is not configured. Please set your OPENAI_API_KEY in the .env file and restart the bot."
        )
        return
    
    try:
        # Call OpenAI API
        response = await bot.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant in a Discord server. Keep responses concise and engaging."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Split long responses to fit Discord's character limit
        if len(ai_response) > 2000:
            chunks = [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(ai_response)
            
    except Exception as e:
        logger.error(f"Error in ai command: {e}")
        await interaction.followup.send(f"Sorry, I encountered an error: {str(e)}")

@bot.tree.command(name="connect", description="Connect to your voice channel for AI voice chat")
async def connect_command(interaction: discord.Interaction):
    """Handle the /connect slash command"""
    await interaction.response.defer()
    
    # Check if required APIs are available
    if not bot.openai_client:
        await interaction.followup.send(
            "❌ OpenAI API is not configured. Please set your OPENAI_API_KEY in the .env file and restart the bot."
        )
        return
    
    if not bot.elevenlabs_client:
        await interaction.followup.send(
            "❌ ElevenLabs API is not configured. Please set your ELEVENLABS_API_KEY in the .env file and restart the bot."
        )
        return
    
    # Check if user is in a voice channel
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("You need to be in a voice channel first!")
        return
    
    voice_channel = interaction.user.voice.channel
    guild_id = interaction.guild.id
    
    try:
        # Connect to voice channel
        if guild_id in bot.voice_connections:
            await bot.voice_connections[guild_id].disconnect()
        
        voice_client = await voice_channel.connect()
        bot.voice_connections[guild_id] = voice_client
        
        await interaction.followup.send(f"Connected to {voice_channel.name}! Use text chat to talk with AI and I'll respond with voice.")
        
        # Set up voice chat session
        await setup_voice_session(interaction.channel, voice_client)
        
    except Exception as e:
        logger.error(f"Error connecting to voice: {e}")
        await interaction.followup.send(f"Failed to connect to voice channel: {str(e)}")

async def setup_voice_session(text_channel, voice_client):
    """Set up a voice chat session"""
    def check_message(message):
        return (message.channel == text_channel and 
                not message.author.bot and 
                voice_client.is_connected())
    
    await text_channel.send("🎤 Voice session started! Type messages and I'll respond with voice. Type 'disconnect' to end the session.")
    
    while voice_client.is_connected():
        try:
            # Wait for user message
            message = await bot.wait_for('message', check=check_message, timeout=300.0)  # 5 minute timeout
            
            if message.content.lower() in ['disconnect', 'stop', 'quit']:
                await voice_client.disconnect()
                await text_channel.send("Voice session ended!")
                break
            
            # Get AI response
            response = await bot.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful voice assistant. Keep responses brief and conversational since this will be spoken aloud."},
                    {"role": "user", "content": message.content}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            ai_text = response.choices[0].message.content
            
            # Generate speech with ElevenLabs
            await generate_and_play_speech(ai_text, voice_client, text_channel)
            
        except asyncio.TimeoutError:
            await text_channel.send("Voice session timed out due to inactivity.")
            await voice_client.disconnect()
            break
        except Exception as e:
            logger.error(f"Error in voice session: {e}")
            await text_channel.send(f"Error: {str(e)}")

async def generate_and_play_speech(text, voice_client, text_channel):
    """Generate speech with ElevenLabs and play it in voice channel"""
    try:
        # Generate audio with ElevenLabs
        audio_generator = bot.elevenlabs_client.generate(
            text=text,
            voice=bot.voice_id,
            model="eleven_monolingual_v1",
            stream=True
        )
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            for chunk in audio_generator:
                temp_file.write(chunk)
            temp_audio_path = temp_file.name
        
        # Convert to opus for Discord
        opus_path = temp_audio_path.replace('.mp3', '.opus')
        
        # Use FFmpeg to convert to opus (Discord's preferred format)
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i', temp_audio_path, '-c:a', 'libopus', '-b:a', '64k', opus_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        # Play audio in voice channel
        if voice_client.is_connected():
            audio_source = discord.FFmpegOpusAudio(opus_path)
            voice_client.play(audio_source)
            
            # Wait for audio to finish
            while voice_client.is_playing():
                await asyncio.sleep(0.1)
        
        # Clean up temporary files
        try:
            os.unlink(temp_audio_path)
            os.unlink(opus_path)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        await text_channel.send(f"Error generating speech: {str(e)}")

@bot.tree.command(name="disconnect", description="Disconnect from voice channel")
async def disconnect_command(interaction: discord.Interaction):
    """Handle the /disconnect slash command"""
    guild_id = interaction.guild.id
    
    if guild_id in bot.voice_connections:
        await bot.voice_connections[guild_id].disconnect()
        del bot.voice_connections[guild_id]
        await interaction.response.send_message("Disconnected from voice channel!")
    else:
        await interaction.response.send_message("I'm not connected to any voice channel!")

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state updates"""
    if member == bot.user:
        return
    
    # If the bot is alone in a voice channel, disconnect
    for guild_id, voice_client in list(bot.voice_connections.items()):
        if voice_client.channel and len(voice_client.channel.members) == 1:
            await voice_client.disconnect()
            del bot.voice_connections[guild_id]

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        exit(1)
    
    bot.run(token)