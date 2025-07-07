import discord
from discord.ext import commands
import asyncio
import aiohttp
import json
import os
import sys
from dotenv import load_dotenv
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
        
        # Voice connection storage (kept for potential future use)
        self.voice_connections = {}
        
        # Free AI models to try (no API key required for basic use)
        self.ai_models = [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill",
            "microsoft/DialoGPT-small"
        ]
        self.current_model = self.ai_models[0]
    
    def validate_environment(self):
        """Validate that required environment variables are set"""
        required_vars = ['DISCORD_TOKEN']
        
        missing_required = []
        
        for var in required_vars:
            if not os.getenv(var) or os.getenv(var) == f'your_{var.lower()}_here':
                missing_required.append(var)
        
        if missing_required:
            logger.error(f"Missing required environment variables: {missing_required}")
            logger.error("Please check your .env file!")
            sys.exit(1)
        
        logger.info("✅ Using free AI chatbot - no API keys required!")
    
    async def get_ai_response(self, prompt: str) -> str:
        """Get AI response using a simple rule-based system and free alternatives"""
        
        # Simple built-in responses for common queries
        simple_responses = {
            "hello": "Hello! I'm your friendly Discord AI bot. How can I help you today?",
            "hi": "Hi there! What would you like to chat about?",
            "how are you": "I'm doing great! Thanks for asking. How are you?",
            "what's your name": "I'm an AI chatbot created to help you in this Discord server!",
            "help": "I can chat with you! Try asking me questions or just have a conversation. Use /ai followed by your message!",
            "thank you": "You're welcome! I'm happy to help anytime!",
            "thanks": "You're welcome! Feel free to ask me anything else!",
            "bye": "Goodbye! Have a wonderful day!",
            "goodbye": "See you later! It was nice chatting with you!",
        }
        
        # Check for simple responses first
        prompt_lower = prompt.lower().strip()
        for key, response in simple_responses.items():
            if key in prompt_lower:
                return response
        
        # For more complex responses, try to use Hugging Face's free inference
        try:
            return await self.try_huggingface_api(prompt)
        except Exception as e:
            logger.warning(f"Free AI API failed: {e}")
            return await self.generate_contextual_response(prompt)
    
    async def try_huggingface_api(self, prompt: str) -> str:
        """Try to use Hugging Face's free inference API"""
        headers = {
            "Content-Type": "application/json",
        }
        
        # Try different models
        for model in self.ai_models:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api-inference.huggingface.co/models/{model}"
                    payload = {"inputs": prompt}
                    
                    async with session.post(url, headers=headers, json=payload, timeout=10) as response:
                        if response.status == 200:
                            result = await response.json()
                            if isinstance(result, list) and len(result) > 0:
                                if 'generated_text' in result[0]:
                                    text = result[0]['generated_text']
                                    # Clean up the response
                                    if text.startswith(prompt):
                                        text = text[len(prompt):].strip()
                                    return text[:500] if text else "I'm thinking about that..."
                            elif isinstance(result, dict) and 'generated_text' in result:
                                text = result['generated_text']
                                if text.startswith(prompt):
                                    text = text[len(prompt):].strip()
                                return text[:500] if text else "I'm thinking about that..."
            except Exception as e:
                logger.debug(f"Model {model} failed: {e}")
                continue
        
        # If all models fail, fall back to contextual response
        raise Exception("All free AI models unavailable")
    
    async def generate_contextual_response(self, prompt: str) -> str:
        """Generate a contextual response when APIs are unavailable"""
        prompt_lower = prompt.lower()
        
        # Question responses
        if "?" in prompt:
            if any(word in prompt_lower for word in ["what", "how", "why", "when", "where", "who"]):
                return f"That's an interesting question about '{prompt[:50]}...'. I'd need to think more about that! What do you think?"
            else:
                return "I'm not sure about that specific question, but I'd love to help you explore it further!"
        
        # Opinion or discussion
        if any(word in prompt_lower for word in ["think", "believe", "opinion", "feel"]):
            return "That's a thoughtful perspective! I'd love to hear more about your thoughts on this topic."
        
        # Problem-solving
        if any(word in prompt_lower for word in ["problem", "issue", "help", "stuck", "difficult"]):
            return "It sounds like you're working through something challenging. Sometimes it helps to break things down into smaller steps. What's the main part you're focusing on?"
        
        # Creative or fun topics
        if any(word in prompt_lower for word in ["story", "joke", "fun", "creative", "imagine"]):
            return "I love creative conversations! While I'm a simple bot, I think the best ideas come from collaboration. What's your take on this?"
        
        # Default conversational response
        responses = [
            f"That's interesting! Tell me more about '{prompt[:30]}...'",
            "I find that topic fascinating! What got you thinking about that?",
            "That's a great point to discuss! What's your perspective on it?",
            "I'd love to explore that idea with you! What aspects interest you most?",
            "That's something worth talking about! How did you come across this topic?"
        ]
        
        import random
        return random.choice(responses)
        
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

@bot.tree.command(name="ai", description="Chat with AI - completely free, no API keys needed!")
async def ai_command(interaction: discord.Interaction, prompt: str):
    """Handle the /ai slash command"""
    await interaction.response.defer()
    
    try:
        # Get AI response using our free method
        ai_response = await bot.get_ai_response(prompt)
        
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
        await interaction.followup.send("Sorry, I'm having trouble thinking right now. Try asking me something else!")

@bot.tree.command(name="info", description="Learn about this free AI chatbot")
async def info_command(interaction: discord.Interaction):
    """Handle the /info slash command"""
    embed = discord.Embed(
        title="🤖 Free AI Chatbot", 
        description="A completely free Discord AI bot - no API keys required!",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🆓 Features",
        value="• Free AI chat using `/ai`\n• Built-in conversational responses\n• No API costs or limits\n• Works immediately after setup",
        inline=False
    )
    
    embed.add_field(
        name="💬 How to Use",
        value="Just type `/ai` followed by your message!\nExample: `/ai Hello, how are you?`",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Technology",
        value="Uses free Hugging Face models when available,\nwith smart fallback responses",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Perfect For",
        value="• Casual conversations\n• Learning Discord bots\n• No-cost AI experimentation\n• Community engagement",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# Voice functionality removed - this is now a text-only free AI chatbot
# To add voice back, you would need paid APIs like OpenAI + ElevenLabs

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        exit(1)
    
    bot.run(token)