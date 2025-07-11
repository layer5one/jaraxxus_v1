import json
import re
from typing import List, Tuple, Dict, Any, Optional
import config
import tools # Make sure your tools package is properly loaded

class JaraxxusAgent:
    def __init__(self):
        # Load tools (name -> function) and tool descriptions
        self.tools = tools.load_tools()
        # Conversation history (excluding system prompt)
        self.history: List[Dict[str, str]] = []
        # System prompt template for tool usage instructions
        self.system_prompt_template = """You are Jaraxxus, a powerful AI assistant with tool-using capabilities.
You have access to the following tools. You must use them to answer the user's request.

<tools>
{tool_list}
</tools>

When you need to use a tool, you MUST output a single JSON object in the following format. Do not output anything else.
{{
  "action": "<tool_name>",
  "action_input": {{ ... arguments ... }}
}}

The "action_input" must be a JSON object that strictly follows the schema provided for that tool.
Valid "action" values are: {tool_names_list}

When you have gathered all the information you need and are ready to provide the final response to the user, use the "Final Answer" action.
{{
  "action": "Final Answer",
  "action_input": "<your final answer as a complete, well-formatted string>"
}}

Begin now.
"""
        # ... (the rest of your __init__ method remains the same) ...
        self.allow_cloud = config.settings.get("allow_cloud", False)
        self.model_name = config.settings.get("default_model", "")
        self.use_openai = False
        openai_prefixes = ("gpt-3", "gpt-4", "openai")
        for prefix in openai_prefixes:
            if self.model_name.lower().startswith(prefix):
                self.use_openai = True
                break
        if self.use_openai:
            import os
            api_key = config.settings.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                openai.api_key = api_key

    # ... (reload_tools, set_model, reset_conversation methods are unchanged) ...
    def reload_tools(self) -> List[str]:
        """Reload the tools dynamically (for hot-swapping). Returns list of tool names."""
        self.tools = tools.load_tools()
        # Add new tools to config.allowed_tools as enabled by default
        for mod_name in self.tools:
             if mod_name not in config.settings.get("allowed_tools", {}):
                config.settings.setdefault("allowed_tools", {})[mod_name] = True
        return list(self.tools.keys())

    def set_model(self, model_name: str):
        # ... (no changes needed)
        pass

    def reset_conversation(self):
        # ... (no changes needed)
        pass


    def _build_system_prompt(self) -> str:
        """
        Re-build the system prompt every time to provide an up-to-date
        list of tools and their schemas.
        """
        enabled_tools = []
        enabled_names = []

        for name, fn in self.tools.items():
            if not config.is_tool_enabled(name):
                continue
            
            # Get the description and the new schema from the function attributes
            desc = getattr(fn, "description", "No description available.")
            schema = getattr(fn, "args_schema", "No arguments.")
            
            # Format a clear "contract" for each tool
            tool_contract = (
                f"Tool: {name}\n"
                f"  Description: {desc}\n"
                f"  Argument Schema: {schema}"
            )
            enabled_tools.append(tool_contract)
            enabled_names.append(f'"{name}"')

        if not enabled_tools:
            tool_block = "No tools are currently available."
            tool_name_block = '"Final Answer"'
        else:
            tool_block = "\n\n".join(enabled_tools)
            tool_name_block = ", ".join(enabled_names + ['"Final Answer"'])

        return self.system_prompt_template.format(
            tool_list=tool_block,
            tool_names_list=tool_name_block
        )

    # ... (_call_model and _parse_action_json are unchanged) ...
    def _call_model(self, messages: List[Dict[str, str]]) -> str:
        # ... (no changes needed)
        pass

    def _parse_action_json(self, text: str) -> Optional[Dict[str, Any]]:
        # ... (no changes needed)
        pass

    def process(self, user_input: str) -> Tuple[str, List[str]]:
        """Process a user message through the agent, returning the assistant's answer and a list of log entries."""
        logs: List[str] = []
        self.history.append({"role": "user", "content": user_input})
        system_prompt = self._build_system_prompt()
        work_messages = [{"role": "system", "content": system_prompt}] + self.history.copy()
        
        assistant_reply = ""
        max_steps = 10 # Safety break
        
        for step in range(max_steps):
            try:
                model_output = self._call_model(work_messages)
            except Exception as e:
                err_msg = f"[ERROR] Model call failed: {e}"
                logs.append(err_msg)
                self.history.pop()
                return "(Error: LLM failure)", logs

            action_data = self._parse_action_json(model_output)
            
            if action_data is None:
                assistant_reply = model_output.strip()
                logs.append("LLM response (no action): " + assistant_reply[:100])
                break # Treat as final answer

            action = str(action_data.get("action", ""))
            action_input = action_data.get("action_input", "")
            
            # NEW: Add the model's thought process to the conversation history
            # This helps it remember what it just did.
            work_messages.append({"role": "assistant", "content": json.dumps(action_data, indent=2)})
            logs.append(f"LLM Action: {json.dumps(action_data)}")


            if action.lower() == "final answer":
                assistant_reply = str(action_input)
                logs.append("Final Answer received.")
                break

            if tool_name not in self.tools or not config.is_tool_enabled(tool_name):
                obs_text = f"Error: Tool '{tool_name}' is not available or is disabled."
            else:
                tool_func = self.tools[tool_name]
                try:
                    # The tool's run function will now handle the dict or string
                    result = tool_func(action_input)
                    obs_text = str(result)
                except Exception as e:
                    # Catch errors from within the tool itself
                    obs_text = f"Error executing tool '{tool_name}': {e}"
            
            # Truncate long observations to keep the context window clean
            if len(obs_text) > 2000:
                obs_text = obs_text[:2000] + "... [truncated]"
            
            logs.append("Observation: " + obs_text)
            # Add the observation to the conversation for the LLM's next step
            work_messages.append({"role": "system", "content": "Observation: " + obs_text})
            continue
        
        else: # Loop finished without a "Final Answer"
            assistant_reply = "(No final answer after max steps)"
            logs.append("Stopped after max steps.")

        assistant_reply = assistant_reply.strip()
        if assistant_reply:
            self.history.append({"role": "assistant", "content": assistant_reply})
            
        return assistant_reply, logs