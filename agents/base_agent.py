from typing import List, Optional, Any

class BaseAgent:
    """
    A base agent that can handle:
      - A Model (e.g., your DeepSeekModel)
      - Memory (optional, for storing/retrieving data)
      - Tools (optional, for 3rd-party integrations)
    """
    def __init__(
        self,
        model: Optional[Any] = None,
        memory: Optional[Any] = None,
        tools: Optional[List[Any]] = None,
    ):
        """
        :param model:   An object or function capable of processing text (i.e., must have a .generate(str)->str method).
        :param memory:  An object to store and retrieve data (e.g., conversation history).
        :param tools:   A list of tool objects/functions the agent can call.
        """
        self.model = model
        self.memory = memory
        self.tools = tools or []

    def set_model(self, model: Any):
        """Set or replace the current model."""
        self.model = model

    def set_memory(self, memory: Any):
        """Set or replace the current memory backend."""
        self.memory = memory

    def add_tool(self, tool: Any):
        """Add a new tool to the agent's toolset."""
        self.tools.append(tool)

    def _retrieve_context(self, prompt: str) -> str:
        """Override with your own logic if you have memory."""
        if self.memory is None:
            return ""
        # E.g., if memory has a .retrieve() method
        return self.memory.retrieve(prompt)
    
    def _decide_tool_usage(self, prompt: str) -> Optional[Any]:
        """
        Decide if a tool is needed. This is a stub; your real logic might parse the prompt
        or use an LLM to decide which tool to call.
        """
        for tool in self.tools:
            if hasattr(tool, "TRIGGER_KEYWORD") and tool.TRIGGER_KEYWORD in prompt:
                return tool
        return None

    def run(self, prompt: str, prefix: str="", suffix: str="", no_prefix: bool=False) -> str:
        """
        Main entry point for the agent:
          1) Optionally retrieve context from memory
          2) Possibly decide to use a tool
          3) Process the prompt with the model
          4) Store output in memory if desired
          5) Return the final response
        """
        # (1) Retrieve context
        context = self._retrieve_context(prompt)

        # (2) Decide if a tool is needed
        chosen_tool = self._decide_tool_usage(prompt)
        if chosen_tool is not None:
            tool_output = chosen_tool.run(prompt)
            final_prompt = f"{context}\nTool Output: {tool_output}\nOriginal Prompt: {prompt}"
        else:
            final_prompt = f"{context}\n{prompt}"

        # (3) Generate response using the model (DeepSeekModel in your case)
        if self.model is not None and hasattr(self.model, "generate"):
            response = self.model.generate(text = final_prompt, prompt_type=self.model.prompt_type, prefix=prefix, suffix=suffix, no_prefix=no_prefix)
        else:
            response = f"No model is defined, but here's what we have:\n{final_prompt}"

        # (4) Optionally store output in memory
        if self.memory is not None and hasattr(self.memory, "store"):
            self.memory.store(prompt, response)

        # (5) Return the response
        return response

