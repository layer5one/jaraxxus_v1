# jaraxxus_v2-gmni/core/llm_clients/memos_client.py

from memos.mem_os.main import MOS
from memos.configs.mem_os import MOSConfig
from memos.configs.llm import LLMConfigFactory
from memos.configs.embedder import EmbedderConfigFactory
from typing import List, Dict, Any

class MemOSClient:
    """
    A client to interact with the MemTensor/MemoryOS library, providing
    a persistent memory store for agents.
    """
    def __init__(self, user_id: str = "jaraxxus_default_user"):
        """
        Initializes the MemoryOS client.
        """
        print(f"Initializing MemoryOS for user: {user_id}...")

        # --- THE LITERAL INTERPRETATION OF THE ERROR MESSAGE ---
        # The 'config' field is a simple string: the model's name.
        llm_params = {
            "provider": "huggingface",
            "config": "google/flan-t5-small"  # Just the string
        }
        embedding_params = {
            "provider": "sentence_transformer",
            "config": "sentence-transformers/all-MiniLM-L6-v2" # Just the string
        }
        # --- END FIX ---

        llm_conf_factory = LLMConfigFactory(backend=llm_params)
        embedding_conf_factory = EmbedderConfigFactory(backend=embedding_params)

        top_level_config = MOSConfig(llm_config=llm_conf_factory, embedding_config=embedding_conf_factory)

        self.mos = MOS(config=top_level_config)
        self.user_id = user_id
        self.mos.create_user(user_id=self.user_id)
        print("MemoryOS Initialized and user created.")

    def save_memory(self, content: List[Dict[str, str]]) -> Dict[str, Any]:
        print(f"CLIENT: Saving memory: {content}")
        result = self.mos.add(messages=content, user_id=self.user_id)
        return result

    def recall_memory(self, query: str) -> Dict[str, Any]:
        print(f"CLIENT: Recalling memory for query: '{query}'")
        results = self.mos.search(query=query, user_id=self.user_id)
        print(f"CLIENT: Found memories.")
        return results

if __name__ == '__main__':
    print("--- Running MemOSClient self-test ---")
    client = MemOSClient(user_id="self_test_user_13")

    client.save_memory(content=[{"role": "user", "content": "The company I work for is being acquired by a soulless conglomerate."}])
    client.save_memory(content=[{"role": "user", "content": "My apartment is on the third story."}])
    client.save_memory(content=[{"role": "user", "content": "The Jaraxxus project's goal is to integrate local LLMs and persistent memory."}])

    print("\n--- Recalling memory about 'my job' ---")
    recalled_memories = client.recall_memory(query="What is happening at my company?")
    print("Recall Results:", recalled_memories.get('text_mem'))

    print("\n--- Recalling memory about 'the project' ---")
    recalled_memories = client.recall_memory(query="What is the goal of this project?")
    print("Recall Results:", recalled_memories.get('text_mem'))

    print("\n--- Recalling memory about my apartment ---")
    recalled_memories = client.recall_memory(query="Where do I live?")
    print("Recall Results:", recalled_memories.get('text_mem'))

    print("\n--- Self-test complete ---")
