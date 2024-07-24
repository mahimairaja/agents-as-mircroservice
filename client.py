import time
from llama_agents import LlamaAgentsClient, AsyncLlamaAgentsClient

client = LlamaAgentsClient("http://0.0.0.0:8001")

def poll_result(query: str):
    task_id = client.create_task(query)
    found = False
    while not found:
      try:
        result = client.get_task_result(task_id=task_id)
        found = True
      except:
        time.sleep(1)
        continue
    return result

result = poll_result("What is the secret fact?")
print(result)