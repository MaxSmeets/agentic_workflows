# workflows/my_workflows/test_workflow.py

from workflows.base_workflow import Workflow
from modules.triggers.schedule import ScheduledTrigger
from modules.ai_modules.models.deepseek import prompt
import os

class PromptWorkflow(Workflow):
    def execute(self):
        # Your prompt logic
        print(f"Running workflow ID: {self.get_id()}")
        result = prompt("What's the capital city of France?")
        print("AI Response:", result)

        return result

# Instantiate the custom workflow
workflow = PromptWorkflow()

# Create and configure trigger
trigger = ScheduledTrigger(
    workflow=workflow.execute,
    interval=1,
    interval_unit='minutes'
)
