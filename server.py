from dotenv import load_dotenv
from llama_agents import (AgentService, AgentOrchestrator, ControlPlaneServer, SimpleMessageQueue)
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
load_dotenv()

# create an agent
def get_the_secret_fact() -> str:
    """Returns the secret fact."""
    return "The secret fact is: A baby llama is called a 'Cria'."


tool = FunctionTool.from_defaults(fn=get_the_secret_fact)

agent1 = ReActAgent.from_tools([tool], llm=OpenAI())
agent2 = ReActAgent.from_tools([], llm=OpenAI())

# create our multi-agent framework components
message_queue = SimpleMessageQueue(port=8000)
control_plane = ControlPlaneServer(
    message_queue=message_queue,
    host="0.0.0.0",
    orchestrator=AgentOrchestrator(llm=OpenAI(model="gpt-4-turbo")),
    port=8001,
)
agent_server_1 = AgentService(
    agent=agent1,
    message_queue=message_queue,
    description="Useful for getting the secret fact.",
    service_name="secret_fact_agent",
    host="0.0.0.0",
    port=8002,
)
agent_server_2 = AgentService(
    agent=agent2,
    message_queue=message_queue,
    description="Useful for getting random dumb facts.",
    service_name="dumb_fact_agent",
    host="0.0.0.0",
    port=8003,
)

from llama_agents import ServerLauncher, CallableMessageConsumer


# Additional human consumer
def handle_result(message) -> None:
    print(f"Got result:", message.data)


human_consumer = CallableMessageConsumer(
    handler=handle_result, message_type="human",
)

# Define Launcher
launcher = ServerLauncher(
    [agent_server_1, agent_server_2],
    control_plane,
    message_queue,
    additional_consumers=[human_consumer],
)

# Launch it!
launcher.launch_servers()
