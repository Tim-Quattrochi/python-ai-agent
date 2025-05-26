from src.config import Config
from src.llm_client import Message

# Mock LocalLLMClient for testing
class MockLocalLLMClient:
    def __init__(self, config):
        self.config = config
    
    def generate_response(self, messages, tools=None):
        return Message(role="assistant", content="Hello! I'm a mock local LLM response.")

# Test
config = Config()
config.llm_provider = "local"
client = MockLocalLLMClient(config)
messages = [Message(role="user", content="Hello!")]

response = client.generate_response(messages)
print(f"Mock response: {response.content}")
