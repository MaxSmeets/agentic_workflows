import json
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from modules.ai_modules.models.deepseek import conversational_prompt, json_prompt
from modules.ai_modules.speech_to_text import transcribe_audio

# Load environment variables
load_dotenv()

GUILD = os.getenv('DISCORD_GUILD_ID')  # Add guild ID to .env

# Bot setup
intents = discord.Intents.default()  # Adjust intents based on functionality
intents.messages = True  # Enable message-related events
intents.message_content = True  # Needed to read message content
bot = commands.Bot(command_prefix="!", intents=intents)

hierarchy = '''
**Hierarchy**
Apricot Labs exists of:
- *owner*: Max, founder of Apricot Labs
- *executive director*: Luna
- *research manager*: Eric
- *communication manager*: Grace
- *project manager*: Sam
'''

# Commands
@bot.command(name='workforce')
async def show_workforce(ctx):
    await ctx.send(hierarchy)

# Events
@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == bot.user:
        return

    # Ensure commands still work
    await bot.process_commands(message)

    # Check if the message is from the correct guild
    if message.guild.id != int(GUILD):
        print("Unauthorized guild")
        return

    # Print the message content for debugging
    print(str(message.content))

    # Process attachments
    if message.attachments:
        for attachment in message.attachments:
            # Check if the attachment is an audio file (e.g., .ogg, .mp3)
            if attachment.filename.endswith(('.ogg', '.mp3', '.wav')):
                # Save the file to the local project directory
                file_path = f"{attachment.filename}"
                await attachment.save(file_path)
                print(f"Downloaded voice message: {file_path}")
                transcription = transcribe_audio(file_path, 'tiny')
                text = transcription.get('text')
                #evaluate transribed message
                await evaluate_message(text, message.channel)
                os.remove(file_path)
                return

    # Process non-command messages
    if not message.content.startswith("!"):
        await evaluate_message(message.content, message.channel)


def conversation_from_message(message, system_prompt):
    messages = [
        {
            "role": "user",
            "content": message
        }
    ]
    results = conversational_prompt(messages=messages, system_prompt=system_prompt)
    return results

async def evaluate_message(message, channel):
    system_prompt = '''
                    You are gonna analyse the intent of an input prompt.

                    - You will explicitly return a list of dictionaries containing content and intent.
                    - Valid intent are:
                        - general
                        - delegate_tasks
                    - General is only used for general questions about apricot labs and about the workforce itself.
                    

                    **output format**
                    [
                        {
                            "content": "part of the prompt relevant to the intent",
                            "intent": "type of intent"
                        }
                    ]
                    '''
    # Get the JSON string response
    json_response = conversation_from_message(message, system_prompt)
    
    # Clean the response by removing markdown code blocks
    cleaned_response = json_response.strip().replace('```json\n', '').replace('```', '').replace('\n', '')
    
    try:
        # Parse the JSON string into a Python list
        results = json.loads(cleaned_response)
        print("Parsed results:", results)

        # Process the results
        for result in results:
            intent = result.get("intent")
            content = result.get("content")
            
            print(f"Processing intent: {intent}, content: {content}")
            
            if intent == "general":
                system_prompt = f'''
                You are Luna, the executive director of Apricot Labs. You like to communicate in a concise and friendly manner. Always being straight to the point.
                You have knowledge of Apricot Labs' hierarchy: 
                {hierarchy}

                **Instructions**
                - Workers under you cannot be contacted directly by the user, you will offer to pass a message to them.
                '''
                response = conversation_from_message(message=content, system_prompt=system_prompt)
                await channel.send(response)
            elif intent == "delegate_tasks":
                delegation_response = await delegate_task(content)
                manager = delegation_response.get("manager")
                task = delegation_response.get("task")
                await channel.send(f"**Luna:** @*{manager}* {task}")              
                await channel.send(f"**{manager}:** Delegated {task}")
            await channel.send(f"**Luna:** All requests executed")
                
                
        return "I'm not sure how to handle that."
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return "Error processing your request. Please try again."

async def delegate_task(task):
    system_prompt = '''
                    You are gonna assign tasks to their respective managers.

                    Tasks:
                    - For the given input task, choose from one of the following managers:
                        - Research manager (Eric): Used for looking up knowledge from online sources.
                        - Communication manager (Grace): Used for accessing communication platforms and interacting with messages and inboxes.
                        - Project manager (Sam): Used for interacting with calendar and to-do related tasks.
                    - When defining the task avoid vague time descriptions like in a hour or next monday.
                    - Respond in the following json format:

                        <output_format>
                        [
                            {
                                "manager": "manager name e.g Eric",
                                "task": "task description"
                            }
                        ]
                    '''
    result = json_prompt(prompt=task, system_prompt=system_prompt)
    return result