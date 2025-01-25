# agents/managers/manager_config.py

from workflows.my_workflows.add_to_calendar import AddToCalendarWorkflow

def placeholder():
    pass

managers_config = {
    "Sam": {
        "name": "Sam",
        "role": "project manager",
        "workflows": [
            {
                "name": "add to calendar",
                "trigger": AddToCalendarWorkflow,  # reference the workflow class
                "description": "Adds an event to the calendar.",
                "params": {
                    "summary": "string",
                    "start_time": "string (RFC3339 format)",
                    "end_time": "string (RFC3339 format)",
                    "location": "string (optional)",
                    "description": "string (optional)"
                }
            }
        ]
    },
    "Grace": {
        "name": "Grace",
        "role": "communication manager",
        "workflows": [
            {
                "name": "workflow name",
                "trigger": placeholder,
                "description": "Short description of the purpose of the workflow.",
                "params": {}
            }
        ]
    },
    "Eric": {
        "name": "Eric",
        "role": "research manager",
        "workflows": [
            {
                "name": "workflow name",
                "trigger": placeholder,
                "description": "Short description of the purpose of the workflow.",
                "params": {}
            }
        ]
    },
}
