# core/base_agent.py
import os
import json
import google.generativeai as genai

# Configure API key
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except AttributeError:
    print("ERROR: The GOOGLE_API_KEY environment variable is not set.")
    exit()

class BaseAgent:
    def __init__(self, name, description, tools, update_queue):
        self.name = name
        self.description = description
        self.tools = tools
        self.update_queue = update_queue
        self.status = "idle"
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print(f"Agent '{self.name}' created with tools: {list(self.tools.keys())}")

    def _build_prompt(self, task, history):
        """Builds the prompt for the LLM, including the task, history, and tools."""
        tool_details = []
        for tool_name, tool_module in self.tools.items():
            description = getattr(tool_module, 'DESCRIPTION', 'No description.')
            args_schema = getattr(tool_module, 'ARGS_SCHEMA', '{}')
            tool_details.append(f"- Tool: `{tool_name}`\n  Description: {description}\n  Arguments (JSON): {args_schema}")
        tools_string = "\n".join(tool_details)

        prompt = f"""
        You are an autonomous AI agent named {self.name}. Your goal is to accomplish the user's task by breaking it down into steps and using the available tools.

        Available Tools:
        {tools_string}

        Conversation History (User's Task and results from previous tool executions):
        {history}

        Based on the history, decide on the next step. You have two choices:
        1.  Use a tool: Respond with a single JSON object:
            {{"thought": "<reasoning>", "tool_to_use": "<tool_name>", "tool_input": {{<json_args>}}}}
        2.  Finish the task: If you have the final answer for the user, respond with:
            {{"thought": "<summary of what was accomplished>", "final_answer": "<your complete and final answer to the user>"}}
        """
        return prompt

    def run_task(self, task):
        self.status = "running"
        self.update_queue.put(f"[{self.name}] Starting new task: {task}")

        conversation_history = f"USER_TASK: {task}"

        while True: # The main reasoning loop
            prompt = self._build_prompt(task, conversation_history)

            try:
                llm_response_text = self.model.generate_content(prompt).text
                self.update_queue.put(f"[{self.name}] Reasoning:\n{llm_response_text}")

                if llm_response_text.strip().startswith("```json"):
                    cleaned_json_str = llm_response_text.strip()[7:-3].strip()
                else:
                    cleaned_json_str = llm_response_text.strip()

                parsed_response = json.loads(cleaned_json_str)

                if "final_answer" in parsed_response:
                    final_answer = parsed_response["final_answer"]
                    self.update_queue.put(f"[{self.name}] Task Complete. Final Answer:\n{final_answer}")
                    break # Exit the loop

                tool_name = parsed_response.get("tool_to_use")
                tool_input = parsed_response.get("tool_input", {})

                if tool_name and tool_name in self.tools:
                    self.update_queue.put(f"[{self.name}] Executing tool: '{tool_name}'")
                    tool_module = self.tools[tool_name]
                    result = tool_module.run(tool_input)

                    # Add the result to the conversation history for the next loop iteration
                    conversation_history += f"\nTOOL_RESULT for {tool_name}: {result}"
                    self.update_queue.put(f"[{self.name}] Tool Result:\n{result}")
                else:
                    self.update_queue.put(f"[{self.name}] LLM chose an invalid tool. Ending task.")
                    break # Exit the loop

            except Exception as e:
                self.update_queue.put(f"[{self.name}] An error occurred: {e}")
                break # Exit on any error

        self.status = "idle"
