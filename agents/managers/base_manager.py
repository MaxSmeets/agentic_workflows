from typing import Any, Optional
import json
from agents.managers.manager_config import managers_config

class BaseManager:
    """
    The base manager can setup a model integration
    """
    def __init__(
        self,
        model: Optional[Any] = None,
        name: str = "",
        role: str = "",

    ):
        """
        :param model:   An object or function capable of processing text (i.e., must have a .generate(str)->str method).
        :param memory:  An object to store and retrieve data (e.g., conversation history).
        :param tools:   A list of tool objects/functions the agent can call.
        """
        self.model = model
        self.name = name
        self.role = role
    
    def run(self, text: str, prompt_type: str = 'json'):
        """
        Processes the response and passes parameters to the workflow.
        """
        if self.model is not None and hasattr(self.model, "generate"):
            raw_response = self.model.generate(text)
            print("Raw response:", raw_response)

            # Clean response if wrapped in ```json
            if raw_response.startswith("```json"):
                raw_response = raw_response.strip().replace("```json\n", "").replace("```", "")

            try:
                parsed_response = json.loads(raw_response)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                return "Error: Unable to process the response."

            # Extract workflow and params
            workflow_name = parsed_response.get("workflow")
            params = parsed_response.get("params", {})

            manager_data = managers_config.get(self.name, {})
            workflow_info = next(
                (w for w in manager_data.get("workflows", []) if w["name"] == workflow_name),
                None
            )

            if not workflow_info:
                return f"No workflow named '{workflow_name}' found for {self.name}."

            workflow_class = workflow_info["trigger"]
            workflow_instance = workflow_class()

            # Map params to workflow, include defaults for missing optional parameters
            params_to_pass = {}
            for param_name, param_type in workflow_info.get("params", {}).items():
                params_to_pass[param_name] = params.get(param_name, "")

            try:
                result = workflow_instance.execute(**params_to_pass)
                return result
            except Exception as e:
                print(f"Error executing workflow '{workflow_name}': {e}")
                return f"Failed to execute the workflow: {str(e)}"
        else:
            return "No model is defined."


