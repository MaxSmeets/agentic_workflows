from workflows.base_workflow import Workflow
from modules.triggers.schedule import ScheduledTrigger
from modules.ai_modules.models.deepseek import prompt
import time

class PromptWorkflow(Workflow):
    def execute(self):
        """Override base execute method with your prompt logic"""
        print(f"Running workflow ID: {self.get_id()}")
        result = prompt("What's the capital city of France?")
        print("AI Response:", result)
        return result

# Instantiate the custom workflow
workflow = PromptWorkflow()

# Create and configure trigger
every_minute_trigger = ScheduledTrigger(
    workflow=workflow.execute,
    interval=1,
    interval_unit='minutes'
)
