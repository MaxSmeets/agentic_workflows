# workflows/my_workflows/test_workflow.py

from workflows.base_workflow import Workflow
from modules.app_actions.discord.executive_director_bot import bot
import os

class OnDiscordMessageWorkflow(Workflow):
    def execute(self):
        TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        bot.run(TOKEN)

