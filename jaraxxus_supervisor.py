import time
import json
from core.app_config import settings  # CORRECT: Uses the central settings object
from tools import AVAILABLE_TOOLS      # CORRECT: Imports the dynamically loaded tools
from core.base_agent import BaseAgent  # CORRECT: Imports our agent blueprint
from threading import Thread

class JaraxxusSupervisor:
    def __init__(self, command_queue, update_queue):
        self.command_queue = command_queue
        self.update_queue = update_queue
        self.is_running = False  # Initialize the flag here
        self.agents = self._load_agents_from_config()

    def start(self):
        """Sets the running flag to True."""
        print("Supervisor starting...")
        self.is_running = True

    def stop(self):
        """Sets the running flag to False to gracefully stop the loop."""
        print("Supervisor stopping...")
        self.is_running = False

    def run_in_background(self):
        """The main loop for the supervisor, intended to be run in a separate thread."""
        self.start()  # Set the running flag to true when the loop starts
        while self.is_running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    print(f"Supervisor received command: {command}")

                    # A simple, hard-coded command handler
                    if command == "list_tools":
                        response = "--- Available Agents & Tools ---\n"
                        if not self.agents:
                            response += "No agents have been loaded."
                        else:
                            for agent_name, agent_instance in self.agents.items():
                                response += f"\n[Agent] {agent_name}\n"
                                tool_names = list(agent_instance.tools.keys())
                                if tool_names:
                                    response += "  Tools: " + ", ".join(tool_names) + "\n"
                                else:
                                    response += "  Tools: None\n"

                        # Send the formatted response back to the GUI
                        self.update_queue.put(response)

                    else:
                        # --- Pass the command to an agent ---
                        if not self.agents:
                            self.update_queue.put("No agents available to handle the command.")
                        else:
                            # For now, just pick the first agent in the list
                            # In the future, we could have a routing agent
                            agent_to_use = list(self.agents.values())[0]

                            # Run the agent's task logic in a separate thread so it doesn't block the supervisor
                            agent_thread = Thread(target=agent_to_use.run_task, args=(command,))
                            agent_thread.start()

                            self.update_queue.put(f"Task '{command}' dispatched to agent '{agent_to_use.name}'.")
                time.sleep(0.1)  # Prevents the loop from using 100% CPU

            except Exception as e:
                print(f"[SUPERVISOR_ERROR] {e}")

        print("Supervisor background loop has terminated.")

    def _load_agents_from_config(self):
        """Loads agent configurations and instantiates agent objects."""
        # For now, we assume the config file is in the root directory.
        config_path = 'jaraxxus_config.json'
        try:
            with open(config_path, 'r') as f:
                agent_config = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Configuration file not found at {config_path}")
            return {}

        loaded_agents = {}
        for agent_data in agent_config.get("agents", []):
            if agent_data.get("enabled", False):
                agent_name = agent_data["name"]
                agent_description = agent_data.get("description", "")
                agent_tools = {}

                for tool_name in agent_data.get("tools", []):
                    if tool_name in AVAILABLE_TOOLS:
                        # Pass the whole tool module to the agent
                        agent_tools[tool_name] = AVAILABLE_TOOLS[tool_name]
                    else:
                        print(f"Warning: Tool '{tool_name}' for agent '{agent_name}' not found.")

                # Create an instance of our BaseAgent class
                agent_instance = BaseAgent(
                    name=agent_name,
                    description=agent_description,
                    tools=agent_tools,
                    update_queue=self.update_queue # Pass the queue here
                )
                loaded_agents[agent_name] = agent_instance

        return loaded_agents
