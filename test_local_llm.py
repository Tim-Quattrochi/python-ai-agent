from src.config import Config

# Test config loading
config = Config()
config.llm_provider = "local"

print(f"Provider: {config.llm_provider}")
print(f"URL: {config.local_llm_url}")
print(f"Model: {config.current_model}")

# Test the LocalLLMClient directly
from src.llm_client import LocalLLMClient, Message

client = LocalLLMClient(config)
messages = [Message(role="user", content="Hello!")]

try:
    response = client.generate_response(messages)
    print(f"Success! Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
